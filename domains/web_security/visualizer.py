#!/usr/bin/env python3
"""
Web Security Visualizer (Deprecated)

DEPRECATED: This module has been moved to domains/_base/docker_compose_visualizer.py
to reflect its shared nature across all Docker Compose-based domains.

For backward compatibility, this file re-exports the DockerComposeVisualizer as WebSecurityVisualizer.
Please update your imports to use:
    from domains._base.docker_compose_visualizer import DockerComposeVisualizer
"""

import warnings
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domains._base.docker_compose_visualizer import DockerComposeVisualizer, NoOpVisualizer

# Backward compatibility alias
WebSecurityVisualizer = DockerComposeVisualizer

# Issue deprecation warning when this module is imported
warnings.warn(
    "domains.web_security.visualizer is deprecated. "
    "Please use domains._base.docker_compose_visualizer.DockerComposeVisualizer instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['WebSecurityVisualizer', 'NoOpVisualizer', 'DockerComposeVisualizer']
