"""Format skill data into Claude Skills structure."""

import re
import textwrap
from typing import List, Dict, Any, Optional
from pathlib import Path


class SkillFormatter:
    """Formats workflow data into Claude Skill structure.

    Follows Anthropic's Claude Skills specification with YAML frontmatter
    and structured markdown content.
    """

    @staticmethod
    def sanitize_skill_name(name: str) -> str:
        """Convert a name into a valid skill identifier.

        Args:
            name: Raw skill name

        Returns:
            Sanitized skill name (lowercase, hyphenated, ≤64 chars)
        """
        # Convert to lowercase
        name = name.lower()

        # Replace spaces and underscores with hyphens
        name = re.sub(r'[\s_]+', '-', name)

        # Remove invalid characters (keep alphanumeric and hyphens)
        name = re.sub(r'[^a-z0-9-]', '', name)

        # Remove consecutive hyphens
        name = re.sub(r'-+', '-', name)

        # Trim hyphens from start and end
        name = name.strip('-')

        # Limit to 64 characters
        if len(name) > 64:
            name = name[:64].rstrip('-')

        return name or "unnamed-skill"

    @staticmethod
    def truncate_description(description: str, max_length: int = 200) -> str:
        """Truncate description to maximum length.

        Args:
            description: Original description
            max_length: Maximum length (default: 200 chars)

        Returns:
            Truncated description with ellipsis if needed
        """
        if len(description) <= max_length:
            return description

        # Truncate at word boundary
        truncated = description[:max_length - 1]
        last_space = truncated.rfind(' ')

        if last_space > 0:
            truncated = truncated[:last_space]

        return truncated + "…"

    @staticmethod
    def format_yaml_frontmatter(
        name: str,
        description: str,
        version: str = "0.1.0",
        allowed_tools: Optional[List[str]] = None,
    ) -> str:
        """Format YAML frontmatter for SKILL.md.

        Args:
            name: Skill identifier
            description: Skill description (≤200 chars)
            version: Semantic version string
            allowed_tools: Optional list of allowed tools

        Returns:
            Formatted YAML frontmatter
        """
        frontmatter = f"""---
name: {name}
description: {description}
version: {version}"""

        if allowed_tools:
            tools_yaml = "\nallowed-tools:\n"
            for tool in allowed_tools:
                tools_yaml += f"  - {tool}\n"
            frontmatter += tools_yaml.rstrip()

        frontmatter += "\n---"
        return frontmatter

    @staticmethod
    def format_instructions(steps: List[Dict[str, Any]]) -> str:
        """Format steps as numbered instructions.

        Args:
            steps: List of step dictionaries with "text" field

        Returns:
            Formatted markdown instructions
        """
        instructions = "## Instructions\n\n"

        for i, step in enumerate(steps, 1):
            text = step.get("text", "").strip()
            if text:
                instructions += f"{i}. {text}\n"

        return instructions

    @staticmethod
    def format_examples(
        summary: str,
        additional_examples: Optional[List[str]] = None,
    ) -> str:
        """Format example use cases.

        Args:
            summary: Main summary to use as first example
            additional_examples: Optional additional example prompts

        Returns:
            Formatted examples section
        """
        examples = "## Examples\n\n"
        examples += f"- {summary}\n"

        if additional_examples:
            for example in additional_examples:
                examples += f"- {example}\n"

        return examples

    @staticmethod
    def format_reference(
        steps: List[Dict[str, Any]],
        session_metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Format reference documentation with detailed context.

        Args:
            steps: List of step dictionaries
            session_metadata: Optional session metadata

        Returns:
            Formatted reference content
        """
        reference = "# Reference\n\n"
        reference += "This skill was automatically generated from a recorded workflow.\n\n"

        if session_metadata:
            reference += "## Recording Details\n\n"
            if "description" in session_metadata and session_metadata["description"]:
                reference += f"**Description:** {session_metadata['description']}\n\n"
            if "start_time" in session_metadata:
                reference += f"**Recorded:** {session_metadata['start_time']}\n\n"

        reference += "## Detailed Steps\n\n"

        for i, step in enumerate(steps, 1):
            reference += f"### Step {i}\n\n"
            reference += f"**Action:** {step.get('text', 'N/A')}\n\n"

            if step.get("timestamp"):
                reference += f"**Timestamp:** {step['timestamp']:.2f}s\n\n"

            if step.get("ocr_text"):
                reference += f"**UI Text:**\n```\n{step['ocr_text']}\n```\n\n"

        return reference

    @staticmethod
    def generate_skill_md(
        name: str,
        description: str,
        steps: List[Dict[str, Any]],
        summary: str,
        version: str = "0.1.0",
        allowed_tools: Optional[List[str]] = None,
        additional_examples: Optional[List[str]] = None,
    ) -> str:
        """Generate complete SKILL.md content.

        Args:
            name: Skill identifier
            description: Skill description
            steps: List of workflow steps
            summary: Summary for examples
            version: Version string
            allowed_tools: Optional list of allowed tools
            additional_examples: Additional example prompts

        Returns:
            Complete SKILL.md content
        """
        # Sanitize and validate inputs
        name = SkillFormatter.sanitize_skill_name(name)
        description = SkillFormatter.truncate_description(description)

        # Build content sections
        frontmatter = SkillFormatter.format_yaml_frontmatter(
            name=name,
            description=description,
            version=version,
            allowed_tools=allowed_tools,
        )

        title = f"\n\n# {name.replace('-', ' ').title()}\n\n"

        instructions = SkillFormatter.format_instructions(steps)

        examples = SkillFormatter.format_examples(summary, additional_examples)

        # Combine all sections
        content = frontmatter + title + instructions + "\n" + examples

        return content

    @staticmethod
    def generate_reference_md(
        steps: List[Dict[str, Any]],
        session_metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate REFERENCE.md content.

        Args:
            steps: List of workflow steps
            session_metadata: Optional session metadata

        Returns:
            Complete REFERENCE.md content
        """
        return SkillFormatter.format_reference(steps, session_metadata)

    @staticmethod
    def create_helper_script(skill_name: str) -> str:
        """Create a template helper script.

        Args:
            skill_name: Name of the skill

        Returns:
            Python script template content
        """
        script = f'''#!/usr/bin/env python3
"""Helper script for {skill_name} skill.

This script provides utility functions that can be called from the skill.
"""

import sys
from pathlib import Path


def main():
    """Main entry point."""
    print(f"Helper script for {skill_name}")
    # Add your helper logic here


if __name__ == "__main__":
    main()
'''
        return script
