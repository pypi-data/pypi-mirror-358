# __main__.py

"""入口点脚本，允许通过 python -m translate_mcp_server 启动MCP服务器"""

from .server import run_server

if __name__ == "__main__":
    run_server(transport='stdio')