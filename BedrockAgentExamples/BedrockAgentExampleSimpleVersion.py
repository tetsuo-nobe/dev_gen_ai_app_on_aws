import uuid
import boto3


# Agentの定義
agent_id: str = "XXXXXXXXXX"  # Agent IDを入力
agent_alias_id: str = "XXXXXXXXXX"  # Alias IDを入力

prompt1 = "AnyCompany社の製品ID P001 の製品の情報を教えてください。"
prompt2 = "登山に興味があるのですが、日本で一番高い山は何ですか"

prompts = [prompt1,prompt2]

session_id: str = str(uuid.uuid1())
client = boto3.client("bedrock-agent-runtime")


for prompt in prompts:
    # Agentの実行
    response = client.invoke_agent(
        inputText=prompt,
        agentId=agent_id,
        agentAliasId=agent_alias_id,
        sessionId=session_id,
        enableTrace=False,
    )
    
    #Agent 実行結果の取得と表示
    #（ストリームを処理しているようなコードだが、実際はストリームのように細切れでレスポンスは返ってきていない。
    # https://repost.aws/questions/QU_jIzfKIAQHSXyPeE4JMAJg/issue-streaming-response-from-bedrock-agent
    event_stream = response["completion"]
    text = "" 
    for event in event_stream:
        if "chunk" in event:
            text += event["chunk"]["bytes"].decode("utf-8")
    print("Q: " + prompt)        
    print("A: " +text)
    print("-" * 80)
