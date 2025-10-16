"""
Nudge Engine Module for Automated Interventions
Multi-tiered system based on idea.txt specifications
"""

from .engine import NudgeEngine, Nudge, NudgeChannel, NudgeIntensity, RiskSignal
from .templates import NudgeTemplates

__all__ = [
    'NudgeEngine', 'Nudge', 'NudgeChannel', 'NudgeIntensity', 'RiskSignal',
    'NudgeTemplates'
]