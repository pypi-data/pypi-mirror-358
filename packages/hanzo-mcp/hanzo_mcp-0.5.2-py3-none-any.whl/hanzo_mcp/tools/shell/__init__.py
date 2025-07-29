"""Shell tools package for Hanzo MCP.

This package provides tools for executing shell commands and scripts.
"""

import shutil

from fastmcp import FastMCP

from hanzo_mcp.tools.common.base import BaseTool, ToolRegistry
from hanzo_mcp.tools.common.permissions import PermissionManager
from hanzo_mcp.tools.shell.bash_session_executor import BashSessionExecutor
from hanzo_mcp.tools.shell.command_executor import CommandExecutor
from hanzo_mcp.tools.shell.run_background import RunBackgroundTool
from hanzo_mcp.tools.shell.processes import ProcessesTool
from hanzo_mcp.tools.shell.pkill import PkillTool
from hanzo_mcp.tools.shell.logs import LogsTool
from hanzo_mcp.tools.shell.uvx import UvxTool
from hanzo_mcp.tools.shell.uvx_background import UvxBackgroundTool
from hanzo_mcp.tools.shell.npx import NpxTool
from hanzo_mcp.tools.shell.npx_background import NpxBackgroundTool

# Export all tool classes
__all__ = [
    "get_shell_tools",
    "register_shell_tools",
]


def get_shell_tools(
    permission_manager: PermissionManager,
) -> list[BaseTool]:
    """Create instances of all shell tools.

    Args:
        permission_manager: Permission manager for access control

    Returns:
        List of shell tool instances
    """
    tools = []
    
    # Add platform-specific command tool
    if shutil.which("tmux") is not None:
        # Use tmux-based implementation for interactive sessions
        from hanzo_mcp.tools.shell.run_command import RunCommandTool

        command_executor = BashSessionExecutor(permission_manager)
        tools.append(RunCommandTool(permission_manager, command_executor))
    else:
        # Use Windows-compatible implementation
        from hanzo_mcp.tools.shell.run_command_windows import RunCommandTool

        command_executor = CommandExecutor(permission_manager)
        tools.append(RunCommandTool(permission_manager, command_executor))
    
    # Add other shell tools
    tools.extend([
        RunBackgroundTool(permission_manager),
        ProcessesTool(),
        PkillTool(),
        LogsTool(),
        UvxTool(permission_manager),
        UvxBackgroundTool(permission_manager),
        NpxTool(permission_manager),
        NpxBackgroundTool(permission_manager),
    ])
    
    return tools


def register_shell_tools(
    mcp_server: FastMCP,
    permission_manager: PermissionManager,
) -> list[BaseTool]:
    """Register all shell tools with the MCP server.

    Args:
        mcp_server: The FastMCP server instance
        permission_manager: Permission manager for access control

    Returns:
        List of registered tools
    """
    tools = get_shell_tools(permission_manager)
    ToolRegistry.register_tools(mcp_server, tools)
    return tools
