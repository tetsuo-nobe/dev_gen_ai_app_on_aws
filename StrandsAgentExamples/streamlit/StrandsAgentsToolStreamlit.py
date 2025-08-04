# 実行 streamlit run your_script.py --server.port 8082
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
from strands_tools import calculator, current_time, python_repl,shell
import os
import time
import re

nest_asyncio.apply()


USER = "user"
ASSISTANT = "assistant"

# 文字列の長さを返すツールとして定義
# 使用例: "Helloという単語の文字数を数えて"
@tool
def counter(msg: str) -> int:
    """文字列の長さ（文字数）を返します。
    
    Args:
        msg: 長さを測定したい文字列
        
    Returns:
        文字列の長さ
    """
    print(f"counter tool called with text: {msg}")
    return len(msg)

# model ID の設定
model_id = "amazon.nova-lite-v1:0"

# システムメッセージの設定
system_prompts = "あなたは優秀なアシスタントです。質問に日本語で回答して下さい。"
  
# <thinking>タグを除去する関数
def remove_thinking_tags(text):
    return re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL)

# タイプライター効果でテキストを表示する関数
def typewriter_effect(text, placeholder, delay=0.02):
    displayed_text = ""
    for char in text:
        displayed_text += char
        placeholder.markdown(displayed_text)
        time.sleep(delay)

# セッションステートに agent が無ければ初期化
if "agent" not in st.session_state:
    # Agent の作成
    agent = Agent(
      model = model_id,
      system_prompt = system_prompts,
      tools=[counter],
      callback_handler=None  # この指定がないとPrintingCallbackHandlerによりレスポンスが自動的に標準出力に表示されてしまう。
    )
    st.session_state.agent = agent

# チャット履歴保存用のセッションを初期化
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# タイトル設定
st.title("Strands Agents チャット")


if prompt := st.chat_input("質問を入力してください。"):
    # 以前のチャットログを表示（<thinking>タグを除去）
    messages: Messages = st.session_state.chat_log
    for message in messages:
        if message["content"] and "text" in message["content"][0]:
            filtered_text = remove_thinking_tags(message["content"][0]["text"])
            # <thinking>タグを除去すると Agentの回答が空になるケースもあるので、空ではない場合のみチャットに表示する。
            if  filtered_text and filtered_text.strip() != "":
                with st.chat_message(message["role"]):
                    st.write(filtered_text)


    with st.chat_message(USER):
        st.markdown(prompt)

    with st.chat_message(ASSISTANT):

        with st.spinner("回答を生成中..."):
            # Agentを同期的に呼び出し
            response = st.session_state.agent(prompt)
            
            # <thinking>タグを除去
            filtered_response = remove_thinking_tags(str(response))
            
            # タイプライター効果で表示
            message_placeholder = st.empty()
            typewriter_effect(filtered_response, message_placeholder)
    
    # セッションの履歴に基盤モデルの回答を追加
    st.session_state.chat_log = st.session_state.agent.messages