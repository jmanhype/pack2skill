"""Confidence scoring for generated workflow steps."""

import logging
from typing import List, Dict, Any, Optional
import re

logger = logging.getLogger(__name__)


class ConfidenceScorer:
    """Calculates confidence scores for workflow steps.

    Combines multiple signals:
    - Visual certainty (caption quality)
    - Event alignment (caption matches recorded events)
    - Temporal consistency (reasonable timing between steps)
    - OCR validation (UI text found in caption)
    """

    def __init__(
        self,
        visual_weight: float = 0.4,
        event_weight: float = 0.3,
        temporal_weight: float = 0.3,
    ):
        """Initialize confidence scorer.

        Args:
            visual_weight: Weight for visual certainty (default: 0.4)
            event_weight: Weight for event alignment (default: 0.3)
            temporal_weight: Weight for temporal consistency (default: 0.3)
        """
        # Weights should sum to 1.0
        total = visual_weight + event_weight + temporal_weight
        self.visual_weight = visual_weight / total
        self.event_weight = event_weight / total
        self.temporal_weight = temporal_weight / total

    def calculate_visual_confidence(
        self,
        step: Dict[str, Any],
    ) -> float:
        """Calculate visual confidence for a step.

        Args:
            step: Step dictionary with caption and OCR data

        Returns:
            Confidence score (0-1)
        """
        score = 0.5  # Base score

        caption = step.get("caption", "")
        ocr_text = step.get("ocr_text", "")

        if not caption:
            return 0.0

        # Check caption quality
        # Longer captions are generally more descriptive
        if len(caption) > 20:
            score += 0.2
        elif len(caption) < 10:
            score -= 0.2

        # Check for generic/uncertain language
        uncertain_phrases = ["appears", "seems", "might", "possibly", "unclear"]
        if any(phrase in caption.lower() for phrase in uncertain_phrases):
            score -= 0.15

        # OCR validation: check if caption mentions UI elements found in OCR
        if ocr_text:
            # Extract likely UI keywords from OCR (short phrases, proper case)
            ocr_keywords = self._extract_ui_keywords(ocr_text)

            # Check if any OCR keywords appear in caption
            matches = sum(1 for kw in ocr_keywords if kw.lower() in caption.lower())

            if matches > 0:
                score += 0.2 * min(matches, 2)  # Cap at 2 matches
            else:
                # Caption doesn't mention any UI text - might be too generic
                score -= 0.1

        # Clamp to 0-1
        return max(0.0, min(1.0, score))

    def calculate_event_confidence(
        self,
        step: Dict[str, Any],
    ) -> float:
        """Calculate event alignment confidence.

        Args:
            step: Step dictionary with optional event data

        Returns:
            Confidence score (0-1)
        """
        if "event" not in step:
            # No event to validate against - neutral score
            return 0.5

        event = step["event"]
        caption = step.get("caption", "")

        # Check if event type matches caption
        event_type = event.get("type", "")

        if event_type == "click":
            # Caption should mention clicking, selecting, or opening
            click_keywords = ["click", "select", "open", "choose", "press", "tap"]
            if any(kw in caption.lower() for kw in click_keywords):
                return 0.9
            else:
                return 0.4  # Event doesn't match caption

        elif event_type == "keystroke":
            key = event.get("key", "")
            # Check if caption mentions the key or typing
            if key.lower() in caption.lower():
                return 0.95
            elif any(kw in caption.lower() for kw in ["type", "enter", "press"]):
                return 0.7
            else:
                return 0.4

        return 0.5  # Unknown event type

    def calculate_temporal_confidence(
        self,
        step: Dict[str, Any],
        previous_step: Optional[Dict[str, Any]] = None,
    ) -> float:
        """Calculate temporal consistency confidence.

        Args:
            step: Current step dictionary
            previous_step: Previous step dictionary (if any)

        Returns:
            Confidence score (0-1)
        """
        if previous_step is None:
            return 1.0  # First step - no temporal constraints

        current_time = step.get("timestamp", 0)
        prev_time = previous_step.get("timestamp", 0)

        time_diff = current_time - prev_time

        # Reasonable time differences
        if 0.5 <= time_diff <= 5.0:
            # Normal pace
            return 1.0
        elif 0.2 <= time_diff < 0.5:
            # Fast but plausible
            return 0.8
        elif 5.0 < time_diff <= 10.0:
            # Slow but plausible
            return 0.7
        elif time_diff > 10.0:
            # Very long gap - might indicate pause or missed steps
            return 0.5
        else:
            # Negative or too small - timing issue
            return 0.3

    def score_step(
        self,
        step: Dict[str, Any],
        previous_step: Optional[Dict[str, Any]] = None,
    ) -> float:
        """Calculate overall confidence score for a step.

        Args:
            step: Step dictionary
            previous_step: Previous step (for temporal analysis)

        Returns:
            Overall confidence score (0-1)
        """
        visual_conf = self.calculate_visual_confidence(step)
        event_conf = self.calculate_event_confidence(step)
        temporal_conf = self.calculate_temporal_confidence(step, previous_step)

        overall = (
            self.visual_weight * visual_conf +
            self.event_weight * event_conf +
            self.temporal_weight * temporal_conf
        )

        logger.debug(
            f"Step @ {step.get('timestamp', 0):.2f}s: "
            f"visual={visual_conf:.2f}, event={event_conf:.2f}, "
            f"temporal={temporal_conf:.2f} => overall={overall:.2f}"
        )

        return overall

    def score_steps(
        self,
        steps: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Score all steps in a workflow.

        Args:
            steps: List of step dictionaries

        Returns:
            Updated steps with confidence scores
        """
        for i, step in enumerate(steps):
            prev_step = steps[i - 1] if i > 0 else None
            step["confidence"] = round(self.score_step(step, prev_step), 2)

        return steps

    def identify_low_confidence_steps(
        self,
        steps: List[Dict[str, Any]],
        threshold: float = 0.6,
    ) -> List[int]:
        """Identify steps with low confidence scores.

        Args:
            steps: List of steps with confidence scores
            threshold: Confidence threshold (default: 0.6)

        Returns:
            List of step indices with low confidence
        """
        return [
            i for i, step in enumerate(steps)
            if step.get("confidence", 1.0) < threshold
        ]

    def _extract_ui_keywords(self, ocr_text: str) -> List[str]:
        """Extract likely UI keywords from OCR text.

        Args:
            ocr_text: Raw OCR text

        Returns:
            List of UI keywords
        """
        if not ocr_text:
            return []

        # Split into lines and filter
        lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]

        keywords = []
        for line in lines:
            # UI elements are typically short and start with capital
            words = line.split()

            if 1 <= len(words) <= 4 and line[0].isupper():
                # Remove common noise words
                noise = ["the", "and", "or", "a", "an", "in", "on", "at", "to"]
                clean_words = [w for w in words if w.lower() not in noise]

                if clean_words:
                    keywords.append(' '.join(clean_words))

        return keywords[:10]  # Limit to top 10

    def generate_confidence_report(
        self,
        steps: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Generate a comprehensive confidence report.

        Args:
            steps: List of steps with confidence scores

        Returns:
            Report dictionary with statistics and recommendations
        """
        if not steps:
            return {
                "total_steps": 0,
                "average_confidence": 0.0,
                "low_confidence_count": 0,
            }

        scores = [step.get("confidence", 0.0) for step in steps]

        return {
            "total_steps": len(steps),
            "average_confidence": round(sum(scores) / len(scores), 2),
            "min_confidence": round(min(scores), 2),
            "max_confidence": round(max(scores), 2),
            "low_confidence_count": sum(1 for s in scores if s < 0.6),
            "low_confidence_indices": self.identify_low_confidence_steps(steps),
            "recommendation": self._get_recommendation(scores),
        }

    def _get_recommendation(self, scores: List[float]) -> str:
        """Get recommendation based on confidence scores.

        Args:
            scores: List of confidence scores

        Returns:
            Recommendation string
        """
        avg = sum(scores) / len(scores) if scores else 0.0

        if avg >= 0.8:
            return "High quality - skill is ready to use"
        elif avg >= 0.6:
            return "Good quality - review low confidence steps"
        elif avg >= 0.4:
            return "Moderate quality - manual review recommended"
        else:
            return "Low quality - significant manual editing needed"
