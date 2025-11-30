import os
import boto3

region = "us-west-2"
kb_id = "OMC53NNCFX"
client = boto3.client("bedrock-agent-runtime", region_name=region)

# 生成に使うモデルは Nova Pro とする(Nova Lite では動作しないケースがあった)
model_arn = "arn:aws:bedrock:us-west-2:330174381929:inference-profile/us.amazon.nova-pro-v1:0"

# メタデータで date が 20251203 のドキュメントのみにフィルタリングする 
filter = {"equals": {"key": "date", "value": 20251203}}

response = client.retrieve_and_generate(
    input={"text": "ロンドンウォーキングの販売における戦略地域はどこですか？"},
    retrieveAndGenerateConfiguration={
        "knowledgeBaseConfiguration": {
            "knowledgeBaseId": kb_id,
            "modelArn": model_arn,
            "retrievalConfiguration": {
                "vectorSearchConfiguration": {
                    "filter": filter,
                    "numberOfResults": 5,
                }
            },
        },
        "type": "KNOWLEDGE_BASE",
    },
)

# 回答は 「京都」だけになる。フィルターを使わないと、「大阪」や「神戸」も回答に含まれる。
print(response["output"]["text"])
