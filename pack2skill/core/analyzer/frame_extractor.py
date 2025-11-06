"""Extract key frames from video recordings."""

import cv2
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)


class FrameExtractor:
    """Extracts key frames from video files.

    Uses scene change detection and interval sampling to identify important frames.
    """

    def __init__(
        self,
        scene_threshold: float = 0.3,
        min_interval: float = 1.0,
        max_frames: Optional[int] = None,
    ):
        """Initialize frame extractor.

        Args:
            scene_threshold: Threshold for scene change detection (0-1)
            min_interval: Minimum time between frames in seconds
            max_frames: Maximum number of frames to extract (None = no limit)
        """
        self.scene_threshold = scene_threshold
        self.min_interval = min_interval
        self.max_frames = max_frames

    def _calculate_frame_diff(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray,
    ) -> float:
        """Calculate difference between two frames.

        Args:
            frame1: First frame
            frame2: Second frame

        Returns:
            Normalized difference score (0-1)
        """
        # Convert to grayscale
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        # Calculate absolute difference
        diff = cv2.absdiff(gray1, gray2)

        # Normalize to 0-1 range
        return np.mean(diff) / 255.0

    def extract_frames(
        self,
        video_path: Path,
        output_dir: Path,
        method: str = "scene_change",
    ) -> List[Dict[str, Any]]:
        """Extract key frames from video.

        Args:
            video_path: Path to video file
            output_dir: Directory to save extracted frames
            method: Extraction method ("scene_change", "interval", or "hybrid")

        Returns:
            List of frame metadata dictionaries

        Raises:
            FileNotFoundError: If video file doesn't exist
            RuntimeError: If video cannot be opened
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Open video
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open video: {video_path}")

        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        logger.info(
            f"Processing video: {video_path.name} "
            f"({total_frames} frames, {duration:.2f}s, {fps:.2f} FPS)"
        )

        frames_data = []
        prev_frame = None
        last_saved_time = -self.min_interval  # Allow first frame

        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            current_time = frame_idx / fps if fps > 0 else 0
            time_since_last = current_time - last_saved_time

            # Check if we should save this frame
            should_save = False

            if method in ("scene_change", "hybrid"):
                # Scene change detection
                if prev_frame is not None and time_since_last >= self.min_interval:
                    diff = self._calculate_frame_diff(prev_frame, frame)
                    if diff > self.scene_threshold:
                        should_save = True
                        logger.debug(
                            f"Scene change detected at {current_time:.2f}s "
                            f"(diff={diff:.3f})"
                        )

            if method in ("interval", "hybrid") and not should_save:
                # Interval-based sampling
                if time_since_last >= self.min_interval * 2:  # Double interval for fallback
                    should_save = True
                    logger.debug(f"Interval frame at {current_time:.2f}s")

            # Save frame if needed
            if should_save or (frame_idx == 0 and method != "scene_change"):
                # Check max frames limit
                if self.max_frames and len(frames_data) >= self.max_frames:
                    logger.info(f"Reached max frames limit: {self.max_frames}")
                    break

                # Save frame
                frame_filename = f"frame_{len(frames_data):04d}.png"
                frame_path = output_dir / frame_filename
                cv2.imwrite(str(frame_path), frame)

                frames_data.append({
                    "index": frame_idx,
                    "timestamp": round(current_time, 2),
                    "path": str(frame_path),
                    "filename": frame_filename,
                })

                last_saved_time = current_time
                logger.debug(f"Saved frame {len(frames_data)} at {current_time:.2f}s")

            prev_frame = frame.copy()
            frame_idx += 1

        cap.release()

        logger.info(f"Extracted {len(frames_data)} frames from {total_frames} total frames")
        return frames_data

    def extract_specific_times(
        self,
        video_path: Path,
        output_dir: Path,
        timestamps: List[float],
    ) -> List[Dict[str, Any]]:
        """Extract frames at specific timestamps.

        Args:
            video_path: Path to video file
            output_dir: Directory to save extracted frames
            timestamps: List of timestamps in seconds

        Returns:
            List of frame metadata dictionaries
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        frames_data = []

        for i, timestamp in enumerate(sorted(timestamps)):
            # Seek to timestamp
            frame_number = int(timestamp * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

            ret, frame = cap.read()
            if not ret:
                logger.warning(f"Could not extract frame at {timestamp}s")
                continue

            # Save frame
            frame_filename = f"frame_{i:04d}.png"
            frame_path = output_dir / frame_filename
            cv2.imwrite(str(frame_path), frame)

            frames_data.append({
                "index": frame_number,
                "timestamp": round(timestamp, 2),
                "path": str(frame_path),
                "filename": frame_filename,
            })

        cap.release()
        logger.info(f"Extracted {len(frames_data)} frames at specific timestamps")
        return frames_data
