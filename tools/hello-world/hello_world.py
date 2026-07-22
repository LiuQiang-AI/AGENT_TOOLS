#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Hello World 示例工具"""

def run(state, **kwargs):
    """执行 hello world 工具"""
    name = kwargs.get("name", "World")
    
    # 获取 ToolResult
    if hasattr(state, "ToolResult"):
        ToolResult = state.ToolResult
    else:
        try:
            from agent.core.types_def import ToolResult
        except ImportError:
            class ToolResult:
                def __init__(self, success, output, error=None):
                    self.success = success
                    self.output = output
                    self.error = error
    
    message = f"Hello, {name}! Welcome to Agent Toolkit!"
    return ToolResult(success=True, output=message)
