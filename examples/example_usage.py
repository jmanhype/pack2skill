#!/usr/bin/env python3
"""Example usage of Pack2Skill pipeline.

This script demonstrates the complete workflow from recording to skill generation.
"""

import json
from pathlib import Path
from pack2skill.core.recorder import WorkflowRecorder
from pack2skill.core.analyzer import FrameAnalyzer
from pack2skill.core.generator import SkillGenerator
from pack2skill.quality import ConfidenceScorer, DescriptionOptimizer, RobustnessChecker


def example_end_to_end_workflow():
    """Example: Complete workflow from recording to generation."""
    print("=== Pack2Skill Example Usage ===\n")

    # Phase 1: Recording
    print("Phase 1: Recording Workflow")
    print("-" * 40)

    recorder = WorkflowRecorder(
        output_dir=Path("./example_output/recordings"),
        framerate=12,
    )

    print("To record a workflow:")
    print("  recorder.start_recording(name='my-workflow', description='Export presentation')")
    print("  # ... perform workflow ...")
    print("  session = recorder.stop_recording(summary='Export Keynote to PDF')")
    print()

    # For this example, we'll use mock data
    mock_session = {
        "name": "export-to-pdf",
        "description": "Export presentation to PDF",
        "summary": "Export a Keynote presentation to PDF in the Reports folder",
        "video_path": "./example_output/recordings/export-to-pdf.mp4",
        "events_path": "./example_output/recordings/export-to-pdf.json",
        "steps": []
    }

    # Phase 1: Analysis
    print("Phase 1: Video Analysis")
    print("-" * 40)

    # Mock analysis results (in real usage, this would process the video)
    mock_steps = [
        {
            "timestamp": 1.2,
            "text": "Click the Export button in the File menu",
            "caption": "Clicking Export option",
            "ocr_text": "File\nExport\nPDF",
        },
        {
            "timestamp": 2.5,
            "text": "Press Cmd+Shift+S to save the file",
            "caption": "Keyboard shortcut pressed",
            "event": {"type": "keystroke", "key": "Cmd+Shift+S", "t": 2.5},
        },
        {
            "timestamp": 3.8,
            "text": "Select PDF format from the dropdown",
            "caption": "Selecting PDF format",
            "ocr_text": "Format\nPDF\nPowerPoint",
        },
        {
            "timestamp": 5.0,
            "text": "Click Save button to complete export",
            "caption": "Clicking Save",
            "ocr_text": "Cancel\nSave",
            "event": {"type": "click", "x": 450, "y": 550, "t": 5.0},
        },
    ]

    mock_session["steps"] = mock_steps

    print(f"Analysis complete: {len(mock_steps)} steps identified")
    print()

    # Phase 2: Quality Improvements
    print("Phase 2: Quality Analysis")
    print("-" * 40)

    # Confidence scoring
    confidence_scorer = ConfidenceScorer()
    scored_steps = confidence_scorer.score_steps(mock_steps)

    report = confidence_scorer.generate_confidence_report(scored_steps)
    print(f"Confidence Report:")
    print(f"  Average: {report['average_confidence']}")
    print(f"  Low confidence steps: {report['low_confidence_count']}")
    print(f"  Recommendation: {report['recommendation']}")
    print()

    # Description optimization
    desc_optimizer = DescriptionOptimizer()
    optimized_desc = desc_optimizer.optimize_description(
        summary=mock_session["summary"],
        steps=scored_steps,
    )

    print(f"Optimized Description:")
    print(f"  {optimized_desc}")
    print(f"  Length: {len(optimized_desc)}/200 chars")

    validation = desc_optimizer.validate_description(optimized_desc)
    print(f"  Valid: {validation['valid']}")
    print()

    # Robustness checking
    robustness_checker = RobustnessChecker()
    robustness = robustness_checker.check_workflow(scored_steps, mock_session)

    print(f"Robustness Check:")
    print(f"  Score: {robustness['robustness_score']}")
    print(f"  Issues found: {sum(len(v) for v in robustness['issues'].values())}")

    if robustness['recommendations']:
        print(f"  Recommendations:")
        for rec in robustness['recommendations'][:3]:
            print(f"    - {rec}")
    print()

    # Phase 1: Skill Generation
    print("Phase 1: Skill Generation")
    print("-" * 40)

    generator = SkillGenerator()

    # Update session with quality improvements
    mock_session["steps"] = scored_steps

    output_dir = Path("./example_output/skills")
    output_dir.mkdir(parents=True, exist_ok=True)

    skill_dir = generator.generate_skill(
        session_data=mock_session,
        output_dir=output_dir,
        description=optimized_desc,
        version="0.1.0",
    )

    print(f"✓ Skill generated: {skill_dir}")
    print(f"\nSkill structure:")
    print(f"  {skill_dir.name}/")
    print(f"  ├── SKILL.md")
    print(f"  ├── REFERENCE.md")
    print(f"  └── scripts/")
    print(f"      └── helper.py")
    print()

    # Show generated SKILL.md content
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        print("Generated SKILL.md:")
        print("-" * 40)
        content = skill_md.read_text()
        print(content[:500] + "..." if len(content) > 500 else content)
        print()

    print("=== Example Complete ===")
    print(f"\nTo install the skill:")
    print(f"  pack2skill install {skill_dir}")


def example_quality_analysis_only():
    """Example: Analyzing an existing session for quality."""
    print("=== Quality Analysis Example ===\n")

    # Load existing session (mock data)
    steps = [
        {
            "timestamp": 1.0,
            "text": "Click the button",
            "caption": "clicking something",
            "ocr_text": "",
        },
        {
            "timestamp": 8.5,  # Long gap
            "text": "Type the filename",
            "caption": "typing in text field",
            "ocr_text": "Filename",
        },
    ]

    # Run quality checks
    scorer = ConfidenceScorer()
    scored = scorer.score_steps(steps)

    print("Step Confidence Scores:")
    for i, step in enumerate(scored):
        print(f"  Step {i + 1}: {step['confidence']:.2f} - {step['text']}")

    report = scorer.generate_confidence_report(scored)
    print(f"\nOverall: {report['average_confidence']:.2f}")
    print(f"Recommendation: {report['recommendation']}")


if __name__ == "__main__":
    print("Pack2Skill Example Usage\n")
    print("Choose an example:")
    print("  1. Complete end-to-end workflow")
    print("  2. Quality analysis only")
    print()

    choice = input("Enter choice (1-2): ").strip()

    if choice == "1":
        example_end_to_end_workflow()
    elif choice == "2":
        example_quality_analysis_only()
    else:
        print("Running default example...")
        example_end_to_end_workflow()
