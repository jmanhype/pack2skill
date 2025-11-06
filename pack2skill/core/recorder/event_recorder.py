"""User interaction event recording."""

import json
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from threading import Thread, Event as ThreadEvent

try:
    from pynput import mouse, keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    logging.warning("pynput not available. Event recording will be disabled.")

logger = logging.getLogger(__name__)


class EventRecorder:
    """Records user interaction events (mouse clicks, keystrokes).

    Uses pynput to capture keyboard and mouse events with timestamps.
    """

    def __init__(self, output_dir: Path = Path("./recordings")):
        """Initialize event recorder.

        Args:
            output_dir: Directory to save event logs
        """
        if not PYNPUT_AVAILABLE:
            raise RuntimeError(
                "pynput is not installed. Install it with: pip install pynput"
            )

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.events: List[Dict[str, Any]] = []
        self.start_time: Optional[float] = None
        self.current_output: Optional[Path] = None

        # Listeners
        self.mouse_listener: Optional[mouse.Listener] = None
        self.keyboard_listener: Optional[keyboard.Listener] = None
        self.stop_event = ThreadEvent()

    def _get_timestamp(self) -> float:
        """Get relative timestamp from recording start.

        Returns:
            Time in seconds since recording started
        """
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time

    def _on_click(self, x: int, y: int, button, pressed: bool):
        """Handle mouse click events.

        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button
            pressed: True if pressed, False if released
        """
        if not pressed:  # Only record on button release (complete click)
            event = {
                "t": round(self._get_timestamp(), 2),
                "type": "click",
                "x": x,
                "y": y,
                "button": str(button),
            }
            self.events.append(event)
            logger.debug(f"Click event: {event}")

    def _on_key(self, key):
        """Handle keyboard events.

        Args:
            key: Key that was pressed
        """
        try:
            # Regular character key
            key_str = key.char
        except AttributeError:
            # Special key (e.g., Ctrl, Shift, Enter)
            key_str = str(key).replace("Key.", "")

        event = {
            "t": round(self._get_timestamp(), 2),
            "type": "keystroke",
            "key": key_str,
        }
        self.events.append(event)
        logger.debug(f"Keystroke event: {event}")

    def start_recording(self, name: Optional[str] = None) -> Path:
        """Start recording user events.

        Args:
            name: Optional name for the event log. Auto-generated if None.

        Returns:
            Path to the output JSON file

        Raises:
            RuntimeError: If recording is already in progress
        """
        if self.start_time is not None:
            raise RuntimeError("Recording already in progress")

        # Generate output filename
        if name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"events_{timestamp}"

        output_path = self.output_dir / f"{name}.json"
        self.current_output = output_path

        # Initialize
        self.events = []
        self.start_time = time.time()
        self.stop_event.clear()

        # Start listeners
        self.mouse_listener = mouse.Listener(on_click=self._on_click)
        self.keyboard_listener = keyboard.Listener(on_press=self._on_key)

        self.mouse_listener.start()
        self.keyboard_listener.start()

        logger.info(f"Event recording started: {output_path}")
        return output_path

    def stop_recording(self) -> Optional[Path]:
        """Stop recording events and save to file.

        Returns:
            Path to the saved event log, or None if no recording was active
        """
        if self.start_time is None:
            logger.warning("No recording in progress")
            return None

        logger.info("Stopping event recording...")

        # Stop listeners
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None

        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None

        # Save events to file
        output = self.current_output
        if output:
            with open(output, 'w') as f:
                json.dump(self.events, f, indent=2)
            logger.info(f"Event log saved: {output} ({len(self.events)} events)")

        # Reset state
        self.start_time = None
        self.current_output = None
        self.events = []

        return output

    def is_recording(self) -> bool:
        """Check if event recording is currently active.

        Returns:
            True if recording is in progress
        """
        return self.start_time is not None

    def get_events(self) -> List[Dict[str, Any]]:
        """Get the list of recorded events.

        Returns:
            List of event dictionaries
        """
        return self.events.copy()

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the current recording.

        Returns:
            Dictionary with recording metadata
        """
        return {
            "is_recording": self.is_recording(),
            "event_count": len(self.events),
            "current_output": str(self.current_output) if self.current_output else None,
            "elapsed_time": self._get_timestamp() if self.start_time else 0,
        }
