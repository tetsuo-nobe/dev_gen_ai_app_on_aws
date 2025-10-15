import boto3
from ddb import client as client
from ddb import table_name as table_name
from datetime import datetime
import os
from strands.types.tools import ToolResult, ToolUse
from typing import Any

TOOL_SPEC = {
    "name": "update_appointment",
    "description": "予定ID に基づいて予定を更新します。",
    "inputSchema": {
        "json": {
            "type": "object",
            "properties": {
                "appointment_id": {
                    "type": "string",
                    "description": "予定ID"
                },
                "date": {
                    "type": "string",
                    "description": "予定日時 (format: YYYY-MM-DD HH:MM)."
                },
                "location": {
                    "type": "string",
                    "description": "予定場所"
                },
                "title": {
                    "type": "string",
                    "description": "予定のタイトル"
                },
                "description": {
                    "type": "string",
                    "description": "予定の説明"
                }
            },
            "required": ["appointment_id"]
        }
    }
}
# 関数名はツール名と一致する必要があります
def update_appointment(tool: ToolUse, **kwargs: Any) -> ToolResult:
    tool_use_id = tool["toolUseId"]
    appointment_id = tool["input"]["appointment_id"]
        
    # 予定が存在するかどうかを確認する
    try:
        res = client.get_item(TableName = table_name,   Key = {"id": {"S": appointment_id}})
        # 存在している場合は、更新する属性を用意する
        if "Item" in res:
                if "date" in tool["input"]:
                    date = tool["input"]["date"]
                else:
                    date = res["Item"]["date"]["S"]
                if "location" in tool["input"]:
                    location = tool["input"]["location"]
                else:
                    location = res["Item"]["location"]["S"]
                if "title" in tool["input"]:
                    title = tool["input"]["title"]
                else:
                    title = res["Item"]["title"]["S"]
                if "description" in tool["input"]:
                    description = tool["input"]["description"]
                else:
                    description = res["Item"]["description"]["S"]
        else: # 存在していない場合はエラー
            return {
                "toolUseId": tool_use_id,
                "status": "error",
                "content": [{"text": f"Appointment {appointment_id} does not exist"}]
            }
        
        # 日付形式が指定されている場合は検証する
        if date:
            try:
                datetime.strptime(date, '%Y-%m-%d %H:%M')
            except ValueError:
                conn.close()
                return {
                    "toolUseId": tool_use_id,
                    "status": "error",
                    "content": [{"text": "Date must be in format 'YYYY-MM-DD HH:MM'"}]
                }
        
        # 更新
        item = {
            "id":            {"S": appointment_id},
            "title":         {"S": title},
            "date":          {"S": date},
            "location":      {"S": location},
            "description":   {"S": description}
        }
        client.put_item(TableName=table_name, Item=item)
        
        return {
            "toolUseId": tool_use_id,
            "status": "success",
            "content": [{"text": f"Appointment {appointment_id} updated with success"}]
        }
    
    except Exception as e:
        return {
            "toolUseId": tool_use_id,
            "status": "error",
            "content": [{"text": str(e)}]
        }