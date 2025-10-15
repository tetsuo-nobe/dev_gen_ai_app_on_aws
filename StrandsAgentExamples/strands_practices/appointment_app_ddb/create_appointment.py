import json
import boto3
import uuid
from datetime import datetime
from ddb import client as client
from ddb import table_name as table_name
import os
from strands import tool

@tool
def create_appointment(date: str, location: str, title: str, description: str) -> str:
    """
    データベースに新しい個人用予定を作成します。

    引数:
      date (str): 予定の日時 (形式: YYYY-MM-DD HH:MM)
      location (str): 予定の場所
      title (str): 予定のタイトル
      description (str): 予定の説明

    戻り値:
      str: 新しく作成された予定のID

    例外:
      ValueError: 日付の形式が無効な場合
    """
    # 日付フォーマットを検証
    try:
        datetime.strptime(date, "%Y-%m-%d %H:%M")
    except ValueError:
        raise ValueError("Date must be in format 'YYYY-MM-DD HH:MM'")

    # 一意のIDを生成
    appointment_id = str(uuid.uuid4())
    # DynamoDB テーブルへ putItem
    try:
        item = {
            "id":            {"S": appointment_id},
            "title":         {"S": title},
            "date":          {"S": date},
            "location":      {"S": location},
            "description":   {"S": description}
        }
        client.put_item(TableName=table_name, Item=item)
        return f"Appointment with id {appointment_id} created"
    except Exception as e:
      print(f"予期しないエラーが発生しました: {e}")
      return f"予期しないエラーが発生しました: {e}"
    