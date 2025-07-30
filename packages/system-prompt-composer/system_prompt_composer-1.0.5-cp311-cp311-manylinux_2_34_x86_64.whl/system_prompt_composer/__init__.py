"""
System Prompt Composer - A modular system prompt composition framework

This package provides intelligent system prompt generation based on available MCP tools,
task complexity, and session state. It helps create more effective AI assistants by
applying proven prompt engineering patterns automatically.

All prompt guidance is loaded from transparent markdown files that developers can
read, understand, and customize.

Example usage:
    import json
    from system_prompt_composer import compose_system_prompt
    
    # Prepare request
    request = {
        "user_prompt": "Look at config.json and fix any issues",
        "mcp_config": {
            "mcpServers": {
                "desktop-commander": {
                    "name": "desktop-commander", 
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-filesystem"]
                }
            }
        },
        "session_state": {
            "tool_call_count": 0
        }
    }
    
    # Generate optimized system prompt with built-in prompts
    response = compose_system_prompt(json.dumps(request))
    result = json.loads(response)
    system_prompt = result["system_prompt"]
    
    # Or use custom prompts directory
    response = compose_system_prompt_with_prompts_dir(
        json.dumps(request), 
        "/path/to/custom/prompts"
    )
"""

import os
from ._system_prompt_composer import (
    compose_system_prompt_with_prompts_dir as _compose_system_prompt_with_prompts_dir,
    compose_system_prompt_cached_with_prompts_dir as _compose_system_prompt_cached_with_prompts_dir,
    refresh_server_tools,
    get_status
)

__version__ = "1.0.5"

# Get the path to the built-in prompts directory
_BUILTIN_PROMPTS_DIR = os.path.join(os.path.dirname(__file__), 'prompts')

def compose_system_prompt(request_json):
    """
    Compose a system prompt using the built-in prompt library.
    
    Args:
        request_json (str): JSON string containing the request configuration
        
    Returns:
        str: JSON string containing the composed system prompt
    """
    return _compose_system_prompt_with_prompts_dir(request_json, _BUILTIN_PROMPTS_DIR)

def compose_system_prompt_with_prompts_dir(request_json, prompts_dir):
    """
    Compose a system prompt using a custom prompts directory.
    
    Args:
        request_json (str): JSON string containing the request configuration
        prompts_dir (str): Path to custom prompts directory
        
    Returns:
        str: JSON string containing the composed system prompt
    """
    return _compose_system_prompt_with_prompts_dir(request_json, prompts_dir)

def compose_system_prompt_cached(request_json):
    """
    Compose a system prompt using the built-in prompt library with caching.
    
    Args:
        request_json (str): JSON string containing the request configuration
        
    Returns:
        str: JSON string containing the composed system prompt
    """
    return _compose_system_prompt_cached_with_prompts_dir(request_json, _BUILTIN_PROMPTS_DIR)

def compose_system_prompt_cached_with_prompts_dir(request_json, prompts_dir):
    """
    Compose a system prompt using a custom prompts directory with caching.
    
    Args:
        request_json (str): JSON string containing the request configuration
        prompts_dir (str): Path to custom prompts directory
        
    Returns:
        str: JSON string containing the composed system prompt
    """
    return _compose_system_prompt_cached_with_prompts_dir(request_json, prompts_dir)

__all__ = [
    "compose_system_prompt", 
    "compose_system_prompt_with_prompts_dir",
    "compose_system_prompt_cached", 
    "compose_system_prompt_cached_with_prompts_dir",
    "refresh_server_tools",
    "get_status"
]
