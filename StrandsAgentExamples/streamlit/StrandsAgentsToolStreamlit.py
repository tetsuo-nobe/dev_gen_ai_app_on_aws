# 実行 streamlit run your_script.py --server.port 8080
# 実行時に表示される Faild to detach context のエラーは下記の Bug の可能性
# https://github.com/google/adk-python/issues/1670

import uuid
import json
import boto3
import streamlit as st
import asyncio
import nest_asyncio
from strands import Agent, tool
from strands.models import BedrockModel
from strands.types.content import Messages
from strands_tools import shell
import os

nest_asyncio.apply()

# shell ツールの確認のために環境変数を設定
# プロンプト:環境変数 DEV の値を取得して表示して下さい。
os.environ["DEV"] = "true"

USER = "user"
ASSISTANT = "assistant"

# 文字カウント関数をツールとして定義
# プロンプト: 環境変数 DEV の値を取得してその文字数をカウントして下さい。
@tool
def counter(word: str, letter: str):
    return word.lower().count(letter.lower())

# model ID の設定
model_id = "amazon.nova-lite-v1:0"

# システムメッセージの設定
system_prompts = "あなたは優秀なアシスタントです。質問に日本語で回答して下さい。"
  
# ストリームからテキストを取得する関数
async def streaming(stream):
  async for event in stream:
    if "event" in event:
        text = (
        event.get("event", {})
            .get("contentBlockDelta", {})
            .get("delta", {})
            .get("text", "")
        )
        yield text
    elif "current_tool_use" in event:
        current_tool_use = event.get("current_tool_use", {})

        yield f"\n\n```\n🔧 Using tool: {current_tool_use}\n```\n\n"

# セッションステートに agent が無ければ初期化
if "agent" not in st.session_state:
    # Agent の作成
    agent = Agent(
      model = model_id,
      system_prompt = system_prompts,
      tools=[shell,counter],
      callback_handler=None  # この指定がないとPrintingCallbackHandlerによりレスポンスが自動的に標準出力に表示されてしまう。
    )
    st.session_state.agent = agent

# チャット履歴保存用のセッションを初期化
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# タイトル設定
st.title("Strands Agents チャット")


if prompt := st.chat_input("質問を入力してください。"):
    # 以前のチャットログを表示
    messages: Messages = st.session_state.chat_log
    for message in messages:
      with st.chat_message(message["role"]):
          st.write(message["content"][0]["text"])
    
    with st.chat_message(USER):
        st.markdown(prompt)

    with st.chat_message(ASSISTANT):

        with st.spinner("回答を生成中..."):
            message_placeholder = st.empty()
            # Agent への問い合わせ実行
            agent_stream = st.session_state.agent.stream_async(prompt=prompt)

            # 実行結果の表示
            st.write_stream(streaming(agent_stream))
    
    # セッションの履歴に基盤モデルの回答を追加
    st.session_state.chat_log = st.session_state.agent.messages