#!/usr/bin/env python3
"""
命令行入口点
"""

import sys
import argparse
from .mcp_server import run_server

def main():
    """主入口点函数"""
    parser = argparse.ArgumentParser(
        description="MCP Log Analyzer - MCP服务器用于读取和解析gm4life.cn日志文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  mcp_log_analyze                    # 启动MCP服务器
  mcp_log_analyze --help            # 显示帮助信息
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="mcp-log-analyzer 0.1.0"
    )
    
    parser.add_argument(
        "--host",
        default="localhost",
        help="服务器主机地址 (默认: localhost)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="服务器端口 (默认: 8000)"
    )
    
    args = parser.parse_args()
    
    try:
        print("正在启动MCP Log Analyzer服务器...")
        print(f"服务器地址: {args.host}:{args.port}")
        print("按 Ctrl+C 停止服务器")
        
        # 启动MCP服务器
        run_server()
        
    except KeyboardInterrupt:
        print("\n服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"启动服务器时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()