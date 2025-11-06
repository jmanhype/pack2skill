"""Robustness checking and edge case handling for generated skills."""

import logging
import re
from typing import List, Dict, Any, Set, Optional

logger = logging.getLogger(__name__)


class RobustnessChecker:
    """Checks and improves robustness of generated skills.

    Identifies edge cases, missing error handling, and opportunities
    for generalization.
    """

    def __init__(self):
        """Initialize robustness checker."""
        self.file_patterns = re.compile(r'["\']([^"\']+\.(pdf|txt|doc|xls|ppt|png|jpg)["\'])', re.IGNORECASE)
        self.path_patterns = re.compile(r'["\']([/\\][\w/\\]+)["\']')

    def check_workflow(
        self,
        steps: List[Dict[str, Any]],
        session_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Check workflow for robustness issues.

        Args:
            steps: List of workflow steps
            session_metadata: Optional session metadata

        Returns:
            Dictionary with issues and recommendations
        """
        issues = {
            "hardcoded_values": [],
            "missing_error_handling": [],
            "assumptions": [],
            "edge_cases": [],
        }

        recommendations = []

        # Check for hardcoded filenames
        hardcoded = self._find_hardcoded_values(steps)
        if hardcoded:
            issues["hardcoded_values"] = hardcoded
            recommendations.append(
                "Generalize hardcoded filenames - use placeholders or parameters"
            )

        # Check for missing error handling
        error_checks = self._check_error_handling(steps)
        if error_checks:
            issues["missing_error_handling"] = error_checks
            recommendations.append(
                "Add conditional steps for error handling (e.g., 'If prompted, ...')"
            )

        # Check for implicit assumptions
        assumptions = self._identify_assumptions(steps)
        if assumptions:
            issues["assumptions"] = assumptions
            recommendations.append(
                "Document prerequisites or add checks for required state"
            )

        # Identify potential edge cases
        edge_cases = self._identify_edge_cases(steps)
        if edge_cases:
            issues["edge_cases"] = edge_cases
            recommendations.append(
                "Consider edge cases and add handling steps"
            )

        return {
            "issues": issues,
            "recommendations": recommendations,
            "robustness_score": self._calculate_robustness_score(issues),
        }

    def _find_hardcoded_values(
        self,
        steps: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Find hardcoded filenames and paths in steps.

        Args:
            steps: List of workflow steps

        Returns:
            List of issues with hardcoded values
        """
        hardcoded = []

        for i, step in enumerate(steps):
            text = step.get("text", "")

            # Find file references
            file_matches = self.file_patterns.findall(text)
            if file_matches:
                hardcoded.append({
                    "step_index": i,
                    "step_text": text,
                    "values": [m[0] for m in file_matches],
                    "type": "filename",
                    "suggestion": "Use a parameter for the filename"
                })

            # Find path references
            path_matches = self.path_patterns.findall(text)
            if path_matches:
                hardcoded.append({
                    "step_index": i,
                    "step_text": text,
                    "values": path_matches,
                    "type": "path",
                    "suggestion": "Use a relative path or parameter"
                })

        return hardcoded

    def _check_error_handling(
        self,
        steps: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Check for missing error handling.

        Args:
            steps: List of workflow steps

        Returns:
            List of steps that might need error handling
        """
        issues = []

        error_keywords = ["if", "error", "fail", "cancel", "confirm", "warning"]

        # Actions that commonly need error handling
        risky_actions = [
            "save", "export", "delete", "overwrite", "replace",
            "send", "publish", "submit", "upload"
        ]

        for i, step in enumerate(steps):
            text = step.get("text", "").lower()

            # Check if this is a risky action
            is_risky = any(action in text for action in risky_actions)

            if not is_risky:
                continue

            # Check if there's error handling in this or next step
            has_error_handling = any(kw in text for kw in error_keywords)

            next_step = steps[i + 1] if i + 1 < len(steps) else None
            if next_step:
                next_text = next_step.get("text", "").lower()
                has_error_handling = has_error_handling or any(
                    kw in next_text for kw in error_keywords
                )

            if not has_error_handling:
                issues.append({
                    "step_index": i,
                    "step_text": step.get("text", ""),
                    "reason": "Action may fail or require confirmation",
                    "suggestion": "Add: 'If prompted, confirm the action' or similar"
                })

        return issues

    def _identify_assumptions(
        self,
        steps: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Identify implicit assumptions in the workflow.

        Args:
            steps: List of workflow steps

        Returns:
            List of identified assumptions
        """
        assumptions = []

        # Common assumptions
        assumption_patterns = [
            {
                "keywords": ["file", "document", "open"],
                "assumption": "A specific file must be open",
                "suggestion": "Add step: 'Open the target file'"
            },
            {
                "keywords": ["menu", "toolbar", "button"],
                "assumption": "UI element is visible/accessible",
                "suggestion": "Ensure the application is in the correct view/mode"
            },
            {
                "keywords": ["folder", "directory", "location"],
                "assumption": "Specific directory exists",
                "suggestion": "Verify directory exists or create it"
            },
        ]

        for i, step in enumerate(steps):
            text = step.get("text", "").lower()

            for pattern in assumption_patterns:
                if any(kw in text for kw in pattern["keywords"]):
                    # Check if assumption is documented in previous steps
                    is_documented = False

                    for j in range(i):
                        prev_text = steps[j].get("text", "").lower()
                        if any(kw in prev_text for kw in pattern["keywords"]):
                            is_documented = True
                            break

                    if not is_documented:
                        assumptions.append({
                            "step_index": i,
                            "assumption": pattern["assumption"],
                            "suggestion": pattern["suggestion"],
                        })
                        break  # One assumption per step

        return assumptions

    def _identify_edge_cases(
        self,
        steps: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Identify potential edge cases.

        Args:
            steps: List of workflow steps

        Returns:
            List of potential edge cases
        """
        edge_cases = []

        # Common edge case scenarios
        scenarios = [
            {
                "keywords": ["export", "save as"],
                "case": "File already exists",
                "suggestion": "Handle overwrite confirmation"
            },
            {
                "keywords": ["delete", "remove"],
                "case": "Item doesn't exist",
                "suggestion": "Check if item exists first"
            },
            {
                "keywords": ["search", "find"],
                "case": "No results found",
                "suggestion": "Handle empty search results"
            },
            {
                "keywords": ["connect", "login"],
                "case": "Authentication failure",
                "suggestion": "Handle failed authentication"
            },
        ]

        for i, step in enumerate(steps):
            text = step.get("text", "").lower()

            for scenario in scenarios:
                if any(kw in text for kw in scenario["keywords"]):
                    edge_cases.append({
                        "step_index": i,
                        "edge_case": scenario["case"],
                        "suggestion": scenario["suggestion"],
                    })

        return edge_cases

    def _calculate_robustness_score(
        self,
        issues: Dict[str, List],
    ) -> float:
        """Calculate overall robustness score.

        Args:
            issues: Dictionary of issues by category

        Returns:
            Score from 0-1 (1 = most robust)
        """
        # Weight different issue types
        weights = {
            "hardcoded_values": 0.15,
            "missing_error_handling": 0.35,
            "assumptions": 0.25,
            "edge_cases": 0.25,
        }

        total_penalty = 0.0

        for category, issue_list in issues.items():
            if category in weights:
                # Each issue reduces score
                penalty = len(issue_list) * weights[category] * 0.2
                total_penalty += min(penalty, weights[category])

        score = max(0.0, 1.0 - total_penalty)
        return round(score, 2)

    def generate_improved_steps(
        self,
        steps: List[Dict[str, Any]],
        issues: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate improved steps with robustness fixes.

        Args:
            steps: Original workflow steps
            issues: Issues identified by check_workflow

        Returns:
            Improved steps with additional error handling and generalization
        """
        improved_steps = []

        for i, step in enumerate(steps):
            # Add original step
            improved_steps.append(step.copy())

            # Check if this step has issues
            # Add error handling after risky operations
            for error_issue in issues["issues"].get("missing_error_handling", []):
                if error_issue["step_index"] == i:
                    # Add error handling step
                    improved_steps.append({
                        "text": "If prompted for confirmation, review and confirm the action",
                        "timestamp": step.get("timestamp", 0) + 0.1,
                        "generated": True,
                        "reason": "Added for robustness"
                    })

        return improved_steps

    def generalize_step_text(self, text: str) -> str:
        """Generalize step text by removing specific values.

        Args:
            text: Original step text

        Returns:
            Generalized step text
        """
        # Replace specific filenames with placeholders
        text = self.file_patterns.sub(r'"<filename>"', text)

        # Replace specific paths
        text = self.path_patterns.sub(r'"<path>"', text)

        # Replace specific numbers that might be IDs or counts
        text = re.sub(r'\b\d{3,}\b', '<number>', text)

        return text
