# Skill Generation Guide

Learn how to generate Claude Skills from recorded workflows.

## Overview

Pack2skill transforms recorded workflows into production-ready Claude Skills through:

1. **Analysis** - Extract meaningful steps from video and events
2. **Generation** - Create Claude Skill structure
3. **Installation** - Deploy to Claude's skills directory

## Quick Start

```bash
# Generate skill from recording
python -m pack2skill generate recording.json --output-dir ./skills/

# Install the generated skill
python -m pack2skill install ./skills/my-skill/

# List installed skills
python -m pack2skill list
```

## Workflow Data Format

Before generation, your workflow data should have this structure:

```json
{
  "name": "My Workflow",
  "summary": "Brief description of what this workflow does",
  "steps": [
    {
      "text": "Description of the step",
      "action": "What action is performed",
      "timestamp": 0.0,
      "confidence": 0.95
    }
  ],
  "metadata": {
    "start_time": "2025-01-06T14:30:00",
    "duration": 120.0,
    "platform": "Darwin"
  }
}
```

## Generation Commands

### Basic Generation

```bash
python -m pack2skill generate workflow.json --output-dir ./skills/
```

Output:
```
Generating skill from: workflow.json
INFO: Generating skill: my-workflow
INFO: Output directory: ./skills/my-workflow
INFO: Created: ./skills/my-workflow/SKILL.md
INFO: Created: ./skills/my-workflow/REFERENCE.md
INFO: Created: ./skills/my-workflow/scripts/helper.py
✓ Skill generated: ./skills/my-workflow
```

### Custom Skill Name

```bash
python -m pack2skill generate workflow.json \
  --output-dir ./skills/ \
  --name "custom-skill-name"
```

### Custom Description

```bash
python -m pack2skill generate workflow.json \
  --output-dir ./skills/ \
  --description "Custom description for when to use this skill"
```

### Specify Version

```bash
python -m pack2skill generate workflow.json \
  --output-dir ./skills/ \
  --version "1.0.0"
```

## Generated Skill Structure

A generated skill includes:

```
my-skill/
├── SKILL.md          # Main skill file (Claude reads this)
├── REFERENCE.md      # Detailed implementation reference
└── scripts/
    └── helper.py     # Helper scripts (optional)
```

### SKILL.md

The main skill file with YAML frontmatter:

```markdown
---
name: my-skill
description: Use this skill when you need to perform XYZ task
version: 0.1.0
---

# My Skill

## Instructions

1. First step description
2. Second step description
3. Third step description

## Examples

- Example use case 1
- Example use case 2
```

### REFERENCE.md

Detailed reference documentation:

```markdown
# Reference

This skill was automatically generated from a recorded workflow.

## Recording Details

- Duration: 2m 30s
- Platform: macOS
- Recorded: 2025-01-06

## Detailed Steps

### Step 1

**Action:** Open terminal application

**Timestamp:** 0.00s

### Step 2

**Action:** Execute command

**Timestamp:** 5.50s
```

## Skill Naming

Pack2skill automatically converts names to Claude's format:

| Input | Output | Valid? |
|-------|--------|--------|
| "My Skill" | my-skill | ✅ |
| "Create GitHub Repo" | create-github-repo | ✅ |
| "Deploy to AWS!!" | deploy-to-aws | ✅ |
| "Very_Long_Skill_Name_That_Exceeds_Limit" | very-long-skill-name-that-exc | ✅ (truncated) |

**Rules:**
- Lowercase with hyphens
- Maximum 64 characters
- Alphanumeric and hyphens only

## Description Optimization

Good descriptions help Claude know when to use the skill:

**Good descriptions:**
```yaml
description: Extract text and tables from PDF files. Use when working with PDFs.
description: Deploy application to AWS using Docker. Use for deployment tasks.
description: Create GitHub repository and push code. Use for new projects.
```

**Poor descriptions:**
```yaml
description: For files  # Too vague
description: Helps with data  # Not specific
```

**Tips:**
- Be specific about what the skill does
- Include when to use it
- Keep under 200 characters
- Use action verbs

## Installation

### Install a Single Skill

```bash
python -m pack2skill install ./skills/my-skill/
```

Output:
```
✓ Skill installed: /Users/you/.claude/skills/my-skill

The skill is now available in Claude!
```

### Install to Custom Location

```bash
python -m pack2skill install ./skills/my-skill/ \
  --skills-dir /custom/path/to/skills/
```

### Verify Installation

```bash
python -m pack2skill list
```

Output:
```
Skills in /Users/you/.claude/skills:

  • my-skill
    Use this skill when you need to perform XYZ task

  • another-skill
    Description of another skill
```

## Testing Skills

### Test with Claude Code

1. Start Claude Code:
   ```bash
   claude
   ```

2. Ask Claude to use your skill:
   ```
   > Can you help me create a GitHub repository?
   ```

3. Claude will automatically detect and use your skill if the description matches.

### Manual Testing

View the skill file:
```bash
cat ~/.claude/skills/my-skill/SKILL.md
```

Verify the format:
```bash
# Check YAML frontmatter
head -10 ~/.claude/skills/my-skill/SKILL.md

# Check instructions
cat ~/.claude/skills/my-skill/SKILL.md | grep -A 20 "## Instructions"
```

## Quality Improvement

### Confidence Scoring

Pack2skill assigns confidence scores to each step:

```python
from pack2skill.quality.confidence import ConfidenceScorer

scorer = ConfidenceScorer()
confidence = scorer.score_step(step)

# Factors considered:
# - Visual clarity (0-1)
# - Event alignment (0-1)
# - Temporal consistency (0-1)
```

**Confidence levels:**
- 0.9-1.0: Excellent
- 0.7-0.9: Good
- 0.5-0.7: Fair
- <0.5: Poor (may need review)

### Description Optimization

Generate better descriptions:

```python
from pack2skill.quality.description import DescriptionOptimizer

optimizer = DescriptionOptimizer()
best_description = optimizer.optimize(
    summary="Create GitHub repo",
    steps=steps
)
```

### Robustness Checking

Identify potential issues:

```python
from pack2skill.quality.robustness import RobustnessChecker

checker = RobustnessChecker()
issues = checker.check_skill(skill_data)

# Checks for:
# - Hardcoded values
# - Missing error handling
# - Edge cases
# - Security concerns
```

## Advanced Generation

### Programmatic Generation

```python
from pack2skill.core.generator import SkillGenerator
from pathlib import Path

# Create generator
generator = SkillGenerator()

# Load workflow data
session_data = {
    "name": "Deploy Application",
    "summary": "Deploy app to production",
    "steps": [
        {"text": "Build Docker image", "action": "docker build", "timestamp": 0.0},
        {"text": "Push to registry", "action": "docker push", "timestamp": 10.0},
        {"text": "Deploy to Kubernetes", "action": "kubectl apply", "timestamp": 20.0}
    ]
}

# Generate skill
skill_dir = generator.generate_skill(
    session_data=session_data,
    output_dir=Path("./skills"),
    skill_name="deploy-app",
    version="1.0.0"
)

print(f"Skill created at: {skill_dir}")
```

### Custom Skill Templates

Create custom skill templates:

```python
skill_md_content = generator.formatter.generate_skill_md(
    name="my-custom-skill",
    description="Custom skill description",
    steps=steps,
    summary="Summary",
    version="1.0.0",
    allowed_tools=["Read", "Write", "Bash"]  # Restrict tool access
)
```

### Batch Generation

Generate multiple skills:

```python
from pack2skill.core.generator import SkillGenerator
from pathlib import Path

generator = SkillGenerator()

# List of workflow files
workflow_files = [
    Path("recording1.json"),
    Path("recording2.json"),
    Path("recording3.json")
]

# Generate all skills
skill_dirs = generator.batch_generate(
    session_files=workflow_files,
    output_dir=Path("./skills")
)

print(f"Generated {len(skill_dirs)} skills")
```

## Troubleshooting

### Skill not detected by Claude

**Check:**
1. Description is specific and actionable
2. Skill is installed in `~/.claude/skills/`
3. SKILL.md has valid YAML frontmatter
4. Name is properly formatted (lowercase-hyphenated)

**Fix:**
```bash
# Reinstall
python -m pack2skill install ./skills/my-skill/ --force

# Verify
python -m pack2skill list
```

### Invalid YAML frontmatter

**Error:**
```
Error: Invalid YAML in SKILL.md
```

**Fix:**
Check frontmatter format:
```yaml
---
name: skill-name
description: Skill description
version: 0.1.0
---
```

Requirements:
- Opening and closing `---`
- Valid YAML syntax
- Required fields: name, description

### Steps missing or incomplete

**Issue:** Generated skill has incomplete instructions

**Causes:**
- Poor video quality
- Fast movements during recording
- Missing event data

**Solutions:**
1. Re-record with clearer actions
2. Manually edit SKILL.md to add detail
3. Use higher framerate during recording

### Hardcoded values detected

**Warning:**
```
⚠ Warning: Hardcoded value detected in step 3: "/Users/john/project"
```

**Fix:**
Edit SKILL.md to use placeholders:
```markdown
3. Navigate to project directory: `cd /path/to/your/project`
```

## Best Practices

### 1. Quality Workflows

- Record clear, deliberate actions
- Use consistent workflows
- Test workflows before recording
- Split complex workflows into smaller skills

### 2. Naming Convention

- Use descriptive names
- Follow verb-noun pattern: `create-repository`, `deploy-application`
- Keep names concise
- Be consistent across related skills

### 3. Organization

```bash
skills/
├── github/
│   ├── create-repo/
│   ├── create-pr/
│   └── review-pr/
├── deployment/
│   ├── deploy-aws/
│   └── deploy-gcp/
└── database/
    ├── backup-db/
    └── restore-db/
```

### 4. Documentation

- Keep REFERENCE.md updated
- Add examples in SKILL.md
- Document prerequisites
- Note platform-specific requirements

### 5. Version Control

Track your skills:
```bash
cd ~/.claude/skills
git init
git add .
git commit -m "Initial skills"
```

## Next Steps

- [Team Setup Guide](team-setup.md) - Share skills with your team
- [API Reference](api-reference.md) - Programmatic usage
- [User Guide](USER_GUIDE.md) - Complete documentation

## Additional Resources

- [Claude Skills Documentation](https://docs.claude.com/claude-code/skills)
- [GitHub Repository](https://github.com/jmanhype/pack2skill)
- [Issue Tracker](https://github.com/jmanhype/pack2skill/issues)
