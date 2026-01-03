#!/usr/bin/env python3
"""
MCP Backend Servers

Vulnerable MCP server implementations for educational security challenges.
Each server demonstrates a specific OWASP MCP Top 10 vulnerability.
"""

from .base_server import VulnerableMCPServer

__all__ = ['VulnerableMCPServer']
