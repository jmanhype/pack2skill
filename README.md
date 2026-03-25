# pack2skill

Records user workflows (screen video + interaction events) and generates Claude Skills from the captured data. Uses vision-language models to extract steps from video frames, then formats them into the Claude Skill directory structure.

## Status

Alpha (v0.1.0). Published on PyPI. The recording and generation pipeline is implemented. Quality scoring and team features are partially built. Ecosystem/marketplace integration (Phase 4) is not implemented.

## Architecture

```
pack2skill/
  cli/           # Click CLI (record, generate, install commands)
  core/
    recorder/    # Screen recording (FFmpeg) + keyboard/mouse event capture
    analyzer/    # Frame extraction, vision-language captioning
    generator/   # Skill template generation and formatting
    utils/       # Shared utilities
  quality/       # Confidence scoring, description optimization, robustness checks
  team/          # Version control integration (versioning.py only)
```

### Modules

| Package | Files | Purpose |
|---|---|---|
| `core/recorder` | 3 | Screen capture (FFmpeg), keyboard/mouse events, workflow session management |
| `core/analyzer` | 3 | Frame extraction, vision-language captioning, frame analysis |
| `core/generator` | 2 | Skill generation logic, output formatting |
| `quality` | 3 | Confidence scoring, description optimization, edge case robustness |
| `team` | 1 | Version control integration |
| `cli` | 1 | Click CLI entry point |

## Usage

```bash
pip install pack2skill

# Record a workflow
pack2skill record --output my_workflow.json

# Generate a skill from recording
pack2skill generate my_workflow.json --output ./skills/

# Install generated skill
pack2skill install ./skills/my-skill/
```

## Dependencies

- Python 3.9+
- FFmpeg (screen recording)
- transformers, torch (vision-language models)
- opencv-python, pillow (frame processing)
- pytesseract (OCR)
- pynput (input capture)
- anthropic, openai (LLM integration)
- click (CLI)

A CUDA-capable GPU is recommended for vision model inference.

## Tests

```bash
pytest tests/
```

1 test file (`test_generator.py`). Test coverage is minimal.

## Docs

The `docs/` directory contains guides for installation, recording, generation, team setup, and API reference.

## Limitations

- Phase 1 (recording + generation) is the only functional pipeline
- Phase 2 quality modules exist but are not integrated into the main CLI flow
- Phase 3 team features are stubs (only `versioning.py` has code)
- Phase 4 ecosystem/marketplace integration does not exist
- No CI/CD pipeline configured
- Test coverage is 1 file; no integration or e2e tests
- Screen recording depends on FFmpeg and platform-specific screen capture
- Vision model inference requires significant GPU memory
- The `ecosystem/` directory referenced in the original README does not exist in the repository
