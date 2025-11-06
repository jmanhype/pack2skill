# Pack to Claude Skill Pipeline

A comprehensive system for capturing workflows and automatically generating Claude Skills from recorded user interactions.

## Overview

This pipeline transforms real-world workflows into Claude Skills through four progressive phases:

1. **Phase 1 (MVP)**: Recording & Basic Skill Generation
2. **Phase 2**: Improving Skill Quality (confidence, descriptions, robustness)
3. **Phase 3**: Collaboration & Deployment (team features)
4. **Phase 4**: Ecosystem Integration and Marketplace

## Features

- **Workflow Recording**: Capture screen video and user interaction events
- **Vision-Language Analysis**: Extract meaningful steps from video frames
- **Automated Skill Generation**: Create Claude Skills with proper structure and metadata
- **Confidence Scoring**: Rate the reliability of each generated step
- **Team Collaboration**: Version control, sharing, and deployment features
- **Ecosystem Integration**: Connect with Claude's skill marketplace and MCP plugins

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Record a workflow
python -m pack2skill record --output my_workflow.json

# Generate a skill
python -m pack2skill generate my_workflow.json --output ./skills/

# Install the skill
python -m pack2skill install ./skills/my-skill/
```

## Project Structure

```
pack2skill/
├── core/                 # Core functionality
│   ├── recorder/        # Workflow recording (screen + events)
│   ├── analyzer/        # Video frame analysis and captioning
│   ├── generator/       # Skill generation logic
│   └── utils/           # Shared utilities
├── quality/             # Phase 2: Quality improvements
│   ├── confidence.py    # Confidence scoring
│   ├── description.py   # Description optimization
│   └── robustness.py    # Edge case handling
├── team/                # Phase 3: Team features
│   ├── versioning.py    # Version control integration
│   ├── deployment.py    # Skill deployment
│   └── testing.py       # Testing framework
├── ecosystem/           # Phase 4: Ecosystem integration
│   ├── marketplace.py   # Marketplace features
│   └── integrations.py  # MCP and plugin support
├── cli/                 # Command-line interface
└── tests/               # Test suite
```

## Requirements

- Python 3.9+
- FFmpeg (for screen recording)
- CUDA-capable GPU (recommended for vision models)

## Documentation

See the [docs/](docs/) directory for detailed documentation:

- [Installation Guide](docs/installation.md)
- [Recording Guide](docs/recording.md)
- [Skill Generation](docs/generation.md)
- [Team Setup](docs/team-setup.md)
- [API Reference](docs/api-reference.md)

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Built for the Claude Skills ecosystem by Anthropic.
