"""Optimize skill descriptions for better Claude triggering."""

import logging
import re
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class DescriptionOptimizer:
    """Optimizes skill descriptions for Claude Skills.

    Generates concise, trigger-friendly descriptions under 200 characters
    that help Claude know when to use the skill.
    """

    MAX_LENGTH = 200

    def __init__(self):
        """Initialize description optimizer."""
        pass

    def generate_candidates(
        self,
        summary: str,
        steps: List[Dict[str, Any]],
        count: int = 5,
    ) -> List[str]:
        """Generate multiple description candidates.

        Args:
            summary: Workflow summary
            steps: List of workflow steps
            count: Number of candidates to generate

        Returns:
            List of candidate descriptions
        """
        candidates = []

        # Extract key actions from steps
        key_actions = self._extract_key_actions(steps)

        # Template 1: "Use this skill when..."
        if summary:
            candidates.append(f"Use this skill when you need to {summary.lower()}")

        # Template 2: "When you want to... this skill helps"
        if summary:
            candidates.append(f"When you want to {summary.lower()}, this skill helps")

        # Template 3: Action-based
        if key_actions:
            action_phrase = ", ".join(key_actions[:3])
            candidates.append(f"Automates: {action_phrase}")

        # Template 4: Goal-oriented
        if summary and key_actions:
            first_action = key_actions[0] if key_actions else "complete the task"
            candidates.append(
                f"{summary.capitalize()}. Starts by {first_action.lower()}"
            )

        # Template 5: Direct purpose
        if steps:
            first_step = steps[0].get("text", "")
            if first_step:
                candidates.append(
                    f"Workflow that {first_step.lower()}"
                )

        # Filter and truncate all candidates
        candidates = [
            self.truncate(c) for c in candidates
            if c and len(c) <= self.MAX_LENGTH
        ]

        return candidates[:count]

    def optimize_description(
        self,
        summary: str,
        steps: List[Dict[str, Any]],
        keywords: Optional[List[str]] = None,
    ) -> str:
        """Generate an optimized skill description.

        Args:
            summary: Workflow summary
            steps: List of workflow steps
            keywords: Optional important keywords to include

        Returns:
            Optimized description string (≤200 chars)
        """
        # Generate candidates
        candidates = self.generate_candidates(summary, steps)

        # Score and select best
        best = self._select_best_description(
            candidates=candidates,
            keywords=keywords or [],
        )

        return best

    def _extract_key_actions(
        self,
        steps: List[Dict[str, Any]],
        max_actions: int = 5,
    ) -> List[str]:
        """Extract key actions from workflow steps.

        Args:
            steps: List of workflow steps
            max_actions: Maximum number of actions to extract

        Returns:
            List of key action phrases
        """
        actions = []

        for step in steps[:max_actions * 2]:  # Look at more steps
            text = step.get("text", "")

            # Extract verb phrases (simple heuristic)
            # Look for action verbs at the start
            action_verbs = [
                "click", "press", "type", "select", "open", "close",
                "save", "export", "import", "create", "delete", "edit",
                "copy", "paste", "cut", "move", "rename", "search",
            ]

            for verb in action_verbs:
                if text.lower().startswith(verb):
                    # Extract the action phrase
                    # Take first sentence/clause
                    action = text.split('.')[0].split(',')[0]
                    if len(action) < 50:
                        actions.append(action)
                    break

            if len(actions) >= max_actions:
                break

        return actions

    def _select_best_description(
        self,
        candidates: List[str],
        keywords: List[str],
    ) -> str:
        """Select the best description from candidates.

        Args:
            candidates: List of candidate descriptions
            keywords: Important keywords that should be present

        Returns:
            Best description
        """
        if not candidates:
            return "Automated workflow skill"

        # Score each candidate
        scored = []

        for desc in candidates:
            score = 0.0

            # Favor descriptions that include keywords
            keyword_matches = sum(
                1 for kw in keywords
                if kw.lower() in desc.lower()
            )
            score += keyword_matches * 2.0

            # Favor descriptions with "when" or "use this"
            if any(phrase in desc.lower() for phrase in ["when you", "use this"]):
                score += 1.5

            # Slightly favor shorter descriptions (more concise)
            length_ratio = len(desc) / self.MAX_LENGTH
            if length_ratio < 0.8:
                score += (0.8 - length_ratio) * 0.5

            # Penalize very short descriptions
            if len(desc) < 30:
                score -= 1.0

            scored.append((score, desc))

        # Sort by score and return best
        scored.sort(reverse=True, key=lambda x: x[0])

        return scored[0][1]

    def truncate(self, text: str, max_length: int = MAX_LENGTH) -> str:
        """Truncate text to maximum length at word boundary.

        Args:
            text: Text to truncate
            max_length: Maximum length

        Returns:
            Truncated text with ellipsis if needed
        """
        if len(text) <= max_length:
            return text

        # Truncate at word boundary
        truncated = text[:max_length - 1]
        last_space = truncated.rfind(' ')

        if last_space > 0:
            truncated = truncated[:last_space]

        return truncated + "…"

    def enhance_with_context(
        self,
        description: str,
        app_name: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> str:
        """Enhance description with application or domain context.

        Args:
            description: Base description
            app_name: Application name (e.g., "Keynote", "Excel")
            domain: Domain/category (e.g., "PDF", "email")

        Returns:
            Enhanced description
        """
        # Add app context if not already mentioned
        if app_name and app_name.lower() not in description.lower():
            # Try to fit it in
            addition = f" in {app_name}"
            if len(description + addition) <= self.MAX_LENGTH:
                description += addition

        # Add domain context if not already mentioned
        if domain and domain.lower() not in description.lower():
            addition = f" for {domain}"
            if len(description + addition) <= self.MAX_LENGTH:
                description += addition

        return self.truncate(description)

    def validate_description(self, description: str) -> Dict[str, Any]:
        """Validate a description and provide feedback.

        Args:
            description: Description to validate

        Returns:
            Validation result with issues and suggestions
        """
        issues = []
        suggestions = []

        # Check length
        if len(description) > self.MAX_LENGTH:
            issues.append(f"Too long ({len(description)} chars, max {self.MAX_LENGTH})")
            suggestions.append("Shorten the description to fit 200 character limit")

        if len(description) < 20:
            issues.append("Too short - may not provide enough context")
            suggestions.append("Add more detail about when to use this skill")

        # Check for trigger phrases
        trigger_phrases = ["when you", "use this", "to ", "for ", "helps you"]
        has_trigger = any(phrase in description.lower() for phrase in trigger_phrases)

        if not has_trigger:
            issues.append("Missing trigger phrase")
            suggestions.append("Add 'use this when...' or similar to help Claude know when to invoke")

        # Check for vague language
        vague_terms = ["something", "anything", "stuff", "things"]
        if any(term in description.lower() for term in vague_terms):
            issues.append("Contains vague language")
            suggestions.append("Be more specific about what the skill does")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "length": len(description),
        }
