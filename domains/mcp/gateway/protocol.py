#!/usr/bin/env python3
"""
MCP Protocol Handler

Validates MCP protocol compliance and handles JSON-RPC message format.
Implements the Model Context Protocol specification version 2025-11-25.
"""

from typing import Dict, Any, Optional, Tuple
import json


class MCPProtocolHandler:
    """
    Handles MCP protocol validation and message formatting.

    Responsibilities:
    - Validate MCP-Protocol-Version header
    - Validate JSON-RPC 2.0 message format
    - Generate error responses
    - Protocol version negotiation
    """

    SUPPORTED_VERSION = "2025-11-25"
    FALLBACK_VERSION = "2025-03-26"  # Backwards compatibility

    def validate_headers(self, headers: Dict[str, str]) -> Tuple[bool, str]:
        """
        Validate MCP protocol headers.

        Args:
            headers: HTTP request headers

        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        # Check for MCP-Protocol-Version header
        protocol_version = headers.get('MCP-Protocol-Version', '').strip()

        if not protocol_version:
            # Missing header - use fallback version
            return True, f"No version header, using fallback {self.FALLBACK_VERSION}"

        if protocol_version not in [self.SUPPORTED_VERSION, self.FALLBACK_VERSION]:
            return False, f"Unsupported protocol version: {protocol_version}"

        return True, f"Protocol version {protocol_version} OK"

    def validate_json_rpc(self, message: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate JSON-RPC 2.0 message format.

        Args:
            message: Parsed JSON message

        Returns:
            tuple[bool, str]: (is_valid, error_message)

        JSON-RPC 2.0 Spec:
        - jsonrpc: "2.0" (required)
        - method: string (required for requests)
        - params: object or array (optional)
        - id: string|number|null (required for requests, forbidden for notifications)
        """
        if not isinstance(message, dict):
            return False, "Message must be JSON object"

        # Check jsonrpc field
        if message.get('jsonrpc') != '2.0':
            return False, "jsonrpc field must be '2.0'"

        # Check message type
        is_request = 'method' in message
        is_response = 'result' in message or 'error' in message
        is_notification = is_request and 'id' not in message

        if not (is_request or is_response):
            return False, "Message must have 'method' (request/notification) or 'result'/'error' (response)"

        # Validate request/notification
        if is_request:
            if not isinstance(message.get('method'), str):
                return False, "'method' must be a string"

            # Notifications must not have id
            if is_notification and 'id' in message:
                return False, "Notifications must not have 'id' field"

            # Requests must have id
            if not is_notification and 'id' not in message:
                return False, "Requests must have 'id' field"

        return True, "Valid JSON-RPC 2.0 message"

    def create_error_response(self, error_code: int, message: str,
                            request_id: Optional[Any] = None,
                            data: Optional[Any] = None) -> Dict[str, Any]:
        """
        Generate JSON-RPC error response.

        Args:
            error_code: JSON-RPC error code
            message: Error message
            request_id: Original request ID (if available)
            data: Additional error data

        Returns:
            JSON-RPC error response dict

        Standard error codes:
        - -32700: Parse error
        - -32600: Invalid request
        - -32601: Method not found
        - -32602: Invalid params
        - -32603: Internal error
        - -32000 to -32099: Server error (custom)
        """
        error_obj = {
            "code": error_code,
            "message": message
        }

        if data is not None:
            error_obj["data"] = data

        return {
            "jsonrpc": "2.0",
            "error": error_obj,
            "id": request_id
        }

    def create_success_response(self, result: Any, request_id: Any) -> Dict[str, Any]:
        """
        Generate JSON-RPC success response.

        Args:
            result: Result data
            request_id: Original request ID

        Returns:
            JSON-RPC success response dict
        """
        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }

    def parse_message(self, raw_message: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Parse and validate raw JSON-RPC message.

        Args:
            raw_message: Raw JSON string

        Returns:
            tuple[bool, Optional[dict], str]: (success, parsed_message, error_message)
        """
        try:
            message = json.loads(raw_message)
        except json.JSONDecodeError as e:
            return False, None, f"Invalid JSON: {e}"

        is_valid, validation_msg = self.validate_json_rpc(message)
        if not is_valid:
            return False, None, validation_msg

        return True, message, "OK"
