# 必要に応じて事前に pip install boto3 を実行
import boto3
import json
import base64
# Bedrock Runtime クライアントを作成
client = boto3.client("bedrock-runtime", 
                      region_name="us-east-1", 
                     )
LITE_MODEL_ID = "us.amazon.nova-lite-v1:0"

# 画像を S3 バケットから取得する場合
messages_s3 = [
    {
        "role": "user",
        "content": [
            {
                "image": {
                    "format": "jpeg",
                    "source": {
                        "s3Location": {
                            # 画像を保存している s3 バケットの URI (https://tnobep-images-us-east-1.s3.us-east-1.amazonaws.com/cat.jpg)
                            "uri": "s3://tnobep-images-us-east-1/cat.jpg"
                        }
                    },
                }
            },
            {"text": "次の画像について説明してください。"},
        ],
    }
]

# 画像を ローカルから取得する場合
# Invoke API の場合は Base64-encoded string、Converse API の場合は Binary array
with open("cherry.jpg", "rb") as image_file:
    binary_data = image_file.read()

messages_local= [
    {
        "role": "user",
        "content": [
            {
                "image": {
                    "format": "jpeg",
                    "source": {
                         "bytes": binary_data
                    },
                }
            },
            {"text": "次の画像について説明してください。"},
        ],
    }
]

inf_params = {"maxTokens": 300, "topP": 0.1, "temperature": 0.3}
model_response = client.converse(
    modelId=LITE_MODEL_ID, messages=messages_s3, inferenceConfig=inf_params
)
print("\n[Full Response]")
print(json.dumps(model_response, indent=2))
print("\n[Response Content Text]")
print(model_response["output"]["message"]["content"][0]["text"])