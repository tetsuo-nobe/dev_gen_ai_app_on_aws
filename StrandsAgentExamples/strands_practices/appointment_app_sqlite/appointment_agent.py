import json
import sqlite3
import uuid
from datetime import datetime

from strands import Agent, tool
from strands.models import BedrockModel

import logging

# ログレベルの指定
logging.getLogger("strands").setLevel(logging.DEBUG)

# ログハンドラの追加
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s", 
    handlers=[logging.StreamHandler()]
)

# ツールのインポート
import create_appointment
import list_appointments
import update_appointment

# 組み込みツールのインポート
from strands_tools import calculator, current_time

# システムプロンプト
system_prompt = """あなたは私の予定とカレンダーの管理を専門とする、頼りになるパーソナルアシスタントです。
予定管理ツールや計算機を利用でき、現在時刻も確認できるので、スケジュールを効率的に管理できます。
必要に応じて更新できるよう、必ず予約IDをお知らせください。"""

# Bedrock のモデル定義
model = BedrockModel(
    model_id="apac.anthropic.claude-3-7-sonnet-20250219-v1:0",
    # region_name="us-east-1",
    # boto_client_config=Config(
    #    read_timeout=900,
    #    connect_timeout=900,
    #    retries=dict(max_attempts=3, mode="adaptive"),
    # ),
    # temperature=0.9,
    # max_tokens=2048,
)

# Agent の定義
agent = Agent(
    model=model,
    system_prompt=system_prompt,
    tools=[
        current_time,
        calculator,
        create_appointment,
        list_appointments,
        update_appointment,
    ],
)

#results = agent("こんにちは。")

# results = agent(
#     "明日午後3時、ニューヨークで「エージェントの楽しみ」を予約してください。このミーティングでは、エージェントが楽しめるあらゆることについて話し合います。"
# )

results = agent(
    "明日の予定を取得して提示して下さい。"
)

# results = agent(
#     "明日の「エージェントの楽しみ」の予定ですが、場所をワシントンDCへ変更して下さい。"
# )

