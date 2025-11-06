# Recording Guide

Learn how to record workflows using pack2skill.

## Overview

Pack2skill records workflows by capturing:
- **Screen video** - Visual representation of actions
- **Keyboard/mouse events** - User interactions with timestamps
- **System metadata** - Platform, duration, timestamps

## Quick Start

```bash
# Start recording (press Ctrl+C to stop)
python -m pack2skill record --output recordings/

# With custom settings
python -m pack2skill record \
  --output recordings/ \
  --name "my-workflow" \
  --description "Creating a GitHub repository" \
  --framerate 30 \
  --resolution 1920x1080
```

## Recording Commands

### Basic Recording

```bash
pack2skill record --output ./recordings/
```

This creates:
- `recording_TIMESTAMP.mp4` - Screen recording
- `recording_TIMESTAMP.json` - Event data and metadata

### Named Recording

```bash
pack2skill record \
  --output ./recordings/ \
  --name "deploy-app" \
  --description "Deploying application to production"
```

### Custom Frame Rate

```bash
pack2skill record \
  --output ./recordings/ \
  --framerate 60  # Higher quality, larger files
```

### Custom Resolution

```bash
pack2skill record \
  --output ./recordings/ \
  --resolution 2560x1440  # 2K resolution
```

### Record Without Events

```bash
pack2skill record \
  --output ./recordings/ \
  --no-events  # Screen only, no keyboard/mouse capture
```

## Recording Workflow

### 1. Preparation

Before starting:

- **Close unnecessary applications**
- **Hide sensitive information** (passwords, API keys)
- **Plan your workflow** - Know what you'll demonstrate
- **Clear your desktop** - Remove distractions

### 2. Start Recording

```bash
pack2skill record --output ./my-workflows/ --name "example"
```

You'll see:
```
Starting workflow recording...
Recording name: example
Output directory: ./my-workflows/
Press Ctrl+C to stop recording

[●] Recording... (0:15)
```

### 3. Perform Your Workflow

- **Work naturally** - No need to slow down
- **Be deliberate** - Each action should be clear
- **Avoid mistakes** - Edit in post or re-record
- **Stay on topic** - Focus on the workflow

### 4. Stop Recording

Press **Ctrl+C** (or Cmd+C on Mac)

You'll see:
```
Stopping recording...
✓ Screen recording saved: my-workflows/example_20250106_143022.mp4
✓ Events saved: my-workflows/example_20250106_143022.json
✓ Recording complete! Duration: 2m 34s
```

## Understanding Recording Files

### Video File (.mp4)

Contains the screen recording:
- **Format**: H.264/MP4
- **Framerate**: 30fps (default) or custom
- **Resolution**: System default or custom
- **Codec**: libx264 with yuv420p pixel format

### Events File (.json)

Contains workflow metadata and events:

```json
{
  "metadata": {
    "name": "example-workflow",
    "description": "Example description",
    "start_time": "2025-01-06T14:30:22",
    "end_time": "2025-01-06T14:32:56",
    "duration": 154.0,
    "platform": "Darwin",
    "resolution": "1920x1080",
    "framerate": 30
  },
  "events": [
    {
      "t": 0.0,
      "type": "keyboard",
      "key": "cmd",
      "pressed": true
    },
    {
      "t": 0.1,
      "type": "keyboard",
      "key": "space",
      "pressed": true
    },
    {
      "t": 2.5,
      "type": "click",
      "x": 640,
      "y": 400,
      "button": "Button.left"
    }
  ]
}
```

## Best Practices

### Recording Quality

**DO:**
- ✅ Use consistent window sizes
- ✅ Keep important actions in center of screen
- ✅ Pause between major steps
- ✅ Use keyboard shortcuts visibly

**DON'T:**
- ❌ Switch between applications unnecessarily
- ❌ Move too fast
- ❌ Include sensitive information
- ❌ Record for too long (split into parts)

### Workflow Organization

Organize recordings by project or category:

```bash
recordings/
├── github-workflows/
│   ├── create-repo_20250106.json
│   └── create-pr_20250106.json
├── deployment/
│   └── deploy-to-aws_20250106.json
└── database/
    └── backup-restore_20250106.json
```

### Privacy & Security

**Before recording:**
- Log out of sensitive accounts
- Clear browser history/cookies
- Hide personal information
- Use dummy data for demos

**During recording:**
- Avoid typing passwords
- Don't show API keys or tokens
- Blur sensitive areas if needed
- Use placeholder values

## Platform-Specific Notes

### macOS

**First-time setup:**
1. Grant screen recording permission:
   - System Preferences → Security & Privacy → Privacy
   - Select "Screen Recording"
   - Add Terminal or your IDE
   - Restart Terminal

**Known issues:**
- May need to grant permission to Python executable
- Some IDE terminals may require additional permissions

### Windows

**Requirements:**
- Git Bash or PowerShell recommended
- Administrator rights may be needed for first run

**Known issues:**
- Some antivirus software may block screen recording
- Add pack2skill to antivirus exceptions if needed

### Linux

**Requirements:**
- X11 or Wayland display server
- FFmpeg with appropriate video capture support

**X11:**
```bash
pack2skill record --output ./recordings/
# Uses x11grab for screen capture
```

**Wayland:**
```bash
# May need additional setup
export XDG_SESSION_TYPE=wayland
pack2skill record --output ./recordings/
```

## Troubleshooting

### "Permission denied" on macOS

Grant screen recording permissions (see macOS section above).

### "FFmpeg not found"

Install FFmpeg:
```bash
# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg

# Windows
choco install ffmpeg
```

### Recording is choppy/laggy

Reduce framerate or resolution:
```bash
pack2skill record --framerate 15 --resolution 1280x720
```

### No keyboard/mouse events captured

Check that pynput has proper permissions:
- **macOS**: Grant Accessibility permissions
- **Linux**: Check X11/Wayland access
- **Windows**: Run as administrator (first time only)

### File size too large

Options to reduce size:
1. Lower framerate: `--framerate 15`
2. Lower resolution: `--resolution 1280x720`
3. Record shorter sessions (split into parts)
4. Compress after recording:
   ```bash
   ffmpeg -i input.mp4 -crf 28 output_compressed.mp4
   ```

## Advanced Recording

### Recording Specific Window

```python
from pack2skill.core.recorder import WorkflowRecorder

recorder = WorkflowRecorder(
    output_dir="./recordings",
    framerate=30
)

# Custom FFmpeg options for window capture
recorder.screen_recorder.custom_options = [
    '-window_id', '0x1234',  # Specific window ID
]

session = recorder.start_recording(name="window-specific")
# Perform workflow...
recorder.stop_recording()
```

### Programmatic Recording

```python
from pack2skill.core.recorder import WorkflowRecorder
import time

# Create recorder
recorder = WorkflowRecorder(
    output_dir="./recordings",
    framerate=30,
    resolution=(1920, 1080)
)

# Start recording
session = recorder.start_recording(
    name="automated-workflow",
    description="Automated recording example"
)

# Your automation code here
time.sleep(10)

# Stop recording
workflow_data = recorder.stop_recording()
print(f"Saved to: {workflow_data['video_path']}")
```

## Next Steps

After recording:

1. **Analyze the recording**: [See Analyzing Recordings](generation.md#analyzing-recordings)
2. **Generate a skill**: [See Skill Generation](generation.md)
3. **Install and test**: [See Testing Skills](generation.md#testing-skills)

## Additional Resources

- [Skill Generation Guide](generation.md)
- [API Reference](api-reference.md)
- [User Guide](USER_GUIDE.md)
