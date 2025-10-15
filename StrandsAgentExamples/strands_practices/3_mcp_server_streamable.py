import threading
import time
from datetime import timedelta

from mcp import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamablehttp_client
from mcp.server import FastMCP
from strands import Agent
from strands.tools.mcp import MCPClient


# MCPサーバーの作成
mcp = FastMCP("Calculator Server")

# ツールの定義


@mcp.tool(description="計算を実行する計算ツール")
def calculator(x: int, y: int) -> int:
    print("----- called calculator -----")
    return x + y


@mcp.tool(description="長時間実行されるツール")
def long_running_tool(name: str) -> str:
    print("----- called long_running_tool -----")
    time.sleep(25)
    return f"Hello {name}"


def main():
    mcp.run(transport="streamable-http", mount_path="mcp")


thread = threading.Thread(target=main)
thread.start()