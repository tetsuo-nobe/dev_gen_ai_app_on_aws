import random
import boto3

# このサンプルは us-east-1 か us-west-2 を前提にしている。東京リージョンでは下記のエラーが出る
#  when calling the InvokeInlineAgent operation: CodeInterpreter action cannot be specified for model amazon.nova-lite-v1:0

client = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

random_int = random.randint(1, 100000)
session_id = f"session-id-{random_int}"
#model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
#model_id = "apac.amazon.nova-lite-v1:0"
model_id = "us.amazon.nova-lite-v1:0"


# instruction は 40文字以上でなくてはならない
instruction = "あなたは優秀なAIエージェントです。ユーザーの質問に対して丁寧かつ詳細に日本語で回答してください。"

#input_text = "京都に旅行しようと思っていますが、おすすめの観光地を3つ教えて下さい。"
input_text = "3.14 を 0.12345乗した値を計算して下さい。"

# Code Interpreter ツールの定義
code_interpreter = {
     "actionGroupName": "CodeInterpreterAction",
     "parentActionGroupSignature": "AMAZON.CodeInterpreter",
}

  
# インラインエージェントの呼出し
response = client.invoke_inline_agent(
    sessionId=session_id,
    foundationModel=model_id,
    instruction=instruction,
    inputText=input_text,
    actionGroups=[code_interpreter],   # actionGroupsはオプションだが Agent なので通常は使用する。
    enableTrace=True
)

# レスポンスの表示
for event in response["completion"]:
    if "chunk" in event:
        chunk = event["chunk"]

        print(chunk["bytes"].decode())

    # enableTrace=True を指定した場合はトレースを出力できる
    if "trace" in event:
        print(event["trace"])
