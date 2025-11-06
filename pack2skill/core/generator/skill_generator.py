"""Main skill generator that coordinates the generation process."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from pack2skill.core.generator.skill_formatter import SkillFormatter

logger = logging.getLogger(__name__)


class SkillGenerator:
    """Generates Claude Skills from analyzed workflow data.

    Coordinates the generation process from session data to skill folder structure.
    """

    def __init__(self, formatter: Optional[SkillFormatter] = None):
        """Initialize skill generator.

        Args:
            formatter: Optional custom formatter (uses default if None)
        """
        self.formatter = formatter or SkillFormatter()

    def load_session_data(self, session_file: Path) -> Dict[str, Any]:
        """Load session data from JSON file.

        Args:
            session_file: Path to session JSON file

        Returns:
            Session data dictionary

        Raises:
            FileNotFoundError: If session file doesn't exist
            ValueError: If session data is invalid
        """
        session_file = Path(session_file)

        if not session_file.exists():
            raise FileNotFoundError(f"Session file not found: {session_file}")

        with open(session_file, 'r') as f:
            data = json.load(f)

        # Validate required fields
        if "steps" not in data:
            raise ValueError("Session data missing 'steps' field")

        return data

    def generate_skill_description(
        self,
        summary: str,
        steps: List[Dict[str, Any]],
    ) -> str:
        """Generate an optimized skill description.

        Args:
            summary: Summary of the workflow
            steps: List of workflow steps

        Returns:
            Optimized description (≤200 chars)
        """
        # Start with summary
        description = summary

        # Add "Use this skill when..." prefix if not present
        if not any(phrase in description.lower() for phrase in ["use this", "when you", "to "]):
            # Extract key action from first step
            if steps:
                first_step = steps[0].get("text", "")
                # Simple heuristic: if first step is short enough, use it
                if len(first_step) < 50:
                    description = f"Use this skill to {first_step.lower()}"
                else:
                    description = f"Use this skill when you need to {summary.lower()}"

        # Truncate to 200 chars
        description = self.formatter.truncate_description(description, max_length=200)

        return description

    def generate_skill(
        self,
        session_data: Dict[str, Any],
        output_dir: Path,
        skill_name: Optional[str] = None,
        description: Optional[str] = None,
        version: str = "0.1.0",
        allowed_tools: Optional[List[str]] = None,
        create_scripts: bool = True,
    ) -> Path:
        """Generate a complete Claude Skill from session data.

        Args:
            session_data: Workflow session data with steps
            output_dir: Directory to create skill folder in
            skill_name: Optional custom skill name
            description: Optional custom description
            version: Semantic version string
            allowed_tools: Optional list of allowed tools
            create_scripts: Whether to create helper scripts folder

        Returns:
            Path to generated skill folder
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Extract data
        steps = session_data.get("steps", [])
        summary = session_data.get("summary", "Recorded workflow")

        # Generate skill name
        if skill_name is None:
            skill_name = session_data.get("name", summary)

        skill_id = self.formatter.sanitize_skill_name(skill_name)

        # Generate description
        if description is None:
            description = self.generate_skill_description(summary, steps)

        # Create skill folder
        skill_dir = output_dir / skill_id
        skill_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Generating skill: {skill_id}")
        logger.info(f"Output directory: {skill_dir}")

        # Generate SKILL.md
        skill_md_content = self.formatter.generate_skill_md(
            name=skill_id,
            description=description,
            steps=steps,
            summary=summary,
            version=version,
            allowed_tools=allowed_tools,
        )

        skill_md_path = skill_dir / "SKILL.md"
        skill_md_path.write_text(skill_md_content)
        logger.info(f"Created: {skill_md_path}")

        # Generate REFERENCE.md
        reference_md_content = self.formatter.generate_reference_md(
            steps=steps,
            session_metadata=session_data,
        )

        reference_md_path = skill_dir / "REFERENCE.md"
        reference_md_path.write_text(reference_md_content)
        logger.info(f"Created: {reference_md_path}")

        # Create scripts directory with helper
        if create_scripts:
            scripts_dir = skill_dir / "scripts"
            scripts_dir.mkdir(exist_ok=True)

            helper_script = self.formatter.create_helper_script(skill_id)
            helper_path = scripts_dir / "helper.py"
            helper_path.write_text(helper_script)
            logger.info(f"Created: {helper_path}")

        logger.info(f"Skill generated successfully: {skill_dir}")

        return skill_dir

    def generate_from_session_file(
        self,
        session_file: Path,
        output_dir: Path,
        **kwargs,
    ) -> Path:
        """Generate skill from a session JSON file.

        Args:
            session_file: Path to session JSON file
            output_dir: Directory to create skill in
            **kwargs: Additional arguments for generate_skill

        Returns:
            Path to generated skill folder
        """
        session_data = self.load_session_data(session_file)
        return self.generate_skill(session_data, output_dir, **kwargs)

    def batch_generate(
        self,
        session_files: List[Path],
        output_dir: Path,
        **kwargs,
    ) -> List[Path]:
        """Generate multiple skills from session files.

        Args:
            session_files: List of session JSON file paths
            output_dir: Directory to create skills in
            **kwargs: Additional arguments for generate_skill

        Returns:
            List of paths to generated skill folders
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        generated = []

        for session_file in session_files:
            logger.info(f"\nProcessing: {session_file}")
            try:
                skill_dir = self.generate_from_session_file(
                    session_file=session_file,
                    output_dir=output_dir,
                    **kwargs,
                )
                generated.append(skill_dir)
            except Exception as e:
                logger.error(f"Failed to generate skill from {session_file}: {e}")

        logger.info(f"\nGenerated {len(generated)}/{len(session_files)} skills")

        return generated

    def update_skill(
        self,
        skill_dir: Path,
        session_data: Dict[str, Any],
        increment_version: bool = True,
    ) -> Path:
        """Update an existing skill with new session data.

        Args:
            skill_dir: Path to existing skill folder
            session_data: New workflow session data
            increment_version: Whether to increment version number

        Returns:
            Path to updated skill folder

        Raises:
            FileNotFoundError: If skill doesn't exist
        """
        skill_dir = Path(skill_dir)

        if not skill_dir.exists():
            raise FileNotFoundError(f"Skill directory not found: {skill_dir}")

        skill_md_path = skill_dir / "SKILL.md"

        if not skill_md_path.exists():
            raise FileNotFoundError(f"SKILL.md not found in {skill_dir}")

        # Read existing SKILL.md to extract metadata
        existing_content = skill_md_path.read_text()

        # Extract version (simple regex)
        import re
        version_match = re.search(r'version:\s*([0-9.]+)', existing_content)
        current_version = version_match.group(1) if version_match else "0.1.0"

        # Increment version if requested
        if increment_version:
            parts = current_version.split('.')
            parts[-1] = str(int(parts[-1]) + 1)
            new_version = '.'.join(parts)
        else:
            new_version = current_version

        # Extract name
        name_match = re.search(r'name:\s*([^\n]+)', existing_content)
        skill_name = name_match.group(1).strip() if name_match else skill_dir.name

        # Regenerate skill
        return self.generate_skill(
            session_data=session_data,
            output_dir=skill_dir.parent,
            skill_name=skill_name,
            version=new_version,
        )
