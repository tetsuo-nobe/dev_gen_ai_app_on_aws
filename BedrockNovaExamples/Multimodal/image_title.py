# 必要に応じて事前に pip install boto3 を実行
import base64
import boto3
import json

# Bedrock Runtime クライアントを作成
client = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1",
)

MODEL_ID = "us.amazon.nova-lite-v1:0"

# 使用したい画像を開き、Base64 でエンコード
with open("cherry.jpg", "rb") as image_file:
    binary_data = image_file.read()
    base_64_encoded_data = base64.b64encode(binary_data)
    base64_string = base_64_encoded_data.decode("utf-8")
    
# システムプロンプト
system_list = [    {
        "text": "あなたは熟練の芸術家です。ユーザーが画像を提供したら、その画像にふさわしいアート作品のタイトルを日本語で3つ提案してください。"
    }
]
# 画像とテキストプロンプトの両方を含むユーザーメッセージを定義
# 画像をローカルから読み込む場合
# Invoke API の場合は Base64-encoded string、Converse API の場合は Binary array
message_list = [
    {
        "role": "user",
        "content": [
            {
                "image": {
                    "format": "jpg",
                    "source": {
                        "bytes": base64_string
                    },
                }
            },
            {
                "text": "この画像にふさわしい作品タイトルを日本語で提案してください。"
            }
        ],
    }
]

# 画像を S3 バケットから取得する場合
message_list_s3 = [
    {
        "role": "user",
        "content": [
            {
                "image": {
                    "format": "jpg",
                    "source": {
                         "s3Location": {
                            # 画像を保存している s3 バケットの URI (https://tnobep-images-us-east-1.s3.us-east-1.amazonaws.com/cat.jpg)
                            "uri": "s3://tnobep-images-us-east-1/cat.jpg"
                        }
                    },
                }
            },
            {
                "text": "この画像にふさわしい作品タイトルを提案してください。"
            }
        ],
    }
]

# 推論パラメータを設定
inf_params = {"maxTokens": 300, "topP": 0.1, "topK": 20, "temperature": 0.3}

native_request = {
    "schemaVersion": "messages-v1",
    "messages": message_list,
    "system": system_list,
    "inferenceConfig": inf_params,
}

# モデルを呼び出し、レスポンスのボディを抽出
response = client.invoke_model(modelId=MODEL_ID, body=json.dumps(native_request))
model_response = json.loads(response["body"].read())

# レスポンスのJSONを整形して表示
print("[Full Response]")
print(json.dumps(model_response, indent=2))

# テキストコンテンツを出力
content_text = model_response["output"]["message"]["content"][0]["text"]
print("\n[Response Content Text]")
print(content_text)
