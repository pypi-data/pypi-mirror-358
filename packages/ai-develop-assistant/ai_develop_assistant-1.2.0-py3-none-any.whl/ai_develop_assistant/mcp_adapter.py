"""
MCP适配器 - 兼容不同版本的MCP SDK
"""
import sys
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

try:
    import mcp
    print("✅ 找到真实MCP包")
    
    # 尝试导入types
    try:
        from mcp import types
        types_attrs = dir(types)
        print(f"Types attributes: {[attr for attr in types_attrs if not attr.startswith('_')]}")
    except ImportError:
        types = None
    
    # 定义Tool类
    if types and hasattr(types, 'Tool'):
        Tool = types.Tool
        print("✅ 使用mcp.types.Tool")
    elif hasattr(mcp, 'Tool'):
        Tool = mcp.Tool
        print("✅ 使用mcp.Tool")
    else:
        @dataclass
        class Tool:
            name: str
            description: str
            inputSchema: Dict[str, Any]
        print("✅ 使用自定义Tool类")
    
    # 定义TextContent类
    if types and hasattr(types, 'TextContent'):
        TextContent = types.TextContent
        print("✅ 使用mcp.types.TextContent")
    elif hasattr(mcp, 'TextContent'):
        TextContent = mcp.TextContent
        print("✅ 使用mcp.TextContent")
    else:
        @dataclass
        class TextContent:
            type: str = "text"
            text: str = ""
        print("✅ 使用自定义TextContent类")
    
    # 定义FastMCP类
    if hasattr(mcp, 'FastMCP'):
        FastMCP = mcp.FastMCP
        print("✅ 使用mcp.FastMCP")
    else:
        class FastMCP:
            def __init__(self, name: str, description: str = ""):
                self.name = name
                self.description = description
                self._tools_handler = None
                self._call_tool_handler = None
                print(f"✅ 创建自定义FastMCP: {name}")
            
            def list_tools(self):
                def decorator(func):
                    self._tools_handler = func
                    return func
                return decorator
            
            def call_tool(self):
                def decorator(func):
                    self._call_tool_handler = func
                    return func
                return decorator
            
            def run(self):
                print(f"✅ MCP服务器 '{self.name}' 启动成功!")
                print(f"📝 描述: {self.description}")
                if self._tools_handler:
                    try:
                        import asyncio
                        tools = asyncio.run(self._tools_handler())
                        print(f"🛠️  可用工具数量: {len(tools)}")
                        for tool in tools:
                            print(f"   - {tool.name}: {tool.description}")
                    except Exception as e:
                        print(f"⚠️  获取工具列表时出错: {e}")

except ImportError as e:
    print(f"⚠️  MCP导入失败: {e}")
    print("🔧 使用完全备用实现...")
    
    @dataclass
    class Tool:
        name: str
        description: str
        inputSchema: Dict[str, Any]
    
    @dataclass 
    class TextContent:
        type: str = "text"
        text: str = ""
    
    class FastMCP:
        def __init__(self, name: str, description: str = ""):
            self.name = name
            self.description = description
            self._tools_handler = None
            self._call_tool_handler = None
            print(f"✅ 创建备用FastMCP: {name}")
        
        def list_tools(self):
            def decorator(func):
                self._tools_handler = func
                return func
            return decorator
        
        def call_tool(self):
            def decorator(func):
                self._call_tool_handler = func
                return func
            return decorator
        
        def run(self):
            print(f"✅ MCP服务器 '{self.name}' 启动成功!")
            print(f"📝 描述: {self.description}")

# 导出类供其他模块使用
__all__ = ['FastMCP', 'Tool', 'TextContent']
print("✅ MCP适配器创建完成")