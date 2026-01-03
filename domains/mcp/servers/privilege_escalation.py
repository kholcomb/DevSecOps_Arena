#!/usr/bin/env python3
"""
Privilege Escalation MCP Server

Demonstrates MCP02:2025 - Excessive Tool Permissions & Privilege Escalation

VULNERABILITY:
This server provides overly permissive tool access without proper authorization:
- No authentication checks on sensitive admin tools
- Missing role-based access control (RBAC)
- Tools expose privileged operations to any connected client

Educational Purpose:
Teaches users to recognize and exploit missing authorization controls in MCP servers
where sensitive administrative functions are accessible without proper permission checks.
"""

from typing import Dict, Any, List
import sys
from pathlib import Path
import logging

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from base_server import VulnerableMCPServer

logger = logging.getLogger(__name__)


class PrivilegeEscalationMCPServer(VulnerableMCPServer):
    """
    MCP server with privilege escalation vulnerability (MCP02:2025).

    Intentionally lacks authorization controls on sensitive admin tools,
    allowing any connected client to execute privileged operations.
    """

    def get_server_name(self) -> str:
        """Get server name."""
        return "User Management MCP Server"

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of tools.

        Returns:
            List with user and admin tools (all accessible without auth)
        """
        return [
            {
                "name": "get_user_info",
                "description": "Get current user information",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "list_files",
                "description": "List user's files",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Directory to list (defaults to user home)"
                        }
                    }
                }
            },
            # VULNERABILITY: Admin tools exposed without authorization
            {
                "name": "create_admin_user",
                "description": "Create a new administrator account (admin only)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "Username for new admin"
                        },
                        "password": {
                            "type": "string",
                            "description": "Password for new admin"
                        }
                    },
                    "required": ["username", "password"]
                }
            },
            {
                "name": "list_all_users",
                "description": "List all system users (admin only)",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_system_flag",
                "description": "Retrieve system configuration flag (admin only)",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with intentional security vulnerabilities.

        VULNERABILITY: No authorization checks - any client can call admin tools.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool execution result (admin tools accessible without auth)
        """
        if name == "get_user_info":
            return await self._get_user_info(arguments)
        elif name == "list_files":
            return await self._list_files(arguments)
        elif name == "create_admin_user":
            # VULNERABILITY: No authorization check!
            return await self._create_admin_user(arguments)
        elif name == "list_all_users":
            # VULNERABILITY: No authorization check!
            return await self._list_all_users(arguments)
        elif name == "get_system_flag":
            # VULNERABILITY: No authorization check!
            return await self._get_system_flag(arguments)
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Unknown tool: {name}"
                }],
                "isError": True
            }

    async def _get_user_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get current user information (normal user tool).

        Args:
            arguments: Tool arguments (none)

        Returns:
            User information
        """
        return {
            "content": [{
                "type": "text",
                "text": """Current User Information:
Username: guest_user
Role: standard
Permissions: read_own_files, write_own_files
Home Directory: /home/guest_user

Hint: You are currently a standard user with limited permissions.
"""
            }]
        }

    async def _list_files(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        List user's files (normal user tool).

        Args:
            arguments: Tool arguments

        Returns:
            File listing
        """
        directory = arguments.get("directory", "/home/guest_user")

        return {
            "content": [{
                "type": "text",
                "text": f"""Files in {directory}:

- documents/
  - notes.txt
  - report.pdf
- downloads/
  - file1.zip
- README.md

You have read/write access to these files.
"""
            }]
        }

    async def _create_admin_user(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create admin user (admin tool - VULNERABLE: no auth check).

        VULNERABILITY: This tool should require admin role, but doesn't check!

        Args:
            arguments: Tool arguments (username, password)

        Returns:
            Admin user creation result
        """
        username = arguments.get("username", "")
        password = arguments.get("password", "")

        if not username or not password:
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: Both username and password are required"
                }],
                "isError": True
            }

        # VULNERABILITY: No authorization check - anyone can create admin users!
        return {
            "content": [{
                "type": "text",
                "text": f"""✅ Admin user created successfully!

Username: {username}
Role: administrator
Permissions: ALL
Created by: guest_user (UNAUTHORIZED - Security Violation!)

WARNING: This operation should be restricted to existing administrators only.
The system allowed a standard user to create an admin account - this is a privilege escalation vulnerability.

Hint: With admin access, you may be able to access system-level resources.
"""
            }]
        }

    async def _list_all_users(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        List all system users (admin tool - VULNERABLE: no auth check).

        VULNERABILITY: This tool should require admin role, but doesn't check!

        Args:
            arguments: Tool arguments (none)

        Returns:
            All system users
        """
        # VULNERABILITY: No authorization check - anyone can list all users!
        return {
            "content": [{
                "type": "text",
                "text": """System Users:

1. admin_root
   - Role: super_admin
   - Created: 2025-01-01
   - Permissions: ALL

2. guest_user
   - Role: standard
   - Created: 2025-01-02
   - Permissions: read_own_files, write_own_files

3. service_account
   - Role: service
   - Created: 2025-01-01
   - Permissions: read_system_config

WARNING: This is sensitive information that should only be accessible to administrators.
The system allowed a standard user to view all users - this is an authorization bypass.

Hint: Some tools may only be mentioned in system documentation or admin interfaces.
"""
            }]
        }

    async def _get_system_flag(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get system flag (admin tool - VULNERABLE: no auth check).

        VULNERABILITY: This tool should require admin role, but doesn't check!
        This is the challenge flag that should only be accessible to admins.

        Args:
            arguments: Tool arguments (none)

        Returns:
            System flag (challenge completion flag)
        """
        # VULNERABILITY: No authorization check - anyone can get the flag!
        return {
            "content": [{
                "type": "text",
                "text": f"""System Configuration Flag:

FLAG: {self.flag}

This flag represents sensitive system configuration that should only be
accessible to administrators. You obtained it without proper authorization,
demonstrating a privilege escalation vulnerability (MCP02:2025).

The server failed to implement proper role-based access control (RBAC),
allowing standard users to execute administrative functions.
"""
            }]
        }


# Standalone server for testing
if __name__ == "__main__":
    import asyncio

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    async def main():
        config = {
            "flag": "ARENA{MCP02_Pr1v1l3g3_3sc4l4t10n_N0_RBAC}",
            "vulnerability": {
                "missing_authorization": True,
                "no_rbac": True,
                "admin_tools_exposed": True
            }
        }

        server = PrivilegeEscalationMCPServer(config, port=9002)
        await server.start()

        print(f"🔌 Privilege Escalation MCP Server running at {server.get_url()}")
        print("🚨 VULNERABLE: Admin tools accessible without authorization!")
        print("\nTry these exploits:")
        print("1. Call get_user_info to see you're a standard user")
        print("2. Call list_all_users (should require admin, but doesn't)")
        print("3. Call create_admin_user to escalate privileges")
        print("4. Call get_system_flag to retrieve the challenge flag")
        print("\nPress Ctrl+C to stop...")

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down server...")
            await server.stop()

    asyncio.run(main())
