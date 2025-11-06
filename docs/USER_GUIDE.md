## Pack2Skill User Guide

Complete guide to using Pack2Skill for generating Claude Skills from recorded workflows.

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Phase 1: MVP - Recording & Generation](#phase-1-mvp)
4. [Phase 2: Quality Improvements](#phase-2-quality)
5. [Phase 3: Team Collaboration](#phase-3-team)
6. [Phase 4: Ecosystem Integration](#phase-4-ecosystem)
7. [Advanced Usage](#advanced-usage)
8. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites

- Python 3.9 or higher
- FFmpeg (for screen recording)
- CUDA-capable GPU (optional, for faster vision models)

### Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

### Install Pack2Skill

```bash
# Clone the repository
git clone https://github.com/yourusername/pack2skill.git
cd pack2skill

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

Verify installation:
```bash
pack2skill --version
```

---

## Quick Start

### 1. Record a Workflow

```bash
pack2skill record --name my-workflow --description "Export presentation to PDF"
```

The recorder will start capturing your screen and user interactions. Perform your workflow, then press **Ctrl+C** to stop.

### 2. Analyze the Recording

```bash
pack2skill analyze ./recordings/my-workflow.json
```

This extracts key frames, generates captions, and creates structured steps.

### 3. Generate the Skill

```bash
pack2skill generate ./recordings/my-workflow_analysis/session.json
```

This creates a Claude Skill folder with SKILL.md, REFERENCE.md, and helper scripts.

### 4. Install the Skill

```bash
pack2skill install ./skills/my-workflow
```

The skill is now available in Claude!

---

## Phase 1: MVP - Recording & Generation

### Recording Workflows

#### Basic Recording

```bash
pack2skill record
```

This starts recording with default settings. You'll be prompted for a summary when you stop.

#### Advanced Recording Options

```bash
pack2skill record \
  --name workflow-name \
  --description "What this workflow does" \
  --framerate 15 \
  --resolution 1920x1080 \
  --no-events  # Disable keyboard/mouse tracking
```

**Options:**
- `--output-dir, -o`: Directory to save recordings (default: `./recordings`)
- `--name, -n`: Name for the recording session
- `--description, -d`: Description of what you're recording
- `--framerate, -f`: Video frame rate (default: 12 FPS)
- `--resolution, -r`: Video resolution (e.g., "1440x900")
- `--no-events`: Disable event recording

#### Recording Tips

1. **Prepare your environment** - Close unnecessary windows, ensure the application is visible
2. **Go slowly** - Pause briefly between actions so they're captured clearly
3. **Use the mouse** - Clicking is easier to detect than keyboard shortcuts
4. **Provide context** - Enter a good description and summary

### Analyzing Recordings

```bash
pack2skill analyze SESSION_FILE [OPTIONS]
```

**Options:**
- `--output-dir, -o`: Output directory for analysis (default: auto-generated)
- `--method`: Frame extraction method:
  - `scene_change` (default): Detect significant screen changes
  - `interval`: Sample at regular intervals
  - `hybrid`: Combine both methods
- `--model`: Caption model (default: "Salesforce/blip-image-captioning-large")
- `--no-ocr`: Disable OCR text extraction

**Example:**
```bash
pack2skill analyze ./recordings/my-workflow.json \
  --method hybrid \
  --output-dir ./analysis/my-workflow
```

### Generating Skills

```bash
pack2skill generate SESSION_FILE [OPTIONS]
```

**Options:**
- `--output-dir, -o`: Directory to create skill in (default: `./skills`)
- `--name, -n`: Custom skill name
- `--description, -d`: Custom skill description
- `--version`: Skill version (default: "0.1.0")

**Example:**
```bash
pack2skill generate ./recordings/my-workflow_analysis/session.json \
  --name export-to-pdf \
  --description "Export Keynote presentation to PDF" \
  --version 1.0.0
```

### Skill Structure

Generated skills follow this structure:

```
my-skill/
├── SKILL.md           # Main skill definition
├── REFERENCE.md       # Detailed documentation
├── CHANGELOG.md       # Version history (if versioned)
└── scripts/
    └── helper.py      # Helper scripts (optional)
```

**SKILL.md Format:**
```markdown
---
name: my-skill
description: Use this skill when you need to...
version: 0.1.0
---

# My Skill

## Instructions

1. First step
2. Second step
3. Third step

## Examples

- Example use case 1
- Example use case 2
```

---

## Phase 2: Quality Improvements

### Confidence Scoring

Pack2Skill automatically scores each step's reliability based on:
- **Visual certainty**: Caption quality and clarity
- **Event alignment**: Match between visual and interaction data
- **Temporal consistency**: Reasonable timing between steps

**Using in Python:**
```python
from pack2skill.quality import ConfidenceScorer

scorer = ConfidenceScorer()
scored_steps = scorer.score_steps(steps)

# Generate report
report = scorer.generate_confidence_report(scored_steps)
print(f"Average confidence: {report['average_confidence']}")
print(f"Recommendation: {report['recommendation']}")
```

**Interpreting Scores:**
- **0.8-1.0**: High quality - skill is ready to use
- **0.6-0.8**: Good quality - review low confidence steps
- **0.4-0.6**: Moderate quality - manual review recommended
- **0.0-0.4**: Low quality - significant editing needed

### Description Optimization

Generates optimized descriptions that help Claude know when to trigger the skill.

**Using in Python:**
```python
from pack2skill.quality import DescriptionOptimizer

optimizer = DescriptionOptimizer()

# Generate optimized description
description = optimizer.optimize_description(
    summary="Export presentation to PDF",
    steps=workflow_steps,
    keywords=["Keynote", "PDF", "export"]
)

# Validate description
validation = optimizer.validate_description(description)
if not validation['valid']:
    print(f"Issues: {validation['issues']}")
    print(f"Suggestions: {validation['suggestions']}")
```

**Good Descriptions:**
- ✅ "Use this skill when you need to export a Keynote presentation to PDF"
- ✅ "Export slides to PDF and save to the Reports folder"
- ❌ "Do something with files" (too vague)
- ❌ "Click buttons and type things and then save..." (too long)

### Robustness Checking

Identifies potential issues and edge cases:

**Using in Python:**
```python
from pack2skill.quality import RobustnessChecker

checker = RobustnessChecker()

# Check workflow
results = checker.check_workflow(steps, session_metadata)

print(f"Robustness score: {results['robustness_score']}")
print(f"Issues: {results['issues']}")
print(f"Recommendations: {results['recommendations']}")

# Generate improved steps
improved = checker.generate_improved_steps(steps, results)
```

**Common Issues:**
- Hardcoded filenames/paths
- Missing error handling
- Implicit assumptions
- Unhandled edge cases

---

## Phase 3: Team Collaboration

### Version Control

Initialize a git repository for your skills:

```bash
cd skills/
git init
git add .
git commit -m "Initial skill collection"
```

**Using the Version Manager:**
```python
from pack2skill.team import SkillVersionManager

manager = SkillVersionManager(skills_repo=Path("./skills"))

# Update version
new_version = manager.update_skill_version(
    skill_dir=Path("./skills/my-skill"),
    bump_type="minor",  # major, minor, or patch
    changelog_entry="Added error handling and improved descriptions"
)

# Commit to git
manager.commit_skill(
    skill_dir=Path("./skills/my-skill"),
    message=f"Release v{new_version}"
)

# Create version tag
manager.create_version_tag(Path("./skills/my-skill"))
```

### Sharing Skills

#### Project-Level Skills

Add skills to your project's `.claude/skills/` directory:

```bash
# Install to project
pack2skill install ./skills/my-skill
```

Commit the skill to your project repository so team members get it automatically.

#### Global Skills

Install skills globally for all Claude sessions:

```bash
# Install globally
pack2skill install --global ./skills/my-skill
```

### Skill Registry

Create a `skills/README.md` to document available skills:

```markdown
# Team Skills

## Available Skills

### export-to-pdf (v1.0.0)
Export Keynote presentations to PDF format.
- **Author**: @username
- **Last Updated**: 2024-01-15

### generate-report (v0.5.0)
Generate monthly reports from data files.
- **Author**: @username
- **Last Updated**: 2024-01-10
```

---

## Phase 4: Ecosystem Integration

### Claude Skills Marketplace

#### Contributing to Public Skills

1. Ensure your skill is high quality (confidence > 0.8)
2. Add comprehensive documentation
3. Test thoroughly
4. Submit PR to [anthropics/skills](https://github.com/anthropics/skills)

#### Publishing Guidelines

- Remove any sensitive/proprietary information
- Generalize hardcoded values
- Include clear examples
- Add proper attribution

### MCP Integration

If your skill needs external APIs, consider using MCP (Model Context Protocol):

```python
# In scripts/helper.py
import mcp

async def fetch_data():
    """Fetch data from external API via MCP."""
    client = mcp.Client()
    result = await client.call("api-server", "fetch_data", {})
    return result
```

Refer to [Anthropic's MCP documentation](https://docs.anthropic.com/claude/docs/mcp) for details.

---

## Advanced Usage

### Custom Caption Models

Use a different vision-language model:

```bash
pack2skill analyze session.json \
  --model "microsoft/git-large-textcaps"
```

**Recommended Models:**
- `Salesforce/blip-image-captioning-large` (default) - Good balance
- `microsoft/git-large-textcaps` - Better for UI text
- `nlpconnect/vit-gpt2-image-captioning` - Faster, less accurate

### Batch Processing

Process multiple recordings:

```python
from pack2skill.core import SkillGenerator
from pathlib import Path

generator = SkillGenerator()

session_files = list(Path("./recordings").glob("*.json"))

generated = generator.batch_generate(
    session_files=session_files,
    output_dir=Path("./skills")
)

print(f"Generated {len(generated)} skills")
```

### Custom Quality Thresholds

Adjust confidence scoring weights:

```python
from pack2skill.quality import ConfidenceScorer

scorer = ConfidenceScorer(
    visual_weight=0.5,    # Emphasize visual quality
    event_weight=0.2,     # De-emphasize events
    temporal_weight=0.3,
)
```

---

## Troubleshooting

### Recording Issues

**Problem:** FFmpeg not found
```
Solution: Install FFmpeg and ensure it's in your PATH
```

**Problem:** No frames extracted
```
Solution:
- Check if video file exists and is valid
- Try --method interval instead of scene_change
- Increase framerate during recording
```

**Problem:** Events not recorded
```
Solution:
- Install pynput: pip install pynput
- Check permissions (macOS requires Accessibility permissions)
- Use --no-events to disable if not needed
```

### Analysis Issues

**Problem:** Poor quality captions
```
Solution:
- Use a better caption model (e.g., microsoft/git-large-textcaps)
- Ensure clear, high-contrast UI in recordings
- Record at higher resolution
```

**Problem:** Out of memory during analysis
```
Solution:
- Use CPU instead of GPU: export CUDA_VISIBLE_DEVICES=""
- Process fewer frames: --method interval
- Use a smaller caption model
```

### Skill Issues

**Problem:** Skill doesn't trigger in Claude
```
Solution:
- Improve the description - make it more specific
- Add more example use cases
- Include key terms that users would say
```

**Problem:** Steps are too generic
```
Solution:
- Record more slowly with clear actions
- Enable OCR to capture UI text
- Manually edit SKILL.md for clarity
```

---

## Getting Help

- **Documentation**: [docs/](../docs/)
- **Examples**: [examples/](../examples/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/pack2skill/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/pack2skill/discussions)

---

## Next Steps

- Try the [Example Workflows](../examples/example_usage.py)
- Read the [API Reference](./API_REFERENCE.md)
- Join the community and share your skills!
