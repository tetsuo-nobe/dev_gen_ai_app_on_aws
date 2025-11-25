import boto3
import json

# リージョンとプロンプトルーターARNを設定
region_name = "us-west-2"

# 作成したプロンプトルーターの ARN Nova Liteと、フォールバックモデルに Nova Pro を指定。応答品質の差 10%)
prompt_router_arn = "arn:aws:bedrock:us-west-2:330174381929:prompt-router/sjd2v3c5xird"

# 作成したプロンプトルーターは、PlayGround からも選択可能

# Bedrock Runtimeクライアントをセットアップ
client = boto3.client("bedrock-runtime", region_name=region_name)

def ask_question(question):
    """
    指定された質問をプロンプトルーターに送信し、応答を取得する関数
    """
    response = client.converse(
        modelId=prompt_router_arn,
        messages=[
            {
                "role": "user",
                "content": [{"text": question}],
            }
        ],
        inferenceConfig={
            "temperature": 0.1,
            "topP": 0.9,
            "maxTokens": 1000,
            "stopSequences":[]
        }
    )
    
    # レスポンスを取得
    answer_text = response["output"]["message"]["content"][0]["text"]
    
    # 使用されたモデルIDを取得
    model_id = "不明"
    try:
        if 'trace' in response and 'promptRouter' in response['trace'] and 'invokedModelId' in response['trace']['promptRouter']:
            full_model_id = response['trace']['promptRouter']['invokedModelId']
            if "inference-profile" in full_model_id:
                model_id = full_model_id.split("inference-profile")[1]
            else:
                model_id = full_model_id
    except Exception as e:
        model_id = f"取得できませんでした（エラー: {str(e)}）"
    
    return answer_text, model_id

def main():
    # ユーザーからの質問を受け付ける
    user_question = input("質問を入力してください: ")

    # シンプルな質問: 日本の首都はどこですか？ ---> Nova Lite
    # 複雑な質問:  数学にて0で除算できない理由を中学生でもわかるように説明して下さい。 ---> Nova Pro (フォールバックモデル)
    
    # 質問を送信して応答を取得
    answer, model = ask_question(user_question)
    
    # 結果を表示
    print("\n=== 回答 ===")
    print(answer)
    print(f"\n使用されたモデル: {model}")

if __name__ == "__main__":
    main()
