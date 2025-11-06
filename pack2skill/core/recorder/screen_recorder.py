"""Screen recording functionality using FFmpeg."""

import subprocess
import platform
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ScreenRecorder:
    """Records screen activity using FFmpeg.

    Supports cross-platform screen recording with configurable quality settings.
    """

    def __init__(
        self,
        output_dir: Path = Path("./recordings"),
        framerate: int = 12,
        resolution: Optional[str] = None,
    ):
        """Initialize screen recorder.

        Args:
            output_dir: Directory to save recordings
            framerate: Frames per second (default: 12)
            resolution: Video resolution (e.g., "1440x900"). Auto-detected if None.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.framerate = framerate
        self.resolution = resolution
        self.process: Optional[subprocess.Popen] = None
        self.current_output: Optional[Path] = None
        self.platform = platform.system()

    def _get_ffmpeg_command(self, output_path: Path) -> list[str]:
        """Build FFmpeg command based on platform.

        Args:
            output_path: Path to save the recording

        Returns:
            List of command arguments for FFmpeg

        Raises:
            RuntimeError: If platform is not supported
        """
        if self.platform == "Darwin":  # macOS
            cmd = [
                "ffmpeg",
                "-f", "avfoundation",
                "-framerate", str(self.framerate),
                "-i", "1:0",  # Screen 1, no audio (use "1:1" for audio)
            ]
            if self.resolution:
                cmd.extend(["-video_size", self.resolution])
            cmd.extend([
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-pix_fmt", "yuv420p",
                str(output_path)
            ])
            return cmd

        elif self.platform == "Windows":
            cmd = [
                "ffmpeg",
                "-f", "gdigrab",
                "-framerate", str(self.framerate),
                "-i", "desktop",
                "-offset_x", "0",
                "-offset_y", "0",
            ]
            if self.resolution:
                cmd.extend(["-video_size", self.resolution])
            cmd.extend([
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-pix_fmt", "yuv420p",
                str(output_path)
            ])
            return cmd

        elif self.platform == "Linux":
            # X11 capture
            display = ":0.0"  # Default display
            cmd = [
                "ffmpeg",
                "-f", "x11grab",
                "-framerate", str(self.framerate),
                "-i", display,
            ]
            if self.resolution:
                cmd.extend(["-video_size", self.resolution])
            cmd.extend([
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-pix_fmt", "yuv420p",
                str(output_path)
            ])
            return cmd

        else:
            raise RuntimeError(f"Unsupported platform: {self.platform}")

    def start_recording(self, name: Optional[str] = None) -> Path:
        """Start screen recording.

        Args:
            name: Optional name for the recording. Auto-generated if None.

        Returns:
            Path to the output video file

        Raises:
            RuntimeError: If recording is already in progress
        """
        if self.process is not None:
            raise RuntimeError("Recording already in progress")

        # Generate output filename
        if name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"recording_{timestamp}"

        output_path = self.output_dir / f"{name}.mp4"
        self.current_output = output_path

        # Build and execute FFmpeg command
        cmd = self._get_ffmpeg_command(output_path)
        logger.info(f"Starting recording: {output_path}")
        logger.debug(f"FFmpeg command: {' '.join(cmd)}")

        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            logger.info("Recording started successfully")
            return output_path

        except FileNotFoundError:
            raise RuntimeError(
                "FFmpeg not found. Please install FFmpeg and ensure it's in your PATH."
            )
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            raise

    def stop_recording(self) -> Optional[Path]:
        """Stop the current recording.

        Returns:
            Path to the recorded video file, or None if no recording was active
        """
        if self.process is None:
            logger.warning("No recording in progress")
            return None

        logger.info("Stopping recording...")

        # Send 'q' to FFmpeg to stop gracefully
        try:
            self.process.communicate(input=b'q', timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning("FFmpeg did not respond to quit command, terminating...")
            self.process.terminate()
            self.process.wait(timeout=5)

        output = self.current_output
        self.process = None
        self.current_output = None

        if output and output.exists():
            logger.info(f"Recording saved: {output}")
            return output
        else:
            logger.error("Recording file was not created")
            return None

    def is_recording(self) -> bool:
        """Check if recording is currently active.

        Returns:
            True if recording is in progress
        """
        return self.process is not None

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the current recording setup.

        Returns:
            Dictionary with recording metadata
        """
        return {
            "platform": self.platform,
            "framerate": self.framerate,
            "resolution": self.resolution,
            "output_dir": str(self.output_dir),
            "is_recording": self.is_recording(),
            "current_output": str(self.current_output) if self.current_output else None,
        }
