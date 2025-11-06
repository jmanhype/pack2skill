"""Combined workflow recorder that coordinates screen and event recording."""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from pack2skill.core.recorder.screen_recorder import ScreenRecorder
from pack2skill.core.recorder.event_recorder import EventRecorder

logger = logging.getLogger(__name__)


class WorkflowRecorder:
    """Coordinates screen and event recording for complete workflow capture.

    Manages synchronized recording of screen video and user interaction events.
    """

    def __init__(
        self,
        output_dir: Path = Path("./recordings"),
        framerate: int = 12,
        resolution: Optional[str] = None,
        record_events: bool = True,
    ):
        """Initialize workflow recorder.

        Args:
            output_dir: Directory to save recordings
            framerate: Frames per second for video
            resolution: Video resolution (auto-detected if None)
            record_events: Whether to record user interaction events
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.screen_recorder = ScreenRecorder(
            output_dir=output_dir,
            framerate=framerate,
            resolution=resolution,
        )

        self.event_recorder: Optional[EventRecorder] = None
        if record_events:
            try:
                self.event_recorder = EventRecorder(output_dir=output_dir)
            except RuntimeError as e:
                logger.warning(f"Event recording disabled: {e}")

        self.current_session: Optional[Dict[str, Any]] = None
        self.session_name: Optional[str] = None

    def start_recording(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Start recording a workflow.

        Args:
            name: Optional name for the workflow
            description: Optional description of what's being recorded

        Returns:
            Session metadata dictionary

        Raises:
            RuntimeError: If recording is already in progress
        """
        if self.current_session is not None:
            raise RuntimeError("Recording already in progress")

        # Generate session name
        if name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"workflow_{timestamp}"

        self.session_name = name

        # Start screen recording
        video_path = self.screen_recorder.start_recording(name)

        # Start event recording (if available)
        events_path = None
        if self.event_recorder:
            try:
                events_path = self.event_recorder.start_recording(name)
            except Exception as e:
                logger.warning(f"Failed to start event recording: {e}")

        # Create session metadata
        self.current_session = {
            "name": name,
            "description": description or "",
            "start_time": datetime.now().isoformat(),
            "video_path": str(video_path),
            "events_path": str(events_path) if events_path else None,
            "framerate": self.screen_recorder.framerate,
            "resolution": self.screen_recorder.resolution,
        }

        logger.info(f"Workflow recording started: {name}")
        return self.current_session.copy()

    def stop_recording(
        self,
        summary: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Stop recording and save session data.

        Args:
            summary: Optional summary of what was recorded

        Returns:
            Complete session data including paths to recordings, or None if no recording was active
        """
        if self.current_session is None:
            logger.warning("No recording in progress")
            return None

        logger.info("Stopping workflow recording...")

        # Stop screen recording
        video_path = self.screen_recorder.stop_recording()

        # Stop event recording
        events_path = None
        if self.event_recorder and self.event_recorder.is_recording():
            events_path = self.event_recorder.stop_recording()

        # Update session data
        self.current_session.update({
            "end_time": datetime.now().isoformat(),
            "summary": summary or "",
            "video_path": str(video_path) if video_path else None,
            "events_path": str(events_path) if events_path else None,
        })

        # Save session metadata
        session_file = self.output_dir / f"{self.session_name}.json"
        with open(session_file, 'w') as f:
            json.dump(self.current_session, f, indent=2)

        logger.info(f"Session metadata saved: {session_file}")

        result = self.current_session.copy()
        result["session_file"] = str(session_file)

        # Reset state
        self.current_session = None
        self.session_name = None

        return result

    def is_recording(self) -> bool:
        """Check if recording is currently active.

        Returns:
            True if recording is in progress
        """
        return self.current_session is not None

    def get_current_session(self) -> Optional[Dict[str, Any]]:
        """Get the current session metadata.

        Returns:
            Session metadata dictionary, or None if no recording is active
        """
        return self.current_session.copy() if self.current_session else None

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the recorder state.

        Returns:
            Dictionary with recorder metadata
        """
        metadata = {
            "is_recording": self.is_recording(),
            "output_dir": str(self.output_dir),
            "screen_recorder": self.screen_recorder.get_metadata(),
        }

        if self.event_recorder:
            metadata["event_recorder"] = self.event_recorder.get_metadata()

        if self.current_session:
            metadata["current_session"] = self.current_session.copy()

        return metadata
