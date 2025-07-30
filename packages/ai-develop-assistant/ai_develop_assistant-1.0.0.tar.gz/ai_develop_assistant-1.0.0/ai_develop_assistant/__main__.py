#!/usr/bin/env python3
"""
AI开发助手MCP服务器入口点
"""

def main():
    """主入口函数"""
    from .AIDevlopStudy import mcp
    import logging
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("🚀 启动AI需求分析和设计助手")
    
    mcp.run()

if __name__ == "__main__":
    main()
