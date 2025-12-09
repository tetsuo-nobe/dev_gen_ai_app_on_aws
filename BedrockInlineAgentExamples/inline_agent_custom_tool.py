#
import json
import random
import boto3

def invoke(
    session_id: str,
    foundation_model: str,
    action_groups: list,
    instruction: str,
    input_text: str,
    enableTrace: bool = False,
):
    """カスタムツールを使用してインラインエージェントを実行する関数"""

    def generate_function_schema(func):
        """Python関数からBedrockエージェント用のスキーマを自動生成"""
        import inspect
    
        # 関数のシグネチャを取得
        sig = inspect.signature(func)
    
        # 各パラメータの型情報を抽出
        parameters = {}
        for param_name, param in sig.parameters.items():
            # 型アノテーションを取得
            param_type = (
                param.annotation.__name__
                if param.annotation != inspect.Parameter.empty
                else "any"
            )
    
            # Pythonの型をJSONスキーマの型に変換
            type_mapping = {
                "int": "integer",
                "str": "string",
                "float": "number",
                "bool": "boolean",
                "list": "array",
                "dict": "object",
            }
            json_type = type_mapping.get(param_type, param_type)
    
            # パラメータ情報を追加
            parameters[param_name] = {"type": json_type, "required": True}
    
        # Bedrockエージェント用のアクショングループスキーマを構築
        schema = {
            "actionGroupName": func.__name__,
            "functionSchema": {
                "functions": [
                    {
                        "name": func.__name__,
                        "description": func.__doc__,  # 関数のdocstringを説明として使用
                        "parameters": parameters,
                    }
                ]
            },
            "actionGroupExecutor": {"customControl": "RETURN_CONTROL"},  # 制御をクライアントに返す
        }
    
        return schema

    # 初回のエージェント呼び出し
    response = client.invoke_inline_agent(
        sessionId=session_id,
        foundationModel=foundation_model,
        actionGroups=[generate_function_schema(action) for action in action_groups],  # 各関数をスキーマに変換
        instruction=instruction,
        inputText=input_text,
        enableTrace=enableTrace,
    )

    # レスポンスを格納する変数
    chunk = []  # エージェントからの応答テキスト
    return_control = []  # ツール実行要求

    # ストリーミングレスポンスを処理
    for event in response["completion"]:
        if "chunk" in event:
            chunk.append(event["chunk"])
        if "returnControl" in event:  # エージェントがツール実行を要求
            return_control.append(event["returnControl"])
        if "trace" in event:  # トレース情報を出力
            print(event["trace"])

    # ツール実行要求がある限りループ
    while len(return_control):
        session_state = None

        # 各ツール実行要求を処理
        for r in return_control:
            invocation_id = r["invocationId"]  # 呼び出しID
            invocation_inputs = r["invocationInputs"]  # 実行するツールの情報

            # セッション状態を初期化
            session_state = {
                "invocationId": invocation_id,
                "returnControlInvocationResults": [],  # ツール実行結果を格納
            }

            # 各ツール呼び出しを実行
            for inputs in invocation_inputs:
                invocation_input = inputs["functionInvocationInput"]

                action_group = invocation_input["actionGroup"]  # アクショングループ名
                function = invocation_input["function"]  # 関数名
                parameters = invocation_input["parameters"]  # パラメータリスト

                # パラメータをディクショナリに変換
                input = {
                    parameter["name"]: parameter["value"] for parameter in parameters
                }
                # 関数名から実際の関数オブジェクトを取得するためのマッピング
                action_groups_dict = {
                    action.__name__: action for action in action_groups
                }
                # 実際のPython関数を実行
                action_result = action_groups_dict[function](**input)

                # ツール実行結果をセッション状態に追加
                session_state["returnControlInvocationResults"].append(
                    {
                        "functionResult": {
                            "actionGroup": action_group,
                            "function": function,
                            "responseBody": {
                                "TEXT": {
                                    "body": json.dumps(
                                        action_result, ensure_ascii=False
                                    )
                                }
                            },
                        }
                    }
                )

        # ツール実行結果を含めて再度エージェントを呼び出し
        response = client.invoke_inline_agent(
            sessionId=session_id,
            foundationModel=foundation_model,
            actionGroups=[generate_function_schema(action) for action in action_groups],
            instruction=instruction,
            enableTrace=enableTrace,
            inlineSessionState=session_state,  # ツール実行結果を渡す
        )

        # レスポンスをリセット
        chunk = []
        return_control = []

        # 再度ストリーミングレスポンスを処理
        for event in response["completion"]:
            if "chunk" in event:
                chunk.append(event["chunk"])
            if "returnControl" in event:  # さらにツール実行が必要な場合
                return_control.append(event["returnControl"])
            if "trace" in event:
                print(event["trace"])

    # 最終的な応答テキストを返す
    return chunk[0]["bytes"].decode()

#############################################################
# メイン処理
#############################################################

# Bedrockエージェントランタイムクライアントを初期化
client = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

# カスタムツールとして使用する add 関数を定義
def add(a: int, b: int):
    """2つの数値を足し算する"""
    return a + b

# カスタムツールとして使用する get_product関数を定義
def get_product(product_id: str) -> dict:
    """製品情報を取得する"""
    product_info = {"product_id": product_id, "name": "ロンドンウォーキング", "price": 10000}
    return product_info


# セッションIDを生成
random_int = random.randint(1, 100000)
session_id = f"session-id-{random_int}"

# エージェント設定
#model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"  # 使用するモデル
model_id = "us.amazon.nova-lite-v1:0"  # 使用するモデル
action_groups = [add, get_product]  # カスタムツールとして使用する関数のリスト
instruction = "あなたはとても優秀なAIエージェントです。ユーザーの質問に丁寧に日本語で回答してください"  # エージェントへの指示（40文字以上必要）
enableTrace = True  # トレース情報を有効化

# ユーザーからの質問
input_text = "製品 ID が P001 の製品の情報を教えてください。"

# エージェントを実行
answer = invoke(
    session_id, model_id, action_groups, instruction, input_text, enableTrace
)

# 最終的な回答を出力
print(answer)
