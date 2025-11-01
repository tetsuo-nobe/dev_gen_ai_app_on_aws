import base64
import json
import boto3

client = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1",
)
MODEL_ID = "amazon.nova-lite-v1:0"

with open('AnyCompany_IR.pdf', "rb") as file:
    doc_bytes = file.read()
messages =[
    {
    "role": "user",
    "content": [
        {
            "document": {
                "format": "pdf",
                "name": "DocumentPDFmessages",
                "source": {
                    "bytes": doc_bytes
                }
            }
        },
        {
            "text": """ドキュメントの貸借対照表の内容を確認し、特筆すべきポイントを日本語で説明して下さい。"""
        }
    ]
}

]

inf_params = {"maxTokens": 1000, "topP": 0.1, "temperature": 0.3}

model_response = client.converse(modelId=MODEL_ID, messages=messages, inferenceConfig=inf_params)

print("\n[Full Response]")
print(json.dumps(model_response, indent=2))

print("\n[Response Content Text]")
print(model_response['output']['message']['content'][0]['text'])