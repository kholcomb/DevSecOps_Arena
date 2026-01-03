#!/usr/bin/env python3
"""
MCP Traffic Logger

Logs MCP protocol traffic (JSON-RPC messages) to the visualization server
for real-time display and educational highlighting of vulnerabilities.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import deque
import json
import re


class TrafficLogger:
    """
    Logs and analyzes MCP traffic for visualization.

    Responsibilities:
    - Record JSON-RPC requests and responses
    - Detect vulnerability patterns (e.g., leaked secrets)
    - Annotate traffic with educational highlights
    - Provide traffic data to visualization server
    """

    def __init__(self, max_messages: int = 1000):
        """
        Initialize traffic logger.

        Args:
            max_messages: Maximum number of messages to keep in memory
        """
        self.max_messages = max_messages
        self.traffic_log: deque = deque(maxlen=max_messages)
        self.vulnerability_patterns = self._init_vulnerability_patterns()

    def _init_vulnerability_patterns(self) -> List[Dict[str, Any]]:
        """
        Initialize vulnerability detection patterns.

        Returns:
            List of patterns with regex and vulnerability types
        """
        return [
            {
                "name": "API Key Leak",
                "pattern": r"(sk-[a-zA-Z0-9]{32,}|api_?key[:=]\s*['\"]?[a-zA-Z0-9_-]{20,})",
                "severity": "critical",
                "icon": "🚨",
                "description": "API key or secret token exposed in response"
            },
            {
                "name": "Flag Leak",
                "pattern": r"ARENA\{[^}]+\}",
                "severity": "high",
                "icon": "🏁",
                "description": "Challenge flag discovered"
            },
            {
                "name": "Password Exposure",
                "pattern": r"password[:=]\s*['\"]?[a-zA-Z0-9_@!#$%^&*]{6,}",
                "severity": "critical",
                "icon": "🔑",
                "description": "Password leaked in response"
            },
            {
                "name": "SQL Injection Attempt",
                "pattern": r"(union\s+select|or\s+1\s*=\s*1|';--)",
                "severity": "medium",
                "icon": "💉",
                "description": "Potential SQL injection payload detected"
            },
            {
                "name": "Command Injection",
                "pattern": r"(;\s*cat\s+|;\s*ls\s+|\|\s*cat\s+|\$\(.*\)|`.*`)",
                "severity": "high",
                "icon": "⚡",
                "description": "Shell command injection attempt"
            },
            {
                "name": "Path Traversal",
                "pattern": r"\.\./|\.\.\\\\",
                "severity": "medium",
                "icon": "📂",
                "description": "Path traversal attempt detected"
            }
        ]

    def log_request(self, message: Dict[str, Any], session_id: Optional[str] = None) -> str:
        """
        Log an incoming JSON-RPC request.

        Args:
            message: JSON-RPC request message
            session_id: Optional session identifier

        Returns:
            str: Log entry ID
        """
        entry_id = f"req-{datetime.now().timestamp()}"

        entry = {
            "id": entry_id,
            "type": "request",
            "direction": "client->gateway",
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "message": message,
            "method": message.get("method"),
            "vulnerabilities": self._detect_vulnerabilities(message)
        }

        self.traffic_log.append(entry)
        return entry_id

    def log_response(self, message: Dict[str, Any], request_id: Optional[str] = None,
                    session_id: Optional[str] = None) -> str:
        """
        Log an outgoing JSON-RPC response.

        Args:
            message: JSON-RPC response message
            request_id: Corresponding request ID
            session_id: Optional session identifier

        Returns:
            str: Log entry ID
        """
        entry_id = f"res-{datetime.now().timestamp()}"

        entry = {
            "id": entry_id,
            "type": "response",
            "direction": "gateway->client",
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "request_id": request_id,
            "message": message,
            "is_error": "error" in message,
            "vulnerabilities": self._detect_vulnerabilities(message)
        }

        self.traffic_log.append(entry)
        return entry_id

    def _detect_vulnerabilities(self, message: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect vulnerability patterns in a message.

        Args:
            message: JSON-RPC message to analyze

        Returns:
            List of detected vulnerabilities with metadata
        """
        # Convert message to string for pattern matching
        message_str = json.dumps(message, indent=2)

        detected = []

        for pattern_info in self.vulnerability_patterns:
            matches = re.finditer(pattern_info["pattern"], message_str, re.IGNORECASE)
            for match in matches:
                detected.append({
                    "name": pattern_info["name"],
                    "severity": pattern_info["severity"],
                    "icon": pattern_info["icon"],
                    "description": pattern_info["description"],
                    "matched_text": match.group(0)[:100],  # Limit match length
                    "position": {
                        "start": match.start(),
                        "end": match.end()
                    }
                })

        return detected

    def get_recent_traffic(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent traffic entries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of traffic entries (most recent first)
        """
        entries = list(self.traffic_log)
        return entries[-limit:][::-1]  # Return last N, reversed

    def get_traffic_since(self, timestamp: str) -> List[Dict[str, Any]]:
        """
        Get traffic entries since a specific timestamp.

        Args:
            timestamp: ISO format timestamp

        Returns:
            List of traffic entries after timestamp
        """
        target_time = datetime.fromisoformat(timestamp)

        return [
            entry for entry in self.traffic_log
            if datetime.fromisoformat(entry["timestamp"]) > target_time
        ]

    def get_vulnerability_summary(self) -> Dict[str, Any]:
        """
        Get summary of detected vulnerabilities.

        Returns:
            dict: Vulnerability counts and recent examples
        """
        vuln_counts = {}
        recent_vulns = []

        for entry in self.traffic_log:
            for vuln in entry.get("vulnerabilities", []):
                vuln_name = vuln["name"]
                vuln_counts[vuln_name] = vuln_counts.get(vuln_name, 0) + 1

                # Keep recent examples
                if len(recent_vulns) < 10:
                    recent_vulns.append({
                        "timestamp": entry["timestamp"],
                        "type": vuln_name,
                        "severity": vuln["severity"],
                        "description": vuln["description"],
                        "entry_id": entry["id"]
                    })

        return {
            "total_messages": len(self.traffic_log),
            "vulnerabilities_detected": sum(vuln_counts.values()),
            "vulnerability_counts": vuln_counts,
            "recent_vulnerabilities": recent_vulns
        }

    def get_traffic_stats(self) -> Dict[str, Any]:
        """
        Get overall traffic statistics.

        Returns:
            dict: Traffic statistics including message counts and types
        """
        request_count = sum(1 for e in self.traffic_log if e["type"] == "request")
        response_count = sum(1 for e in self.traffic_log if e["type"] == "response")
        error_count = sum(1 for e in self.traffic_log if e.get("is_error", False))

        methods = {}
        for entry in self.traffic_log:
            if entry["type"] == "request" and entry.get("method"):
                method = entry["method"]
                methods[method] = methods.get(method, 0) + 1

        return {
            "total_messages": len(self.traffic_log),
            "requests": request_count,
            "responses": response_count,
            "errors": error_count,
            "methods": methods,
            "vulnerabilities": self.get_vulnerability_summary()
        }

    def clear_log(self):
        """Clear all traffic log entries."""
        self.traffic_log.clear()
