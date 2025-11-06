"""Version control and management for Claude Skills."""

import logging
import re
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class SkillVersionManager:
    """Manages versioning of Claude Skills with git integration.

    Provides semantic versioning, changelog generation, and git operations.
    """

    def __init__(self, skills_repo: Optional[Path] = None):
        """Initialize version manager.

        Args:
            skills_repo: Path to skills repository (default: current directory)
        """
        self.skills_repo = Path(skills_repo) if skills_repo else Path.cwd()

    def get_current_version(self, skill_dir: Path) -> str:
        """Get current version from SKILL.md.

        Args:
            skill_dir: Path to skill directory

        Returns:
            Version string (e.g., "0.1.0")

        Raises:
            FileNotFoundError: If SKILL.md doesn't exist
            ValueError: If version not found
        """
        skill_md = skill_dir / "SKILL.md"

        if not skill_md.exists():
            raise FileNotFoundError(f"SKILL.md not found in {skill_dir}")

        content = skill_md.read_text()
        match = re.search(r'version:\s*([0-9]+\.[0-9]+\.[0-9]+)', content)

        if not match:
            raise ValueError(f"No version found in {skill_md}")

        return match.group(1)

    def increment_version(
        self,
        current_version: str,
        bump_type: str = "patch",
    ) -> str:
        """Increment version number.

        Args:
            current_version: Current version string (e.g., "0.1.0")
            bump_type: Type of version bump ("major", "minor", "patch")

        Returns:
            New version string

        Raises:
            ValueError: If version format is invalid
        """
        parts = current_version.split('.')

        if len(parts) != 3:
            raise ValueError(f"Invalid version format: {current_version}")

        major, minor, patch = map(int, parts)

        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")

        return f"{major}.{minor}.{patch}"

    def update_skill_version(
        self,
        skill_dir: Path,
        new_version: Optional[str] = None,
        bump_type: str = "patch",
        changelog_entry: Optional[str] = None,
    ) -> str:
        """Update skill version in SKILL.md.

        Args:
            skill_dir: Path to skill directory
            new_version: Explicit new version (or None to auto-increment)
            bump_type: Type of version bump if auto-incrementing
            changelog_entry: Optional changelog entry

        Returns:
            New version string
        """
        skill_md = skill_dir / "SKILL.md"

        # Get current version
        current_version = self.get_current_version(skill_dir)

        # Determine new version
        if new_version is None:
            new_version = self.increment_version(current_version, bump_type)

        # Update SKILL.md
        content = skill_md.read_text()
        updated = re.sub(
            r'version:\s*[0-9]+\.[0-9]+\.[0-9]+',
            f'version: {new_version}',
            content
        )

        skill_md.write_text(updated)

        logger.info(f"Updated {skill_dir.name}: {current_version} → {new_version}")

        # Update changelog if provided
        if changelog_entry:
            self.add_changelog_entry(
                skill_dir=skill_dir,
                version=new_version,
                entry=changelog_entry,
            )

        return new_version

    def add_changelog_entry(
        self,
        skill_dir: Path,
        version: str,
        entry: str,
    ):
        """Add entry to CHANGELOG.md.

        Args:
            skill_dir: Path to skill directory
            version: Version for this entry
            entry: Changelog entry text
        """
        changelog = skill_dir / "CHANGELOG.md"

        # Create changelog if it doesn't exist
        if not changelog.exists():
            changelog.write_text("# Changelog\n\n")

        # Read existing content
        content = changelog.read_text()

        # Add new entry
        date = datetime.now().strftime("%Y-%m-%d")
        new_entry = f"## [{version}] - {date}\n\n{entry}\n\n"

        # Insert after header
        if "# Changelog" in content:
            content = content.replace(
                "# Changelog\n\n",
                f"# Changelog\n\n{new_entry}"
            )
        else:
            content = f"# Changelog\n\n{new_entry}" + content

        changelog.write_text(content)

        logger.info(f"Added changelog entry for {version}")

    def init_git_repo(self, skills_dir: Optional[Path] = None) -> bool:
        """Initialize git repository for skills.

        Args:
            skills_dir: Directory to initialize (default: self.skills_repo)

        Returns:
            True if successful
        """
        repo_dir = Path(skills_dir) if skills_dir else self.skills_repo

        if (repo_dir / ".git").exists():
            logger.info(f"Git repository already exists: {repo_dir}")
            return True

        try:
            subprocess.run(
                ["git", "init"],
                cwd=repo_dir,
                check=True,
                capture_output=True,
            )

            logger.info(f"Initialized git repository: {repo_dir}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to initialize git repo: {e}")
            return False

    def commit_skill(
        self,
        skill_dir: Path,
        message: Optional[str] = None,
    ) -> bool:
        """Commit skill changes to git.

        Args:
            skill_dir: Path to skill directory
            message: Commit message (auto-generated if None)

        Returns:
            True if successful
        """
        if not (self.skills_repo / ".git").exists():
            logger.warning("No git repository found")
            return False

        try:
            # Get skill name
            skill_name = skill_dir.name

            # Generate message if not provided
            if message is None:
                version = self.get_current_version(skill_dir)
                message = f"Update {skill_name} to v{version}"

            # Add skill files
            subprocess.run(
                ["git", "add", str(skill_dir)],
                cwd=self.skills_repo,
                check=True,
                capture_output=True,
            )

            # Commit
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.skills_repo,
                check=True,
                capture_output=True,
            )

            logger.info(f"Committed: {message}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to commit: {e}")
            return False

    def create_version_tag(
        self,
        skill_dir: Path,
        version: Optional[str] = None,
    ) -> bool:
        """Create git tag for skill version.

        Args:
            skill_dir: Path to skill directory
            version: Version to tag (default: current version)

        Returns:
            True if successful
        """
        if version is None:
            version = self.get_current_version(skill_dir)

        skill_name = skill_dir.name
        tag = f"{skill_name}-v{version}"

        try:
            subprocess.run(
                ["git", "tag", "-a", tag, "-m", f"Release {skill_name} v{version}"],
                cwd=self.skills_repo,
                check=True,
                capture_output=True,
            )

            logger.info(f"Created tag: {tag}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create tag: {e}")
            return False

    def list_skill_versions(self, skill_name: str) -> List[str]:
        """List all git tags for a skill.

        Args:
            skill_name: Name of the skill

        Returns:
            List of version tags
        """
        try:
            result = subprocess.run(
                ["git", "tag", "-l", f"{skill_name}-v*"],
                cwd=self.skills_repo,
                check=True,
                capture_output=True,
                text=True,
            )

            tags = result.stdout.strip().split('\n')
            return [tag for tag in tags if tag]

        except subprocess.CalledProcessError:
            return []

    def generate_version_metadata(self, skill_dir: Path) -> Dict[str, Any]:
        """Generate version metadata for a skill.

        Args:
            skill_dir: Path to skill directory

        Returns:
            Dictionary with version metadata
        """
        version = self.get_current_version(skill_dir)
        skill_name = skill_dir.name

        # Get git info if available
        git_info = {}
        try:
            # Get last commit
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H|%an|%ae|%ad", "--", str(skill_dir)],
                cwd=self.skills_repo,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0 and result.stdout:
                commit_hash, author_name, author_email, date = result.stdout.strip().split('|')
                git_info = {
                    "last_commit": commit_hash[:8],
                    "last_author": author_name,
                    "last_modified": date,
                }

        except subprocess.CalledProcessError:
            pass

        return {
            "skill_name": skill_name,
            "version": version,
            "path": str(skill_dir),
            **git_info,
        }
