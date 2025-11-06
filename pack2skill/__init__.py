"""Pack2Skill: Transform workflows into Claude Skills automatically."""

__version__ = "0.1.0"
__author__ = "Pack2Skill Team"

from pack2skill.core.recorder import WorkflowRecorder
from pack2skill.core.analyzer import FrameAnalyzer
from pack2skill.core.generator import SkillGenerator

__all__ = [
    "WorkflowRecorder",
    "FrameAnalyzer",
    "SkillGenerator",
    "__version__",
]
