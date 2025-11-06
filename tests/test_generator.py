"""Tests for skill generation."""

import pytest
from pathlib import Path
from pack2skill.core.generator import SkillGenerator, SkillFormatter


class TestSkillFormatter:
    """Test cases for SkillFormatter."""

    def test_sanitize_skill_name(self):
        """Test skill name sanitization."""
        formatter = SkillFormatter()

        assert formatter.sanitize_skill_name("My Skill") == "my-skill"
        assert formatter.sanitize_skill_name("Export_to_PDF") == "export-to-pdf"
        assert formatter.sanitize_skill_name("Test@Skill#123") == "testskill123"
        assert formatter.sanitize_skill_name("  spaced  ") == "spaced"

    def test_truncate_description(self):
        """Test description truncation."""
        formatter = SkillFormatter()

        short = "Short description"
        assert formatter.truncate_description(short) == short

        long = "A" * 250
        truncated = formatter.truncate_description(long)
        assert len(truncated) <= 200
        assert truncated.endswith("…")

    def test_format_yaml_frontmatter(self):
        """Test YAML frontmatter formatting."""
        formatter = SkillFormatter()

        yaml = formatter.format_yaml_frontmatter(
            name="test-skill",
            description="Test description",
            version="1.0.0"
        )

        assert "name: test-skill" in yaml
        assert "description: Test description" in yaml
        assert "version: 1.0.0" in yaml
        assert yaml.startswith("---")
        assert yaml.endswith("---")

    def test_format_instructions(self):
        """Test instruction formatting."""
        formatter = SkillFormatter()

        steps = [
            {"text": "First step"},
            {"text": "Second step"},
            {"text": "Third step"},
        ]

        instructions = formatter.format_instructions(steps)

        assert "## Instructions" in instructions
        assert "1. First step" in instructions
        assert "2. Second step" in instructions
        assert "3. Third step" in instructions


class TestSkillGenerator:
    """Test cases for SkillGenerator."""

    def test_generate_skill_description(self):
        """Test skill description generation."""
        generator = SkillGenerator()

        steps = [
            {"text": "Export presentation"},
            {"text": "Save as PDF"},
        ]

        description = generator.generate_skill_description(
            summary="Export to PDF",
            steps=steps
        )

        assert len(description) <= 200
        assert "export" in description.lower() or "pdf" in description.lower()

    def test_generate_skill(self, tmp_path):
        """Test complete skill generation."""
        generator = SkillGenerator()

        session_data = {
            "name": "test-workflow",
            "summary": "Test workflow for unit testing",
            "description": "A test workflow",
            "steps": [
                {"text": "Step 1", "timestamp": 1.0},
                {"text": "Step 2", "timestamp": 2.0},
            ],
        }

        skill_dir = generator.generate_skill(
            session_data=session_data,
            output_dir=tmp_path,
        )

        # Check skill structure
        assert skill_dir.exists()
        assert (skill_dir / "SKILL.md").exists()
        assert (skill_dir / "REFERENCE.md").exists()
        assert (skill_dir / "scripts").exists()
        assert (skill_dir / "scripts" / "helper.py").exists()

        # Check SKILL.md content
        skill_md = (skill_dir / "SKILL.md").read_text()
        assert "name:" in skill_md
        assert "description:" in skill_md
        assert "version:" in skill_md
        assert "Step 1" in skill_md
        assert "Step 2" in skill_md


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
