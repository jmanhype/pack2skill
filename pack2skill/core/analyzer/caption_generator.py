"""Generate captions for video frames using vision-language models."""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from PIL import Image

try:
    from transformers import pipeline, AutoProcessor, AutoModelForVision2Seq
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("transformers not available. Caption generation will be disabled.")

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    logging.warning("pytesseract not available. OCR will be disabled.")

logger = logging.getLogger(__name__)


class CaptionGenerator:
    """Generates captions for video frames using vision-language models.

    Supports multiple captioning models and optional OCR for UI text extraction.
    """

    def __init__(
        self,
        model_name: str = "Salesforce/blip-image-captioning-large",
        use_ocr: bool = True,
        device: Optional[str] = None,
    ):
        """Initialize caption generator.

        Args:
            model_name: HuggingFace model name for image captioning
            use_ocr: Whether to use OCR for text extraction
            device: Device to run model on ("cuda", "cpu", or None for auto)

        Raises:
            RuntimeError: If required dependencies are not available
        """
        if not TRANSFORMERS_AVAILABLE:
            raise RuntimeError(
                "transformers not installed. Install with: "
                "pip install transformers torch pillow"
            )

        self.model_name = model_name
        self.use_ocr = use_ocr and PYTESSERACT_AVAILABLE

        # Determine device
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device

        logger.info(f"Loading caption model: {model_name} on {device}")

        # Initialize captioning model
        try:
            self.captioner = pipeline(
                "image-to-text",
                model=model_name,
                device=0 if device == "cuda" else -1,
            )
            logger.info("Caption model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load caption model: {e}")
            raise

        if not self.use_ocr:
            logger.warning("OCR disabled - UI text will not be extracted")

    def _extract_text_ocr(self, image_path: Path) -> str:
        """Extract text from image using OCR.

        Args:
            image_path: Path to image file

        Returns:
            Extracted text (empty string if no text found)
        """
        if not self.use_ocr:
            return ""

        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.warning(f"OCR failed for {image_path}: {e}")
            return ""

    def generate_caption(
        self,
        image_path: Path,
        max_new_tokens: int = 50,
    ) -> Dict[str, Any]:
        """Generate caption for a single image.

        Args:
            image_path: Path to image file
            max_new_tokens: Maximum tokens to generate

        Returns:
            Dictionary with caption and metadata
        """
        image_path = Path(image_path)

        # Generate caption
        try:
            result = self.captioner(
                str(image_path),
                max_new_tokens=max_new_tokens,
            )
            caption = result[0]["generated_text"]
        except Exception as e:
            logger.error(f"Caption generation failed for {image_path}: {e}")
            caption = ""

        # Extract OCR text
        ocr_text = self._extract_text_ocr(image_path) if self.use_ocr else ""

        return {
            "image_path": str(image_path),
            "caption": caption,
            "ocr_text": ocr_text,
            "model": self.model_name,
        }

    def generate_captions_batch(
        self,
        image_paths: List[Path],
        max_new_tokens: int = 50,
        batch_size: int = 4,
    ) -> List[Dict[str, Any]]:
        """Generate captions for multiple images in batches.

        Args:
            image_paths: List of image paths
            max_new_tokens: Maximum tokens to generate per caption
            batch_size: Number of images to process at once

        Returns:
            List of caption dictionaries
        """
        results = []

        for i in range(0, len(image_paths), batch_size):
            batch = image_paths[i:i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1}/{(len(image_paths) + batch_size - 1) // batch_size}")

            for image_path in batch:
                result = self.generate_caption(image_path, max_new_tokens)
                results.append(result)

        return results

    def enhance_caption_with_context(
        self,
        caption: str,
        ocr_text: str,
        previous_caption: Optional[str] = None,
    ) -> str:
        """Enhance caption with OCR text and context.

        Args:
            caption: Base caption from vision model
            ocr_text: Text extracted via OCR
            previous_caption: Caption from previous frame (for context)

        Returns:
            Enhanced caption text
        """
        # Start with base caption
        enhanced = caption

        # Add important UI text from OCR
        if ocr_text:
            # Extract keywords (buttons, menu items, etc.)
            # Simple heuristic: look for short text (likely UI elements)
            lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
            ui_keywords = [
                line for line in lines
                if 2 <= len(line.split()) <= 5 and line[0].isupper()
            ]

            if ui_keywords:
                # Add the most relevant UI text
                ui_text = ui_keywords[0] if ui_keywords else ""
                if ui_text and ui_text.lower() not in enhanced.lower():
                    enhanced = f"{enhanced.rstrip('.')} with '{ui_text}'"

        # Add transition context from previous frame
        if previous_caption:
            # Check if there's a significant change
            if caption.lower() != previous_caption.lower():
                # This is a new action/scene
                pass  # Could add transition words like "Then,..."

        return enhanced.strip()


class BatchCaptionGenerator:
    """Optimized batch caption generator for processing many frames efficiently."""

    def __init__(
        self,
        model_name: str = "Salesforce/blip-image-captioning-large",
        use_ocr: bool = True,
        device: Optional[str] = None,
        batch_size: int = 8,
    ):
        """Initialize batch caption generator.

        Args:
            model_name: HuggingFace model name
            use_ocr: Whether to use OCR
            device: Device to run on
            batch_size: Default batch size
        """
        self.generator = CaptionGenerator(
            model_name=model_name,
            use_ocr=use_ocr,
            device=device,
        )
        self.batch_size = batch_size

    def process_frames(
        self,
        frames_data: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Process frame data and add captions.

        Args:
            frames_data: List of frame metadata dicts (must have "path" key)

        Returns:
            Updated frames_data with captions added
        """
        image_paths = [Path(frame["path"]) for frame in frames_data]

        logger.info(f"Generating captions for {len(image_paths)} frames...")

        captions = self.generator.generate_captions_batch(
            image_paths,
            batch_size=self.batch_size,
        )

        # Merge captions into frame data
        for frame, caption_data in zip(frames_data, captions):
            frame.update({
                "caption": caption_data["caption"],
                "ocr_text": caption_data["ocr_text"],
            })

        return frames_data
