"""Complete frame analysis pipeline combining extraction and captioning."""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from pack2skill.core.analyzer.frame_extractor import FrameExtractor
from pack2skill.core.analyzer.caption_generator import CaptionGenerator

logger = logging.getLogger(__name__)


class FrameAnalyzer:
    """Complete pipeline for analyzing video frames.

    Combines frame extraction, captioning, and event correlation.
    """

    def __init__(
        self,
        caption_model: str = "Salesforce/blip-image-captioning-large",
        scene_threshold: float = 0.3,
        min_interval: float = 1.0,
        use_ocr: bool = True,
        device: Optional[str] = None,
    ):
        """Initialize frame analyzer.

        Args:
            caption_model: Model name for image captioning
            scene_threshold: Threshold for scene change detection
            min_interval: Minimum time between frames in seconds
            use_ocr: Whether to use OCR for text extraction
            device: Device for model inference
        """
        self.extractor = FrameExtractor(
            scene_threshold=scene_threshold,
            min_interval=min_interval,
        )

        self.caption_generator = CaptionGenerator(
            model_name=caption_model,
            use_ocr=use_ocr,
            device=device,
        )

    def analyze_video(
        self,
        video_path: Path,
        output_dir: Path,
        events: Optional[List[Dict[str, Any]]] = None,
        method: str = "scene_change",
    ) -> List[Dict[str, Any]]:
        """Analyze video and generate annotated steps.

        Args:
            video_path: Path to video file
            output_dir: Directory to save frames and results
            events: Optional list of user interaction events
            method: Frame extraction method

        Returns:
            List of analyzed steps with captions and events
        """
        video_path = Path(video_path)
        output_dir = Path(output_dir)

        # Create frames directory
        frames_dir = output_dir / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Analyzing video: {video_path}")

        # Extract frames
        logger.info("Extracting key frames...")
        frames_data = self.extractor.extract_frames(
            video_path=video_path,
            output_dir=frames_dir,
            method=method,
        )

        if not frames_data:
            logger.warning("No frames extracted")
            return []

        # Generate captions
        logger.info("Generating captions...")
        for i, frame in enumerate(frames_data):
            caption_data = self.caption_generator.generate_caption(
                image_path=Path(frame["path"])
            )
            frame.update({
                "caption": caption_data["caption"],
                "ocr_text": caption_data["ocr_text"],
            })

            # Enhance caption with previous context
            if i > 0:
                prev_caption = frames_data[i - 1]["caption"]
                frame["caption"] = self.caption_generator.enhance_caption_with_context(
                    caption=frame["caption"],
                    ocr_text=frame["ocr_text"],
                    previous_caption=prev_caption,
                )

            logger.info(
                f"Frame {i + 1}/{len(frames_data)} @ {frame['timestamp']}s: "
                f"{frame['caption']}"
            )

        # Merge with events if provided
        steps = self._merge_frames_and_events(frames_data, events)

        # Save results
        results_file = output_dir / "analysis.json"
        with open(results_file, 'w') as f:
            json.dump({
                "video_path": str(video_path),
                "frames_count": len(frames_data),
                "events_count": len(events) if events else 0,
                "steps_count": len(steps),
                "steps": steps,
            }, f, indent=2)

        logger.info(f"Analysis complete: {len(steps)} steps generated")
        logger.info(f"Results saved to: {results_file}")

        return steps

    def _merge_frames_and_events(
        self,
        frames_data: List[Dict[str, Any]],
        events: Optional[List[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        """Merge frame captions with user interaction events.

        Args:
            frames_data: List of frame data with captions
            events: List of user interaction events

        Returns:
            List of merged steps
        """
        if not events:
            # No events - just use captions as steps
            return [
                {
                    "timestamp": frame["timestamp"],
                    "text": frame["caption"],
                    "frame_index": frame["index"],
                    "frame_path": frame["path"],
                    "ocr_text": frame.get("ocr_text", ""),
                }
                for frame in frames_data
            ]

        # Merge frames and events by timestamp
        steps = []
        event_idx = 0
        frame_idx = 0

        while frame_idx < len(frames_data) or event_idx < len(events):
            frame = frames_data[frame_idx] if frame_idx < len(frames_data) else None
            event = events[event_idx] if event_idx < len(events) else None

            if frame is None:
                # Only events left
                steps.append({
                    "timestamp": event["t"],
                    "text": self._format_event(event),
                    "event": event,
                })
                event_idx += 1

            elif event is None:
                # Only frames left
                steps.append({
                    "timestamp": frame["timestamp"],
                    "text": frame["caption"],
                    "frame_index": frame["index"],
                    "frame_path": frame["path"],
                    "ocr_text": frame.get("ocr_text", ""),
                })
                frame_idx += 1

            else:
                # Both available - merge if close in time
                time_diff = abs(frame["timestamp"] - event["t"])

                if time_diff < 0.5:  # Within 0.5 seconds
                    # Merge frame and event
                    text = self._combine_frame_and_event(frame, event)
                    steps.append({
                        "timestamp": event["t"],
                        "text": text,
                        "frame_index": frame["index"],
                        "frame_path": frame["path"],
                        "ocr_text": frame.get("ocr_text", ""),
                        "event": event,
                    })
                    frame_idx += 1
                    event_idx += 1

                elif frame["timestamp"] < event["t"]:
                    # Frame comes first
                    steps.append({
                        "timestamp": frame["timestamp"],
                        "text": frame["caption"],
                        "frame_index": frame["index"],
                        "frame_path": frame["path"],
                        "ocr_text": frame.get("ocr_text", ""),
                    })
                    frame_idx += 1

                else:
                    # Event comes first
                    steps.append({
                        "timestamp": event["t"],
                        "text": self._format_event(event),
                        "event": event,
                    })
                    event_idx += 1

        return steps

    def _format_event(self, event: Dict[str, Any]) -> str:
        """Format an event as readable text.

        Args:
            event: Event dictionary

        Returns:
            Formatted text description
        """
        if event["type"] == "click":
            return f"Click at position ({event['x']}, {event['y']})"
        elif event["type"] == "keystroke":
            key = event["key"]
            # Clean up key name
            if len(key) == 1:
                return f"Type '{key}'"
            else:
                return f"Press {key}"
        else:
            return f"Unknown event: {event['type']}"

    def _combine_frame_and_event(
        self,
        frame: Dict[str, Any],
        event: Dict[str, Any],
    ) -> str:
        """Combine frame caption with event information.

        Args:
            frame: Frame data with caption
            event: Event data

        Returns:
            Combined description text
        """
        caption = frame["caption"]
        ocr_text = frame.get("ocr_text", "")

        if event["type"] == "click":
            # Try to identify what was clicked using OCR
            if ocr_text:
                # Simple heuristic: use first line of OCR as button/element name
                lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]
                if lines:
                    element = lines[0]
                    return f"Click '{element}' button"

            return f"Click on screen element ({caption.lower()})"

        elif event["type"] == "keystroke":
            key = event["key"]
            return f"Press {key} ({caption.lower()})"

        return caption
