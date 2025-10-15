import threading
import time
from datetime import timedelta

from mcp import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamablehttp_client
from mcp.server import FastMCP
from strands import Agent
from strands.tools.mcp import MCPClient


def create_streamable_http_transport():
    return streamablehttp_client("http://localhost:8000/mcp")


streamable_http_mcp_client = MCPClient(create_streamable_http_transport)

with streamable_http_mcp_client:
    tools = streamable_http_mcp_client.list_tools_sync()

    agent = Agent(tools=tools)

    response = str(agent("ツールを使用して計算して下さい。2 + 2 は?"))
    response = str(agent("ツールを使用して長時間実行して下さい。"))
    print("\n*** END Tool ***")