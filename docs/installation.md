# Installation Guide

This guide covers installing pack2skill and its dependencies.

## Quick Install

```bash
pip install pack2skill
```

## System Requirements

- **Python**: 3.9 or higher
- **Operating System**: macOS, Windows, or Linux
- **FFmpeg**: Required for screen recording
- **Disk Space**: 500MB+ for models (optional)

## Installation Methods

### 1. Install from PyPI (Recommended)

```bash
pip install pack2skill
```

Verify installation:
```bash
pack2skill --version
```

### 2. Install from Source

```bash
git clone https://github.com/jmanhype/pack2skill.git
cd pack2skill
pip install -e .
```

### 3. Install with Development Dependencies

```bash
pip install pack2skill[dev]
```

Or from source:
```bash
git clone https://github.com/jmanhype/pack2skill.git
cd pack2skill
pip install -e ".[dev]"
```

## Installing FFmpeg

### macOS

Using Homebrew:
```bash
brew install ffmpeg
```

### Windows

Using Chocolatey:
```bash
choco install ffmpeg
```

Or download from: https://ffmpeg.org/download.html

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install ffmpeg
```

### Linux (Fedora)

```bash
sudo dnf install ffmpeg
```

## Installing Tesseract (Optional)

Tesseract is required for OCR text extraction from videos.

### macOS

```bash
brew install tesseract
```

### Windows

Download installer from: https://github.com/UB-Mannheim/tesseract/wiki

### Linux (Ubuntu/Debian)

```bash
sudo apt install tesseract-ocr
```

## Verifying Installation

Run the following commands to verify everything is installed:

```bash
# Check pack2skill
pack2skill --version

# Check FFmpeg
ffmpeg -version

# Check Tesseract (optional)
tesseract --version

# Check Python version
python --version
```

## Installing Vision Models (Optional)

Pack2skill can use BLIP or other vision-language models for better frame captioning.

### Install with CPU Support

The default installation includes CPU support:

```bash
pip install pack2skill
```

### Install with GPU Support (CUDA)

For NVIDIA GPUs:

```bash
pip install pack2skill
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Install with Apple Silicon Optimization

For M1/M2 Macs:

```bash
pip install pack2skill
# PyTorch is automatically optimized for Apple Silicon
```

## Troubleshooting

### ImportError: No module named 'pack2skill'

Make sure you've installed the package:
```bash
pip install pack2skill
```

If you installed from source, use:
```bash
pip install -e .
```

### FFmpeg not found

Add FFmpeg to your system PATH:

**macOS/Linux:**
```bash
export PATH="/usr/local/bin:$PATH"
```

**Windows:**
Add FFmpeg bin directory to System Environment Variables.

### Permission denied errors

On macOS, grant screen recording permissions:
1. System Preferences → Security & Privacy → Privacy
2. Select "Screen Recording"
3. Add Terminal or your IDE

### CUDA out of memory

Reduce model size or use CPU:
```bash
# Use smaller models
export TRANSFORMERS_CACHE=/path/to/cache
```

Or edit your code to use `device="cpu"`.

### Module import errors

Reinstall with all dependencies:
```bash
pip install --force-reinstall pack2skill
```

## Updating pack2skill

To update to the latest version:

```bash
pip install --upgrade pack2skill
```

## Uninstalling

To remove pack2skill:

```bash
pip uninstall pack2skill
```

## Virtual Environments (Recommended)

Use a virtual environment to avoid conflicts:

```bash
# Create virtual environment
python -m venv pack2skill-env

# Activate it
# macOS/Linux:
source pack2skill-env/bin/activate
# Windows:
pack2skill-env\Scripts\activate

# Install pack2skill
pip install pack2skill
```

## Docker Installation (Advanced)

Create a `Dockerfile`:

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Install pack2skill
RUN pip install pack2skill

WORKDIR /workspace
CMD ["pack2skill", "--help"]
```

Build and run:

```bash
docker build -t pack2skill .
docker run -it pack2skill
```

## Next Steps

After installation:

1. Read the [Quick Start Guide](../QUICKSTART.md)
2. Try [Recording a Workflow](recording.md)
3. Learn about [Skill Generation](generation.md)

## Getting Help

- **Documentation**: https://github.com/jmanhype/pack2skill#readme
- **Issues**: https://github.com/jmanhype/pack2skill/issues
- **Discussions**: https://github.com/jmanhype/pack2skill/discussions
