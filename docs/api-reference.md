# API Reference

Complete API documentation for pack2skill's Python modules.

## Overview

Pack2skill provides a comprehensive Python API for:
- **Recording workflows** - Capture screen video and user events
- **Analyzing recordings** - Extract meaningful steps from workflows
- **Generating skills** - Create Claude Skills programmatically
- **Quality assessment** - Evaluate and improve skill quality
- **Team collaboration** - Manage shared skill repositories

## Installation

```bash
pip install pack2skill
```

For development:
```bash
pip install pack2skill[dev]
```

## Core Modules

### pack2skill.core.recorder

#### WorkflowRecorder

Records user workflows by capturing screen video and input events.

**Purpose:** Provides a complete workflow recording system that synchronizes screen capture with keyboard and mouse events.

```python
from pack2skill.core.recorder import WorkflowRecorder
from pathlib import Path
```

**Constructor:**

```python
WorkflowRecorder(
    output_dir: str | Path,
    framerate: int = 30,
    resolution: tuple[int, int] | None = None,
    capture_events: bool = True
)
```

**Parameters:**
- `output_dir` (str | Path): Directory where recordings will be saved
- `framerate` (int): Video frame rate (default: 30 fps). Higher values = better quality, larger files.
- `resolution` (tuple[int, int] | None): Video resolution as (width, height). None = system default.
- `capture_events` (bool): Whether to capture keyboard/mouse events (default: True)

**Methods:**

##### start_recording()

```python
def start_recording(
    name: str | None = None,
    description: str | None = None
) -> Dict[str, Any]
```

Start recording a workflow.

**Parameters:**
- `name` (str | None): Name for this recording session. Auto-generated if None.
- `description` (str | None): Description of the workflow being recorded.

**Returns:** Dictionary with session metadata:
```python
{
    "session_id": "abc123",
    "name": "my-workflow",
    "description": "Example workflow",
    "start_time": "2025-01-06T14:30:00",
    "output_dir": Path("/path/to/output")
}
```

**Example:**

```python
recorder = WorkflowRecorder(
    output_dir="./recordings",
    framerate=30,
    capture_events=True
)

# Start recording
session = recorder.start_recording(
    name="deploy-app",
    description="Deploying application to production"
)

print(f"Recording started: {session['session_id']}")

# Perform your workflow here...
import time
time.sleep(10)

# Stop recording
workflow_data = recorder.stop_recording()
```

##### stop_recording()

```python
def stop_recording() -> Dict[str, Any]
```

Stop the current recording and save files.

**Returns:** Complete workflow data:
```python
{
    "name": "my-workflow",
    "description": "Example workflow",
    "video_path": Path("/path/to/video.mp4"),
    "events_path": Path("/path/to/events.json"),
    "metadata": {
        "start_time": "2025-01-06T14:30:00",
        "end_time": "2025-01-06T14:32:30",
        "duration": 150.0,
        "platform": "Darwin",
        "resolution": "1920x1080",
        "framerate": 30
    },
    "events": [
        {"t": 0.0, "type": "click", "x": 640, "y": 400, "button": "Button.left"},
        {"t": 1.5, "type": "keyboard", "key": "cmd", "pressed": True}
    ]
}
```

**Edge Cases:**
- Calling without prior `start_recording()` raises `RuntimeError`
- Video file creation failure raises `IOError`
- Interrupted recording (Ctrl+C) automatically saves partial data

**Example:**

```python
try:
    recorder.start_recording(name="test-workflow")
    # ... perform workflow ...
    data = recorder.stop_recording()
    print(f"Saved video: {data['video_path']}")
    print(f"Saved events: {data['events_path']}")
    print(f"Duration: {data['metadata']['duration']}s")
except RuntimeError as e:
    print(f"Error: {e}")
```

---

### pack2skill.core.analyzer

#### WorkflowAnalyzer

Analyzes recorded workflows to extract meaningful steps.

**Purpose:** Transforms raw video and event data into structured workflow steps using vision-language models and OCR.

```python
from pack2skill.core.analyzer import WorkflowAnalyzer
```

**Constructor:**

```python
WorkflowAnalyzer(
    use_vision_model: bool = True,
    use_ocr: bool = True,
    device: str = "cpu"
)
```

**Parameters:**
- `use_vision_model` (bool): Use BLIP or similar for frame captioning (default: True)
- `use_ocr` (bool): Use Tesseract for text extraction (default: True)
- `device` (str): Device for ML models: "cpu", "cuda", or "mps" (default: "cpu")

**Methods:**

##### analyze_workflow()

```python
def analyze_workflow(
    video_path: str | Path,
    events_path: str | Path,
    frame_interval: float = 1.0
) -> Dict[str, Any]
```

Analyze a recorded workflow.

**Parameters:**
- `video_path` (str | Path): Path to video file (.mp4, .avi, .mov)
- `events_path` (str | Path): Path to events JSON file
- `frame_interval` (float): Seconds between frame analysis (default: 1.0). Lower = more detailed, slower.

**Returns:** Analysis results:
```python
{
    "steps": [
        {
            "text": "User opens terminal application",
            "action": "click",
            "timestamp": 0.0,
            "confidence": 0.95,
            "frame_caption": "Terminal window with command prompt",
            "ocr_text": "$ cd project",
            "event_type": "click"
        },
        # ... more steps
    ],
    "summary": "User sets up a new project by...",
    "metadata": {
        "total_frames": 150,
        "analyzed_frames": 30,
        "duration": 150.0,
        "analysis_time": 45.2
    }
}
```

**Edge Cases:**
- Missing video/events file raises `FileNotFoundError`
- Corrupted video returns partial analysis
- No events detected returns vision-only analysis
- Large videos (>10min) may take significant time

**Example:**

```python
analyzer = WorkflowAnalyzer(
    use_vision_model=True,
    use_ocr=True,
    device="cpu"
)

# Analyze recording
results = analyzer.analyze_workflow(
    video_path="recordings/my-workflow.mp4",
    events_path="recordings/my-workflow.json",
    frame_interval=1.0  # Analyze 1 frame per second
)

print(f"Found {len(results['steps'])} steps")
print(f"Summary: {results['summary']}")

for i, step in enumerate(results['steps'], 1):
    print(f"{i}. {step['text']} (confidence: {step['confidence']:.2f})")
```

**Architectural Context:**

WorkflowAnalyzer uses a multi-stage pipeline:
1. **Frame Extraction**: Extract key frames using scene change detection
2. **Vision Analysis**: BLIP model generates frame captions
3. **OCR**: Tesseract extracts visible text from UI elements
4. **Event Correlation**: Match keyboard/mouse events to visual changes
5. **Step Generation**: Combine all sources into coherent steps
6. **Confidence Scoring**: Assign quality scores based on multi-factor analysis

---

### pack2skill.core.generator

#### SkillGenerator

Generates Claude Skills from analyzed workflows.

**Purpose:** Transforms workflow analysis into properly formatted Claude Skills with YAML frontmatter and Markdown instructions.

```python
from pack2skill.core.generator import SkillGenerator
from pathlib import Path
```

**Constructor:**

```python
SkillGenerator()
```

No configuration needed - uses internal formatters and validators.

**Methods:**

##### generate_skill()

```python
def generate_skill(
    session_data: Dict[str, Any],
    output_dir: Path | str,
    skill_name: str | None = None,
    description: str | None = None,
    version: str = "0.1.0"
) -> Path
```

Generate a Claude Skill from workflow data.

**Parameters:**
- `session_data` (dict): Workflow data from analyzer or recorder
- `output_dir` (Path | str): Directory to create skill in
- `skill_name` (str | None): Skill name (auto-generated from session name if None)
- `description` (str | None): Skill description (auto-generated if None)
- `version` (str): Semantic version (default: "0.1.0")

**Returns:** Path to generated skill directory

**Session Data Format:**
```python
{
    "name": "My Workflow",
    "summary": "Brief description",
    "steps": [
        {
            "text": "Step description",
            "action": "Action performed",
            "timestamp": 0.0,
            "confidence": 0.95
        }
    ],
    "metadata": {
        "duration": 120.0,
        "platform": "Darwin",
        # ... other metadata
    }
}
```

**Edge Cases:**
- Invalid skill name characters are sanitized
- Description >200 chars is truncated with "..."
- Missing steps raises `ValueError`
- Output directory created if doesn't exist

**Example:**

```python
generator = SkillGenerator()

# Workflow data from analyzer
session_data = {
    "name": "Deploy Application",
    "summary": "Deploy app to production using Docker",
    "steps": [
        {
            "text": "Build Docker image",
            "action": "docker build",
            "timestamp": 0.0,
            "confidence": 0.98
        },
        {
            "text": "Push to registry",
            "action": "docker push",
            "timestamp": 10.0,
            "confidence": 0.95
        },
        {
            "text": "Deploy to Kubernetes",
            "action": "kubectl apply",
            "timestamp": 20.0,
            "confidence": 0.97
        }
    ],
    "metadata": {
        "duration": 30.0,
        "platform": "Darwin"
    }
}

# Generate skill
skill_path = generator.generate_skill(
    session_data=session_data,
    output_dir=Path("./skills"),
    skill_name="deploy-app",
    description="Deploy application to production using Docker and Kubernetes",
    version="1.0.0"
)

print(f"Skill created at: {skill_path}")
# Output: Skill created at: ./skills/deploy-app
```

**Generated Structure:**
```
deploy-app/
├── SKILL.md          # Main skill file
├── REFERENCE.md      # Detailed reference
└── scripts/
    └── helper.py     # Helper scripts (optional)
```

##### batch_generate()

```python
def batch_generate(
    session_files: list[Path],
    output_dir: Path
) -> list[Path]
```

Generate multiple skills from a list of workflow files.

**Parameters:**
- `session_files` (list[Path]): List of workflow JSON files
- `output_dir` (Path): Directory to create skills in

**Returns:** List of paths to generated skill directories

**Example:**

```python
from pathlib import Path

generator = SkillGenerator()

# List of workflow files
workflows = [
    Path("recordings/workflow1.json"),
    Path("recordings/workflow2.json"),
    Path("recordings/workflow3.json")
]

# Generate all skills
skill_paths = generator.batch_generate(
    session_files=workflows,
    output_dir=Path("./skills")
)

print(f"Generated {len(skill_paths)} skills:")
for path in skill_paths:
    print(f"  - {path.name}")
```

---

### pack2skill.core.generator.skill_formatter

#### SkillFormatter

Formats skill content according to Claude Skills specifications.

**Purpose:** Ensures generated skills comply with Anthropic's Claude Skills format requirements.

```python
from pack2skill.core.generator.skill_formatter import SkillFormatter
```

**Static Methods:**

##### sanitize_skill_name()

```python
@staticmethod
def sanitize_skill_name(name: str) -> str
```

Convert any string to valid Claude Skill name format.

**Parameters:**
- `name` (str): Raw skill name

**Returns:** Sanitized name (lowercase, hyphenated, ≤64 chars)

**Rules:**
- Convert to lowercase
- Replace spaces/underscores with hyphens
- Remove non-alphanumeric characters (except hyphens)
- Truncate to 64 characters
- Remove trailing hyphens

**Example:**

```python
from pack2skill.core.generator.skill_formatter import SkillFormatter

# Valid conversions
SkillFormatter.sanitize_skill_name("My Skill")
# Returns: "my-skill"

SkillFormatter.sanitize_skill_name("Create GitHub Repo")
# Returns: "create-github-repo"

SkillFormatter.sanitize_skill_name("Deploy_to_AWS!!!")
# Returns: "deploy-to-aws"

SkillFormatter.sanitize_skill_name("Very Long Skill Name That Exceeds The Maximum Character Limit For Skills")
# Returns: "very-long-skill-name-that-exceeds-the-maximum-character-limi"
```

##### truncate_description()

```python
@staticmethod
def truncate_description(description: str, max_length: int = 200) -> str
```

Truncate description to maximum length.

**Parameters:**
- `description` (str): Full description
- `max_length` (int): Maximum characters (default: 200)

**Returns:** Truncated description with "..." if needed

**Example:**

```python
long_desc = "This is a very long description that explains in great detail exactly what this skill does and when you should use it and all the edge cases and requirements..."

short_desc = SkillFormatter.truncate_description(long_desc, max_length=200)
print(short_desc)
# Output: "This is a very long description that explains in great detail exactly what this skill does and when you should use it and all the edge cases and requirements..."  (if >200 chars, ends with ...)
```

##### generate_skill_md()

```python
def generate_skill_md(
    name: str,
    description: str,
    steps: list[Dict[str, Any]],
    summary: str,
    version: str = "0.1.0",
    allowed_tools: list[str] | None = None
) -> str
```

Generate SKILL.md content.

**Parameters:**
- `name` (str): Skill name (will be sanitized)
- `description` (str): Skill description (will be truncated)
- `steps` (list[dict]): Workflow steps
- `summary` (str): Workflow summary
- `version` (str): Semantic version
- `allowed_tools` (list[str] | None): Restrict Claude to specific tools

**Returns:** Complete SKILL.md content as string

**Example:**

```python
formatter = SkillFormatter()

content = formatter.generate_skill_md(
    name="deploy-app",
    description="Deploy application to production",
    steps=[
        {"text": "Build Docker image", "action": "docker build"},
        {"text": "Push to registry", "action": "docker push"}
    ],
    summary="Automated deployment workflow",
    version="1.0.0",
    allowed_tools=["Bash", "Read", "Write"]
)

print(content)
```

**Output:**
```markdown
---
name: deploy-app
description: Deploy application to production
version: 1.0.0
allowed_tools: [Bash, Read, Write]
---

# Deploy App

## Instructions

1. Build Docker image
2. Push to registry

## Summary

Automated deployment workflow

## Examples

- Use when deploying to production
- Suitable for Docker-based applications
```

---

### pack2skill.quality.confidence

#### ConfidenceScorer

Assigns confidence scores to workflow steps.

**Purpose:** Evaluates step quality using multi-factor analysis to identify reliable vs. uncertain steps.

```python
from pack2skill.quality.confidence import ConfidenceScorer
```

**Constructor:**

```python
ConfidenceScorer(
    visual_weight: float = 0.4,
    event_weight: float = 0.4,
    temporal_weight: float = 0.2
)
```

**Parameters:**
- `visual_weight` (float): Weight for visual clarity (0-1, default: 0.4)
- `event_weight` (float): Weight for event alignment (0-1, default: 0.4)
- `temporal_weight` (float): Weight for temporal consistency (0-1, default: 0.2)

Weights should sum to 1.0.

**Methods:**

##### score_step()

```python
def score_step(
    step: Dict[str, Any],
    previous_step: Dict[str, Any] | None = None
) -> float
```

Calculate confidence score for a step.

**Parameters:**
- `step` (dict): Step to score
- `previous_step` (dict | None): Previous step for temporal analysis

**Returns:** Confidence score (0.0 to 1.0)

**Score Interpretation:**
- 0.9-1.0: Excellent - High confidence
- 0.7-0.9: Good - Reliable
- 0.5-0.7: Fair - May need review
- <0.5: Poor - Likely needs manual verification

**Factors Considered:**
1. **Visual Clarity** (40%):
   - Frame caption quality
   - OCR text presence
   - Scene complexity

2. **Event Alignment** (40%):
   - Event-to-visual correlation
   - Event type appropriateness
   - Action clarity

3. **Temporal Consistency** (20%):
   - Time gaps between steps
   - Logical sequence
   - Duration reasonableness

**Example:**

```python
scorer = ConfidenceScorer(
    visual_weight=0.4,
    event_weight=0.4,
    temporal_weight=0.2
)

steps = [
    {
        "text": "Open terminal",
        "action": "click",
        "timestamp": 0.0,
        "frame_caption": "Clear view of terminal application",
        "ocr_text": "Terminal",
        "event_type": "click"
    },
    {
        "text": "Execute command",
        "action": "keyboard",
        "timestamp": 2.5,
        "frame_caption": "Command prompt visible",
        "ocr_text": "$ npm install",
        "event_type": "keyboard"
    }
]

# Score each step
for i, step in enumerate(steps):
    prev = steps[i-1] if i > 0 else None
    confidence = scorer.score_step(step, prev)
    print(f"Step {i+1}: {step['text']}")
    print(f"Confidence: {confidence:.2f}")
```

**Edge Cases:**
- Missing fields default to low confidence contribution
- First step has no temporal analysis (previous_step=None)
- Extremely long/short time gaps reduce temporal score

---

### pack2skill.quality.description

#### DescriptionOptimizer

Optimizes skill descriptions for clarity and Claude compatibility.

**Purpose:** Generates concise, actionable descriptions that help Claude understand when to use a skill.

```python
from pack2skill.quality.description import DescriptionOptimizer
```

**Constructor:**

```python
DescriptionOptimizer()
```

**Methods:**

##### optimize()

```python
def optimize(
    summary: str,
    steps: list[Dict[str, Any]],
    max_length: int = 200
) -> str
```

Generate optimized description from workflow data.

**Parameters:**
- `summary` (str): Workflow summary
- `steps` (list[dict]): Workflow steps
- `max_length` (int): Maximum description length (default: 200)

**Returns:** Optimized description string

**Optimization Rules:**
1. Start with action verb (Create, Deploy, Generate, etc.)
2. Be specific about what the skill does
3. Include "Use when..." or "Use for..." context
4. Keep under max_length characters
5. Avoid vague terms ("helps with", "stuff", etc.)

**Example:**

```python
optimizer = DescriptionOptimizer()

summary = "This workflow shows how to create a new GitHub repository"
steps = [
    {"text": "Navigate to GitHub", "action": "browser"},
    {"text": "Click new repository button", "action": "click"},
    {"text": "Fill in repository details", "action": "type"},
    {"text": "Create repository", "action": "click"}
]

description = optimizer.optimize(summary, steps, max_length=200)
print(description)
# Output: "Create a new GitHub repository through the web interface. Use when starting new projects or setting up repositories."
```

---

### pack2skill.quality.robustness

#### RobustnessChecker

Identifies potential issues in generated skills.

**Purpose:** Validates skills for hardcoded values, missing error handling, and other robustness concerns.

```python
from pack2skill.quality.robustness import RobustnessChecker
```

**Constructor:**

```python
RobustnessChecker()
```

**Methods:**

##### check_skill()

```python
def check_skill(skill_data: Dict[str, Any]) -> list[Dict[str, Any]]
```

Check skill for potential issues.

**Parameters:**
- `skill_data` (dict): Generated skill data

**Returns:** List of issues found

**Issue Format:**
```python
{
    "type": "hardcoded_value",
    "severity": "warning",
    "message": "Hardcoded path detected: /Users/john/project",
    "step_index": 2,
    "suggestion": "Use a placeholder: /path/to/your/project"
}
```

**Checks Performed:**
1. **Hardcoded Values**:
   - Absolute paths
   - Email addresses
   - Usernames
   - API keys/tokens

2. **Missing Error Handling**:
   - Commands without validation
   - No fallback options
   - Unchecked prerequisites

3. **Security Concerns**:
   - Credential exposure
   - Unsafe commands
   - Permissions issues

4. **Edge Cases**:
   - Platform-specific commands
   - Missing dependencies
   - Race conditions

**Example:**

```python
checker = RobustnessChecker()

skill_data = {
    "name": "deploy-app",
    "steps": [
        {
            "text": "Navigate to /Users/john/myproject",
            "action": "cd /Users/john/myproject"
        },
        {
            "text": "Run deployment script",
            "action": "./deploy.sh"
        }
    ]
}

issues = checker.check_skill(skill_data)

for issue in issues:
    print(f"[{issue['severity'].upper()}] {issue['type']}")
    print(f"  Message: {issue['message']}")
    print(f"  Step: {issue['step_index']}")
    if 'suggestion' in issue:
        print(f"  Suggestion: {issue['suggestion']}")
```

**Output:**
```
[WARNING] hardcoded_value
  Message: Hardcoded path detected: /Users/john/myproject
  Step: 0
  Suggestion: Use a placeholder: /path/to/your/project

[WARNING] missing_error_handling
  Message: Command executed without validation
  Step: 1
  Suggestion: Add check for script existence before running
```

---

## Utility Functions

### pack2skill.core.utils

Miscellaneous utility functions.

```python
from pack2skill.core.utils import (
    get_platform_info,
    ensure_directory,
    load_json,
    save_json
)
```

##### get_platform_info()

```python
def get_platform_info() -> Dict[str, str]
```

Get current platform information.

**Returns:**
```python
{
    "platform": "Darwin",  # or "Windows", "Linux"
    "version": "24.6.0",
    "architecture": "arm64"
}
```

##### ensure_directory()

```python
def ensure_directory(path: Path | str) -> Path
```

Create directory if it doesn't exist.

**Parameters:**
- `path` (Path | str): Directory path

**Returns:** Path object

##### load_json()

```python
def load_json(file_path: Path | str) -> Dict[str, Any]
```

Load JSON file.

**Parameters:**
- `file_path` (Path | str): JSON file path

**Returns:** Parsed JSON data

**Raises:** `FileNotFoundError`, `json.JSONDecodeError`

##### save_json()

```python
def save_json(data: Dict[str, Any], file_path: Path | str) -> None
```

Save data to JSON file.

**Parameters:**
- `data` (dict): Data to save
- `file_path` (Path | str): Output file path

---

## Complete Example

Full workflow from recording to skill generation:

```python
from pack2skill.core.recorder import WorkflowRecorder
from pack2skill.core.analyzer import WorkflowAnalyzer
from pack2skill.core.generator import SkillGenerator
from pack2skill.quality.confidence import ConfidenceScorer
from pack2skill.quality.description import DescriptionOptimizer
from pack2skill.quality.robustness import RobustnessChecker
from pathlib import Path
import time

# 1. Record workflow
print("Recording workflow...")
recorder = WorkflowRecorder(
    output_dir="./recordings",
    framerate=30,
    capture_events=True
)

session = recorder.start_recording(
    name="create-repo",
    description="Create a new GitHub repository"
)

# Simulate workflow (in real usage, user performs actions)
time.sleep(10)

workflow_data = recorder.stop_recording()
print(f"Recorded {workflow_data['metadata']['duration']}s")

# 2. Analyze recording
print("\nAnalyzing workflow...")
analyzer = WorkflowAnalyzer(
    use_vision_model=True,
    use_ocr=True,
    device="cpu"
)

analysis = analyzer.analyze_workflow(
    video_path=workflow_data['video_path'],
    events_path=workflow_data['events_path'],
    frame_interval=1.0
)

print(f"Found {len(analysis['steps'])} steps")

# 3. Assess quality
print("\nAssessing quality...")
scorer = ConfidenceScorer()
optimizer = DescriptionOptimizer()

# Score steps
for i, step in enumerate(analysis['steps']):
    prev = analysis['steps'][i-1] if i > 0 else None
    step['confidence'] = scorer.score_step(step, prev)

# Optimize description
description = optimizer.optimize(
    summary=analysis['summary'],
    steps=analysis['steps']
)

# 4. Generate skill
print("\nGenerating skill...")
generator = SkillGenerator()

skill_path = generator.generate_skill(
    session_data={
        "name": workflow_data['name'],
        "summary": analysis['summary'],
        "steps": analysis['steps'],
        "metadata": workflow_data['metadata']
    },
    output_dir=Path("./skills"),
    description=description,
    version="0.1.0"
)

print(f"Skill generated: {skill_path}")

# 5. Check robustness
print("\nChecking robustness...")
checker = RobustnessChecker()
issues = checker.check_skill({
    "name": workflow_data['name'],
    "steps": analysis['steps']
})

if issues:
    print(f"Found {len(issues)} issues:")
    for issue in issues:
        print(f"  - [{issue['severity']}] {issue['message']}")
else:
    print("No issues found")

print("\n✓ Complete!")
```

---

## Error Handling

### Common Exceptions

```python
from pack2skill.core.exceptions import (
    RecordingError,
    AnalysisError,
    GenerationError,
    ValidationError
)
```

**RecordingError:** Raised during recording failures
**AnalysisError:** Raised during workflow analysis failures
**GenerationError:** Raised during skill generation failures
**ValidationError:** Raised when skill validation fails

**Example:**

```python
from pack2skill.core.recorder import WorkflowRecorder
from pack2skill.core.exceptions import RecordingError

try:
    recorder = WorkflowRecorder(output_dir="./recordings")
    session = recorder.start_recording()
    # ... workflow ...
    data = recorder.stop_recording()
except RecordingError as e:
    print(f"Recording failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Best Practices

### 1. Resource Management

Always clean up resources:

```python
recorder = WorkflowRecorder(output_dir="./recordings")
try:
    session = recorder.start_recording()
    # ... workflow ...
finally:
    if recorder.is_recording():
        recorder.stop_recording()
```

### 2. Error Handling

Handle errors gracefully:

```python
try:
    analyzer = WorkflowAnalyzer(use_vision_model=True)
    analysis = analyzer.analyze_workflow(video_path, events_path)
except FileNotFoundError:
    print("Recording files not found")
except AnalysisError as e:
    print(f"Analysis failed: {e}")
```

### 3. Performance Optimization

For large videos:

```python
# Reduce frame analysis frequency
analyzer = WorkflowAnalyzer(use_vision_model=True)
analysis = analyzer.analyze_workflow(
    video_path=video_path,
    events_path=events_path,
    frame_interval=2.0  # Analyze every 2 seconds instead of 1
)
```

### 4. Quality Validation

Always check quality before deployment:

```python
# Score steps
scorer = ConfidenceScorer()
low_confidence_steps = []

for i, step in enumerate(steps):
    confidence = scorer.score_step(step)
    if confidence < 0.7:
        low_confidence_steps.append((i, confidence))

if low_confidence_steps:
    print("Warning: Low confidence steps detected")
    for idx, conf in low_confidence_steps:
        print(f"  Step {idx}: {conf:.2f}")
```

---

## Next Steps

- [Installation Guide](installation.md) - Setup instructions
- [Recording Guide](recording.md) - Record workflows
- [Generation Guide](generation.md) - Generate skills
- [Team Setup](team-setup.md) - Team collaboration

## Additional Resources

- [GitHub Repository](https://github.com/jmanhype/pack2skill)
- [Issue Tracker](https://github.com/jmanhype/pack2skill/issues)
- [PyPI Package](https://pypi.org/project/pack2skill/)
