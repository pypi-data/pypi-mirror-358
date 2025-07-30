#!/usr/bin/env python3
"""Debug script to test tool generation."""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing import of tool_param_map...")
    from mcp_cldkctl.tool_param_map import TOOL_PARAM_MAP
    print(f"✅ TOOL_PARAM_MAP imported successfully with {len(TOOL_PARAM_MAP)} items")
    
    print("\nTesting first few tool names:")
    for i, tool_name in enumerate(list(TOOL_PARAM_MAP.keys())[:5]):
        print(f"  {i+1}. {tool_name}")
    
    print("\nTesting get_tool_definitions function...")
    from mcp_cldkctl.server import get_tool_definitions
    tools = get_tool_definitions()
    print(f"✅ Generated {len(tools)} tools successfully")
    
    print("\nFirst few generated tools:")
    for i, tool in enumerate(tools[:5]):
        print(f"  {i+1}. {tool.name} - {tool.description}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 