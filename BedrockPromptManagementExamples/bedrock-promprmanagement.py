"""
参考：https://aws.amazon.com/jp/blogs/machine-learning/amazon-bedrock-prompt-management-is-now-available-in-ga/
"""
import boto3
import json

# Set up the Bedrock client
bedrock = boto3.client("bedrock-runtime")

"""

Prompt management : demo-cooking-advisor で定義したプロンプト

System instructions
あなたは料理の専門家です。料理についてアドバイスを提示して下さい。
User message
以下の料理を作りたいです。 料理名: {{menu}} 人数: {{servings}} 上記の料理に必要な材料、分量、おいしく作るコツを日本語で教えてください。
"""

menu = "親子丼"
servings = "4"

# Example API call
response = bedrock.converse(
    modelId="arn:aws:bedrock:us-east-1:123456789012:prompt/ZFH0XPQ9JM:3",
    promptVariables = { "menu": { "text" : menu},"servings": {"text" : servings}}
)

# Print the response	
output_message = response["output"]["message"]["content"][0]["text"]
print(output_message)