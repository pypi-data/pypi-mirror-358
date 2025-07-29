"""
MCP Log Analyzer - MCP服务器用于读取和解析gm4life.cn日志文件
"""

__version__ = "0.1.0"
__author__ = "Log Analyzer Team"

from .log_parser import LogParser, LogEntry
from .mcp_server import mcp

__all__ = ["LogParser", "LogEntry", "mcp"]