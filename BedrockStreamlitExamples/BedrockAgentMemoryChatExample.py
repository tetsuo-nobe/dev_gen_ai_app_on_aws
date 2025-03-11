# streamlit run your_script.py --server.port 8080
#  Bedrock の Agent のメモリを使う前提
#    https://aws.amazon.com/jp/blogs/news/agents-for-amazon-bedrock-now-support-memory-retention-and-code-interpretation-preview/
#
import uuid

import boto3
import streamlit as st

USER = "user"
ASSISTANT = "assistant"

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Agentの定義
agent_id: str = "XXXXXXXXXX"  # Agent IDを入力
agent_alias_id: str = "XXXXXXXXXX"  # Alias IDを入力:v4 Memory Option Enabled
memoryId: str = "memory-example"

# セッションステートに client が無ければ初期化
if "client" not in st.session_state:
    st.session_state.client = boto3.client("bedrock-agent-runtime")
    
# セッションステートに session_id が無ければ初期化
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

def get_memory():
    response = st.session_state.client.get_agent_memory(
        agentId=agent_id,
        agentAliasId=agent_alias_id,
        memoryId=memoryId,
        memoryType='SESSION_SUMMARY',
    )
    memory = ""
    print(response)
    for content in response['memoryContents']:
        if 'sessionSummary' in content:
            s = content['sessionSummary']
            memory += f"Session ID {s['sessionId']} from {s['sessionStartTime'].strftime(DATE_FORMAT)} to {s['sessionExpiryTime'].strftime(DATE_FORMAT)}\n"
            memory += s['summaryText'] + "\n"
    if memory == "":
        memory = "<no memory>"
    return memory


# チャット履歴保存用のセッションを初期化
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# タイトル設定
st.title("Agents for Amazon Bedrok チャット")

if prompt := st.chat_input("質問を入力してください。"):
    # 以前のチャットログを表示
    for chat in st.session_state.chat_log:
        with st.chat_message(chat["name"]):
            st.write(chat["msg"])
    
    with st.chat_message(USER):
        st.markdown(prompt)

    with st.chat_message(ASSISTANT):
        # Agentの実行
        response = st.session_state.client.invoke_agent(
            inputText=prompt,
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=st.session_state.session_id,
            memoryId=memoryId,
            enableTrace=False,
            endSession=False
        )

        # Agent 実行結果の取得と表示
        event_stream = response["completion"]
        assistant_msg = "" 
        for event in event_stream:
            if "chunk" in event:
                assistant_msg += event["chunk"]["bytes"].decode("utf-8")
        st.write(assistant_msg)
    
    # セッションにチャットログを追加
    st.session_state.chat_log.append({"name": USER, "msg": prompt})
    st.session_state.chat_log.append({"name": ASSISTANT, "msg": assistant_msg})
    
    # 
    print('--- memory の内容 --- session-id:' + st.session_state.session_id)
    print(get_memory())
