# streamlit run your_script.py --server.port 8080
#  Bedrock Agent の Memory や LangChain の Memory モジュールを使わない前提

import uuid

import boto3
import streamlit as st

USER = "user"
ASSISTANT = "assistant"

# Agentの定義
agent_id: str = "XXXXXXXXXX"  # Agent IDを入力
agent_alias_id: str = "XXXXXXXXXX"  # Alias IDを入力


# セッションステートに client が無ければ初期化
if "client" not in st.session_state:
    st.session_state.client = boto3.client("bedrock-agent-runtime")
    
# セッションステートに session_id が無ければ初期化
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

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
            enableTrace=False,
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
