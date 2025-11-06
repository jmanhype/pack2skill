# Team Setup Guide

Learn how to share and collaborate on Claude Skills with your team.

## Overview

Pack2skill supports team collaboration through:
- **Shared skill repositories** - Version control for skills
- **Skill distribution** - Easy installation across team members
- **Custom skill directories** - Team-specific skill locations
- **Quality standards** - Consistent skill quality across team

## Quick Start

```bash
# Team lead: Create shared skills repository
git init team-skills
cd team-skills/
git remote add origin https://github.com/yourteam/team-skills.git

# Generate and share a skill
pack2skill generate workflow.json --output-dir ./skills/
git add skills/
git commit -m "Add new workflow skill"
git push

# Team member: Install shared skill
git clone https://github.com/yourteam/team-skills.git
pack2skill install team-skills/skills/my-skill/
```

## Setting Up Shared Skill Repository

### 1. Create Repository Structure

```bash
mkdir team-skills
cd team-skills/

# Create directory structure
mkdir -p skills/{development,deployment,testing,documentation}
mkdir -p templates
mkdir -p workflows

# Initialize git
git init
```

### 2. Add README

Create `README.md`:

```markdown
# Team Skills Repository

Shared Claude Skills for [Your Team Name].

## Structure

- `skills/` - Generated Claude Skills organized by category
- `templates/` - Skill templates for consistency
- `workflows/` - Recorded workflow files (.json, .mp4)

## Installation

```bash
# Install a specific skill
pack2skill install skills/development/setup-project/

# Install all skills in a category
for skill in skills/development/*/; do
    pack2skill install "$skill"
done
```

## Contributing

1. Record workflow using pack2skill
2. Generate skill with consistent naming
3. Test skill locally
4. Submit PR for team review
```

### 3. Add .gitignore

Create `.gitignore`:

```
# Video files (too large for git)
*.mp4
*.avi
*.mov

# Cache and temp files
__pycache__/
*.pyc
.DS_Store
*.swp

# Local development
venv/
.env
.vscode/
```

### 4. Create Directory Structure

```bash
team-skills/
├── README.md
├── .gitignore
├── skills/
│   ├── development/
│   │   ├── setup-project/
│   │   ├── create-pr/
│   │   └── code-review/
│   ├── deployment/
│   │   ├── deploy-staging/
│   │   └── deploy-production/
│   ├── testing/
│   │   ├── run-tests/
│   │   └── generate-coverage/
│   └── documentation/
│       ├── update-docs/
│       └── generate-api-docs/
├── templates/
│   └── skill-template.md
└── workflows/
    ├── development/
    ├── deployment/
    ├── testing/
    └── documentation/
```

## Skill Development Workflow

### For Skill Authors

#### 1. Record Workflow

```bash
# Create category directory for recordings
mkdir -p workflows/development/

# Record workflow
pack2skill record \
  --output workflows/development/ \
  --name "setup-new-project" \
  --description "Setting up a new Python project with dependencies"
```

#### 2. Generate Skill

```bash
# Generate skill in appropriate category
pack2skill generate \
  workflows/development/setup-new-project_*.json \
  --output-dir skills/development/ \
  --name "setup-new-project" \
  --description "Set up a new Python project with virtual environment and dependencies"
```

#### 3. Test Locally

```bash
# Install to your local Claude
pack2skill install skills/development/setup-new-project/

# Test with Claude Code
claude
# Ask Claude to help set up a new project
```

#### 4. Submit for Review

```bash
git add skills/development/setup-new-project/
git add workflows/development/setup-new-project_*.json
git commit -m "Add setup-new-project skill

- Automates Python project initialization
- Sets up virtual environment
- Installs common dependencies
- Creates project structure"

git push origin feature/setup-new-project
```

Create a pull request with:
- Description of what the skill does
- When it should be used
- Any prerequisites or dependencies
- Testing results

### For Reviewers

Review checklist:

```markdown
## Skill Review Checklist

- [ ] Skill name follows naming convention (lowercase-hyphenated)
- [ ] Description is clear and actionable (≤200 chars)
- [ ] SKILL.md has valid YAML frontmatter
- [ ] Instructions are clear and step-by-step
- [ ] No hardcoded sensitive values (paths, credentials)
- [ ] Examples are provided
- [ ] REFERENCE.md includes implementation details
- [ ] Skill tested locally and works as expected
- [ ] Appropriate category (development/deployment/testing/documentation)
```

## Installation Methods

### Individual Skills

```bash
# Install a single skill
pack2skill install team-skills/skills/development/setup-project/
```

### Category Installation

```bash
# Install all development skills
for skill in team-skills/skills/development/*/; do
    pack2skill install "$skill"
done
```

### Bulk Installation Script

Create `install-all.sh`:

```bash
#!/bin/bash

SKILLS_DIR="$1"
if [ -z "$SKILLS_DIR" ]; then
    SKILLS_DIR="./skills"
fi

echo "Installing skills from $SKILLS_DIR..."

# Find all skill directories (contain SKILL.md)
find "$SKILLS_DIR" -name "SKILL.md" -exec dirname {} \; | while read skill_path; do
    echo "Installing: $skill_path"
    pack2skill install "$skill_path"
done

echo "✓ All skills installed"
```

Usage:
```bash
chmod +x install-all.sh
./install-all.sh team-skills/skills/
```

## Custom Skill Locations

### Team-Specific Directory

```bash
# Set team skills directory
export CLAUDE_SKILLS_DIR="/shared/team-skills"

# Install to team location
pack2skill install \
  team-skills/skills/my-skill/ \
  --skills-dir "$CLAUDE_SKILLS_DIR"
```

### Individual + Team Skills

Keep both personal and team skills:

```bash
# Personal skills (default)
~/.claude/skills/
├── my-personal-skill/
└── my-experiment/

# Team skills (shared)
/shared/team-skills/
├── team-deployment/
├── team-testing/
└── team-docs/
```

Configure Claude to use both:
- Personal: `~/.claude/skills/` (default)
- Team: Install team skills to default location OR set `CLAUDE_SKILLS_DIR`

## Skill Templates

### Create Consistent Templates

Create `templates/skill-template.md`:

```markdown
---
name: {skill-name}
description: {Brief description of when to use this skill}
version: 0.1.0
author: {Your Team Name}
category: {development|deployment|testing|documentation}
---

# {Skill Title}

## Prerequisites

- List any required tools
- List any required permissions
- List any required configurations

## Instructions

1. First step description
   - Sub-step if needed
   - Important notes

2. Second step description
   - Sub-step if needed
   - Important notes

3. Third step description
   - Sub-step if needed
   - Important notes

## Examples

### Example 1: {Use Case Name}

Description of the use case.

```bash
# Example commands
command example
```

### Example 2: {Another Use Case}

Description of another use case.

## Troubleshooting

### Issue 1: {Common Problem}

**Symptoms:** What the user sees

**Solution:** How to fix it

### Issue 2: {Another Problem}

**Symptoms:** What the user sees

**Solution:** How to fix it

## Additional Notes

- Important considerations
- Edge cases
- Known limitations
```

### Using Templates

When generating skills, edit to match template:

```bash
# Generate skill
pack2skill generate workflow.json --output-dir ./temp/

# Edit to match team template
cp templates/skill-template.md temp/my-skill/SKILL.md
# Edit with workflow-specific content

# Install to team repo
mv temp/my-skill/ skills/development/
```

## Quality Standards

### Naming Conventions

Follow consistent naming:

```bash
# Good names
create-github-repo
deploy-to-aws
run-integration-tests
update-api-docs

# Bad names
CreateRepo          # Not lowercase-hyphenated
deploy_to_aws       # Use hyphens not underscores
test                # Too generic
NewProject!         # Special characters
```

### Description Guidelines

**Good descriptions:**
```yaml
description: Create a new GitHub repository with README and license. Use for new projects.
description: Deploy application to AWS using Docker and ECS. Use for production deployments.
description: Run full integration test suite and generate coverage report. Use before merging PRs.
```

**Bad descriptions:**
```yaml
description: For GitHub            # Too vague
description: Deployment            # Not specific
description: This skill helps with testing stuff  # Wordy, unclear
```

### Version Management

Use semantic versioning:

```yaml
version: 0.1.0  # Initial version
version: 0.2.0  # Add new functionality
version: 1.0.0  # Stable, production-ready
version: 1.1.0  # Add features (backwards compatible)
version: 2.0.0  # Breaking changes
```

Update version when:
- **Patch (0.0.x)**: Bug fixes, typos
- **Minor (0.x.0)**: New steps, improvements (backwards compatible)
- **Major (x.0.0)**: Breaking changes, restructure

## Continuous Integration

### Validate Skills on PR

Create `.github/workflows/validate-skills.yml`:

```yaml
name: Validate Skills

on:
  pull_request:
    paths:
      - 'skills/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install pack2skill
        run: pip install pack2skill

      - name: Validate skill structure
        run: |
          # Find all SKILL.md files
          find skills -name "SKILL.md" | while read skill_file; do
            echo "Validating: $skill_file"

            # Check YAML frontmatter
            python -c "
            import yaml
            import sys

            with open('$skill_file', 'r') as f:
                content = f.read()

            # Extract YAML frontmatter
            if not content.startswith('---'):
                print('ERROR: Missing YAML frontmatter')
                sys.exit(1)

            parts = content.split('---', 2)
            if len(parts) < 3:
                print('ERROR: Invalid YAML frontmatter')
                sys.exit(1)

            # Parse YAML
            try:
                metadata = yaml.safe_load(parts[1])
            except Exception as e:
                print(f'ERROR: Invalid YAML: {e}')
                sys.exit(1)

            # Validate required fields
            required = ['name', 'description', 'version']
            for field in required:
                if field not in metadata:
                    print(f'ERROR: Missing required field: {field}')
                    sys.exit(1)

            # Validate name format
            name = metadata['name']
            if not name.islower() or '_' in name:
                print(f'ERROR: Invalid name format: {name}')
                print('Name must be lowercase with hyphens')
                sys.exit(1)

            # Validate description length
            desc = metadata['description']
            if len(desc) > 200:
                print(f'ERROR: Description too long ({len(desc)} > 200)')
                sys.exit(1)

            print('✓ Valid')
            "
          done
```

### Auto-Install on Release

Create `.github/workflows/release.yml`:

```yaml
name: Release Skills

on:
  release:
    types: [published]

jobs:
  package:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Create skills package
        run: |
          tar -czf team-skills-${{ github.event.release.tag_name }}.tar.gz skills/

      - name: Upload to release
        uses: actions/upload-release-asset@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          upload_url: ${{ github.event.release.upload_url }}
          asset_path: ./team-skills-${{ github.event.release.tag_name }}.tar.gz
          asset_name: team-skills-${{ github.event.release.tag_name }}.tar.gz
          asset_content_type: application/gzip
```

## Distribution

### Release Process

```bash
# 1. Tag release
git tag -a v1.0.0 -m "Release v1.0.0: Production-ready skills"
git push origin v1.0.0

# 2. Create GitHub release
gh release create v1.0.0 \
  --title "v1.0.0: Production Skills" \
  --notes "Initial stable release with 10 production-ready skills"

# 3. Team members install
git pull origin main
git checkout v1.0.0
./install-all.sh
```

### Update Process

```bash
# Team member: Update to latest skills
cd team-skills/
git pull origin main
./install-all.sh
```

## Best Practices

### 1. Organize by Category

```bash
skills/
├── development/    # Dev workflows (setup, PR creation, etc.)
├── deployment/     # Deploy workflows
├── testing/        # Testing and QA
└── documentation/  # Docs and API generation
```

### 2. Version Control Workflows

```bash
# Store workflows separately from videos
workflows/
├── workflow-name.json       # Include in git
└── workflow-name.mp4        # Exclude from git (too large)
```

### 3. Document Skill Dependencies

In REFERENCE.md:

```markdown
## Dependencies

- **Tools**: git, gh, python
- **Permissions**: GitHub write access
- **Configuration**: GitHub CLI authenticated
```

### 4. Provide Examples

Include real-world examples in SKILL.md:

```markdown
## Examples

### Creating a Python Library

Use this skill when:
- Starting a new Python library project
- Setting up consistent project structure
- Need standard tooling (pytest, black, mypy)
```

### 5. Regular Maintenance

- Review and update skills quarterly
- Remove deprecated skills
- Update documentation
- Gather team feedback

## Troubleshooting

### Skill not found after installation

**Check:**
```bash
pack2skill list
ls ~/.claude/skills/
```

**Fix:**
```bash
# Reinstall
pack2skill install team-skills/skills/my-skill/
```

### Conflicts between personal and team skills

**Issue:** Skill with same name exists

**Solution:**
```bash
# Remove old version
rm -rf ~/.claude/skills/conflicting-skill/

# Install team version
pack2skill install team-skills/skills/conflicting-skill/
```

### Large repository size

**Issue:** Repository growing too large with videos

**Solution:**
```bash
# Remove large video files from history
git filter-branch --tree-filter 'rm -f workflows/**/*.mp4' HEAD

# Or use git-lfs for large files
git lfs install
git lfs track "workflows/**/*.mp4"
```

## Next Steps

- [Generation Guide](generation.md) - Generate high-quality skills
- [API Reference](api-reference.md) - Programmatic usage
- [User Guide](USER_GUIDE.md) - Complete documentation

## Additional Resources

- [GitHub Repository](https://github.com/jmanhype/pack2skill)
- [Issue Tracker](https://github.com/jmanhype/pack2skill/issues)
- [Discussions](https://github.com/jmanhype/pack2skill/discussions)
