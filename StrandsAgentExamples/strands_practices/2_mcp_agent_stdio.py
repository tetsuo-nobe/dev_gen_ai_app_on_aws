import threading
import time
from datetime import timedelta

from mcp import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamablehttp_client
from mcp.server import FastMCP
from strands import Agent
from strands.tools.mcp import MCPClient


# stdioトランスポートを使用してMCPサーバーに接続
stdio_mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx", args=["awslabs.aws-documentation-mcp-server@latest"]
        )
    )
)

# MCPツールでエージェントを作成
with stdio_mcp_client:
    # MCPサーバーからツールを取得
    tools = stdio_mcp_client.list_tools_sync()

    # これらのツールを使ってエージェントを作成
    agent = Agent(tools=tools)

    response = agent("Amazon Bedrock の料金モデルとは何ですか。簡潔に説明してください。")
