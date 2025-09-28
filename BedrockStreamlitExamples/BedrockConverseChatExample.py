# streamlit run your_script.py --server.port 8080
import uuid
import json
import boto3
import streamlit as st

USER = "user"
ASSISTANT = "assistant"

# Set the model ID
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

# Inference parameters to use.
temperature = 0.5
top_k = 200

# Base inference parameters to use.
inference_config = {"temperature": temperature}

# Additional inference parameters to use.
#additional_model_fields = {"top_k": top_k}

# Setup the system prompts and messages to send to the model.
system_prompts = [{"text": "あなたは優秀なアシスタントです。質問に日本語で回答して下さい。"}]

# プロンプトをチャット履歴に加える関数
def createMessage(prompt, chat_log):
  message = {
      "role": USER,
      "content": [{"text": prompt}]
  }
  chat_log.append(message)
  return chat_log
  
accept = "application/json"
contentType = "application/json"


# セッションステートに client が無ければ初期化
if "client" not in st.session_state:
    st.session_state.client = boto3.client("bedrock-runtime")

# チャット履歴保存用のセッションを初期化
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# タイトル設定
st.title("Amazon Bedrok Converse API を使用したチャット")

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
            chat_log = createMessage(prompt,st.session_state.chat_log)
            # Bedrock への問い合わせ実行
            response = st.session_state.client.converse_stream(
              modelId=model_id,
              messages=chat_log,    # これまでの会話履歴も含めて渡す
              system=system_prompts,
              inferenceConfig=inference_config
              #additionalModelRequestFields=additional_model_fields
            )
            # 実行結果の表示
            stream = response.get('stream')
            if stream:
              for event in stream:
                if 'contentBlockDelta' in event:
                    assistant_msg += event['contentBlockDelta']['delta']['text']
                    message_placeholder.markdown(assistant_msg)
              #message_placeholder.markdown(assistant_msg)
    
    # セッションの履歴に基盤モデルの回答を追加
    st.session_state.chat_log.append( {"role": ASSISTANT,"content": [{"text": assistant_msg}]})
