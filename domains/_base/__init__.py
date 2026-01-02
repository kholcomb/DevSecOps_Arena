"""
DevSecOps Arena - Domain Plugin Base Classes

This package provides abstract base classes for implementing domain plugins.
Each security domain (Kubernetes, Web Security, Container Security, etc.)
implements these interfaces to integrate with the game engine.
"""

from .domain import Domain, DomainConfig, Challenge
from .deployer import ChallengeDeployer
from .validator import ChallengeValidator, BashScriptValidator
from .safety_guard import SafetyGuard, SafetyPattern, SafetySeverity, NoOpSafetyGuard
from .visualizer import DomainVisualizer, NoOpVisualizer

__all__ = [
    'Domain',
    'DomainConfig',
    'Challenge',
    'ChallengeDeployer',
    'ChallengeValidator',
    'BashScriptValidator',
    'SafetyGuard',
    'SafetyPattern',
    'SafetySeverity',
    'NoOpSafetyGuard',
    'DomainVisualizer',
    'NoOpVisualizer',
]
