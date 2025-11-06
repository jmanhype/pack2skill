# Pack2Skill Quick Start Guide

Transform your workflows into Claude Skills in 4 simple steps!

## Prerequisites

1. **Install FFmpeg:**
   ```bash
   # macOS
   brew install ffmpeg

   # Ubuntu/Debian
   sudo apt-get install ffmpeg

   # Windows: Download from ffmpeg.org
   ```

2. **Install Pack2Skill:**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

## Quick Start

### Step 1: Record Your Workflow (2 minutes)

```bash
pack2skill record --name my-first-skill
```

- The screen recorder starts automatically
- Perform your workflow slowly and clearly
- Press **Ctrl+C** when done
- Enter a brief summary when prompted

**Example:** "Export Keynote presentation to PDF"

### Step 2: Analyze the Recording (1-3 minutes)

```bash
pack2skill analyze ./recordings/my-first-skill.json
```

This will:
- Extract key frames from your video
- Generate captions describing each action
- Correlate with keyboard/mouse events
- Create structured workflow steps

**Output:** Analysis results in `./recordings/my-first-skill_analysis/`

### Step 3: Generate the Skill (< 1 minute)

```bash
pack2skill generate ./recordings/my-first-skill_analysis/session.json
```

This creates:
- `SKILL.md` - Main skill definition
- `REFERENCE.md` - Detailed documentation
- `scripts/helper.py` - Helper scripts template

**Output:** Skill folder in `./skills/my-first-skill/`

### Step 4: Install and Use (< 1 minute)

```bash
pack2skill install ./skills/my-first-skill
```

**That's it!** Your skill is now available in Claude.

## Try It Out

Open Claude and say:
> "Export my presentation to PDF"

Claude will recognize your skill and follow the recorded steps!

## Example Session

```bash
# 1. Record exporting a Keynote to PDF
$ pack2skill record --name export-keynote
Recording started... Press Ctrl+C to stop.
# [Perform workflow: File → Export → PDF → Save]
^C
Summary: Export Keynote presentation to PDF
✓ Recording saved

# 2. Analyze
$ pack2skill analyze ./recordings/export-keynote.json
Extracting frames... [##########] 8 frames
Generating captions... [##########] 8/8
✓ Analysis complete: 4 steps generated

# 3. Generate
$ pack2skill generate ./recordings/export-keynote_analysis/session.json
✓ Skill generated: ./skills/export-keynote/

# 4. Install
$ pack2skill install ./skills/export-keynote
✓ Skill installed and ready to use!
```

## What Gets Generated

Your skill folder contains:

```
export-keynote/
├── SKILL.md           # Claude reads this
│   ├── Name: export-keynote
│   ├── Description: "Use this skill when..."
│   └── Instructions: Step-by-step workflow
├── REFERENCE.md       # Detailed context
│   ├── Recording details
│   ├── OCR text from UI
│   └── Technical notes
└── scripts/
    └── helper.py      # Optional helper code
```

## Tips for Best Results

1. **Record Slowly**: Pause briefly between actions
2. **Clear UI**: Ensure buttons/menus are visible
3. **Good Summary**: Write a clear, specific summary
4. **Test First**: Try your workflow manually before recording

## Common Use Cases

- Export documents to different formats
- Generate reports from data files
- Configure software settings
- Batch file operations
- Multi-step data entry
- Automated testing workflows

## Next Steps

- Read the [User Guide](docs/USER_GUIDE.md) for advanced features
- Try the [Example Usage](examples/example_usage.py)
- Learn about [Quality Improvements](#quality-improvements)
- Share skills with your team

## Quality Improvements (Optional)

Enhance your skills with Phase 2 features:

```python
from pack2skill.quality import ConfidenceScorer, DescriptionOptimizer

# Check confidence
scorer = ConfidenceScorer()
report = scorer.generate_confidence_report(steps)
print(f"Quality: {report['recommendation']}")

# Optimize description
optimizer = DescriptionOptimizer()
better_desc = optimizer.optimize_description(summary, steps)
```

## Troubleshooting

**FFmpeg not found?**
```bash
# Verify installation
ffmpeg -version
```

**No frames extracted?**
```bash
# Try interval method instead
pack2skill analyze session.json --method interval
```

**Captions are unclear?**
```bash
# Use a different model
pack2skill analyze session.json --model "microsoft/git-large-textcaps"
```

## Get Help

- Documentation: `docs/USER_GUIDE.md`
- Examples: `examples/example_usage.py`
- Issues: [GitHub Issues](https://github.com/yourusername/pack2skill/issues)

## What's Next?

Now that you've created your first skill:

1. **Share it** with your team (`pack2skill install --global`)
2. **Version it** (use `SkillVersionManager`)
3. **Improve it** (confidence scoring, description optimization)
4. **Contribute it** to the Claude Skills ecosystem

Happy skill building! 🚀
