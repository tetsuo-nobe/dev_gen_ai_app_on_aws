import uuid
import boto3


# Agentの定義
agent_id: str = "3BHIQQCNYN"  # Agent IDを入力
agent_alias_id: str = "39DGJPPCAF"  # Alias IDを入力

#agent_id: str = "PICA38JHA3"  # 0817B
#agent_alias_id: str = "U5WNZGTHJH"  # 0817B v2

prompt1 = "AnyCompany社の最新情報を教えてください。"
prompt2 = "AnyCompany社では、6か月以上勤務した場合に与えられる有給休暇は何日ですか？"
prompt3 = "日本で一番高い山は何ですか"

prompts = [prompt1,prompt2,prompt3]

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
    event_stream = response["completion"]
    text = "" 
    for event in event_stream:
        if "chunk" in event:
            text += event["chunk"]["bytes"].decode("utf-8")
    print("Q: " + prompt)        
    print("A: " +text)
    print("-" * 80)
