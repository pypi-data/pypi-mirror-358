# cli.py

"""命令行接口，用于启动MCP服务器"""

import argparse
from .server import run_server

def main():
    """命令行入口点，解析参数并启动服务器"""
    parser = argparse.ArgumentParser(description="启动国际化工作流MCP服务器")
    parser.add_argument(
        "--transport", 
        choices=["stdio", "http"], 
        default="stdio",
        help="传输方式，可选 'stdio' 或 'http'，默认为 'stdio'"
    )
    parser.add_argument(
        "--host", 
        default="127.0.0.1",
        help="HTTP服务器主机地址，仅当 transport=http 时有效，默认为 '127.0.0.1'"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="HTTP服务器端口，仅当 transport=http 时有效，默认为 8000"
    )
    
    args = parser.parse_args()
    
    if args.transport == "http":
        print(f"启动HTTP服务器，地址: {args.host}:{args.port}")
        run_server(transport="http", host=args.host, port=args.port)
    else:
        print("启动STDIO服务器")
        run_server(transport="stdio")

if __name__ == "__main__":
    main()