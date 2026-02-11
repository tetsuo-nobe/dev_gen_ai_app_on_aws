"""
Amazon Bedrock Structured Outputs - JSON Schemaパターン
モデルの出力をJSONスキーマに準拠させる
"""

import boto3
import json

# Bedrock Runtimeクライアントの作成
bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")

# 使用するモデルID（Claude Haiku 4.5）
MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

# サンプルの非構造化テキスト
SAMPLE_TEXT = """
# 親子丼のレシピ

## 材料
* 鶏もも肉
* 玉ねぎ
* 卵
* ご飯
* めんつゆ
* 水
* 三つ葉 
## 作り方
1. フライパンに水とめんつゆと玉ねぎを入れ、煮立ったら鶏肉を加える。
2. 中火で鶏肉に火が通るまで約3〜4分煮る。
3. 溶き卵の2/3量を円を描くように回し入れ、蓋をして弱火で約30秒煮る。
4. 残りの卵を加え、再度蓋をして10〜20秒、好みのとろとろ具合になったら火を止める。
5. 盛り付け: ご飯にのせ、お好みで三つ葉を散らす。
"""

# 抽出したいデータ構造を定義するJSONスキーマ
json_schema = {
    "type": "object",
    "properties": {
        "recipe_name": {
            "type": "string",
            "description": "レシピ名称"
        },
        "ingredients": {
            "type": "array",
            "items": {"type": "string"},
            "description": "材料"
        },
        "cooking_instructions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "調理手順"
        }, 
    },
    "required": ["recipe_name", "ingredients", "cooking_instructions"],
    "additionalProperties": False
}

def extract_structured_data():
    """非構造化テキストから構造化データを抽出する"""

    response = bedrock_runtime.converse(
        modelId=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": f"以下のレシピから情報を抽出してください：\n\n{SAMPLE_TEXT}"
                    }
                ]
            }
        ],
        # Structured Outputs の設定
        outputConfig={
            "textFormat": {
                "type": "json_schema",
                "structure": {
                    "jsonSchema": {
                        "schema": json.dumps(json_schema),
                        "name": "project_extraction",
                        "description": "レシピ"
                    }
                }
            }
        }
    )

    # レスポンスからテキストを取得
    output_text = response["output"]["message"]["content"][0]["text"]
    return json.loads(output_text)

if __name__ == "__main__":
    print("=" * 60)
    print("Amazon Bedrock Structured Outputs - JSON Schema パターン")
    print("=" * 60)
    print(f"\n使用モデル: {MODEL_ID}")
    print(f"\n--- 入力テキスト ---\n{SAMPLE_TEXT}")
    print("\n--- 抽出結果 ---")

    result = extract_structured_data()
    print(json.dumps(result, indent=2, ensure_ascii=False))
