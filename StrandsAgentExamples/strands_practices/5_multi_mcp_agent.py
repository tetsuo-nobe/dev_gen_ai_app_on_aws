import threading
import time
from datetime import timedelta

from mcp import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamablehttp_client
from mcp.server import FastMCP
from strands import Agent
from strands.tools.mcp import MCPClient

# stdioトランスポートを使用してMCPサーバーに接続
aws_docs_mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx", args=["awslabs.aws-documentation-mcp-server@latest"]
        )
    )
)

# stdioトランスポートを使用してMCPサーバーに接続する
cdk_mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(command="uvx", args=["awslabs.cdk-mcp-server@latest"])
    )
)

output = "Hello"

# MCPツールでエージェントを作成
with aws_docs_mcp_client, cdk_mcp_client:
    # MCPサーバーからツールを取得
    tools = aws_docs_mcp_client.list_tools_sync() + cdk_mcp_client.list_tools_sync()

    # これらのツールを使ってエージェントを作成
    #agent = Agent(tools=tools, max_parallel_tools=2)
    agent = Agent(tools=tools)

    response = agent(
        "Amazon Bedrock の料金モデルについて、ツールで調べて簡潔に教えてください。また、AWS CDK に関するベストプラクティスについて、ツールで調べて簡潔に提示して下さい。"
    )
    output = response

print("-" * 80)
print(output)