# streamlit run --your_script.py --server.port 8080
import uuid
import json
import boto3
import streamlit as st

USER = "user"
ASSISTANT = "assistant"

# Set the model ID
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

max_tokens = 512
temperature = 0.5
top_p = 0.9

accept = "application/json"
contentType = "application/json"

# Format the request payload using the model's native structure.
def createRequestbody(prompt,chat_log):
    # プロンプトをチャット履歴に加える
    message = {"role": USER, "content": [{"type": "text", "text": prompt}]}
    chat_log.append(message)
    
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "messages": chat_log   # 基盤モデルにはチャット履歴ごと渡す
    }
    
    # Convert the native request to JSON.
    requestBody = json.dumps(native_request)
    return requestBody


# セッションステートに client が無ければ初期化
if "client" not in st.session_state:
    st.session_state.client = boto3.client("bedrock-runtime")

# チャット履歴保存用のセッションを初期化
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# タイトル設定
st.title("Amazon Bedrok チャット")

if prompt := st.chat_input("質問を入力してください。"):
    # 以前のチャットログを表示
    for chat in st.session_state.chat_log:
        with st.chat_message(chat["role"]):
             st.write(chat["content"][0]["text"])
    
    with st.chat_message(USER):
        st.markdown(prompt)

    with st.chat_message(ASSISTANT):

        with st.spinner("回答を生成中..."):
            assistant_msg = ""
            message_placeholder = st.empty()
            body = createRequestbody(prompt,st.session_state.chat_log)
            # Bedrock への問い合わせ実行
            response = st.session_state.client.invoke_model_with_response_stream(
                body=body, modelId=model_id, accept=accept, contentType=contentType
            )
            # 実行結果の表示
            for event in response["body"]:
              chunk = json.loads(event["chunk"]["bytes"])
              if chunk["type"] == "content_block_delta":
                  assistant_msg += chunk["delta"].get("text", "")
                  message_placeholder.markdown(assistant_msg)
            message_placeholder.markdown(assistant_msg)
    
    # セッションの履歴に基盤モデルの回答を追加
    st.session_state.chat_log.append( {"role": ASSISTANT, "content": [{"type": "text", "text": assistant_msg}]})
