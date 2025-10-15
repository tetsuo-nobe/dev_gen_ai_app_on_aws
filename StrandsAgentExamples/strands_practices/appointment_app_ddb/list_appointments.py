import boto3
import json
from ddb import client as client
from ddb import table_name as table_name
import os
from strands import tool

@tool
def list_appointments() -> str:
    """
    データベースから利用可能なすべての予定を一覧表示します。

    戻り値:
      str: 利用可能な予定
    """
    
    # DynamoDB テーブルから項目を取得
    try:
        res = client.scan(TableName = table_name)
        
        # DynamoDB　のレスポンスをを Python の辞書型に変換する
        appointments = []
        items = res["Items"]
        for item in items:
            appointment = {
                'id': item['id'],
                'date': item['date'],
                'location': item['location'],
                'title': item['title'],
                'description': item['description']
            }
            appointments.append(appointment)
        
        return json.dumps(appointments)
    
    except Exception:
        return []