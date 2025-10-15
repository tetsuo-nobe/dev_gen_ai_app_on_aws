import sqlite3
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
    if "date" in tool["input"]:
        date = tool["input"]["date"]
    else:
        date = None
    if "location" in tool["input"]:
        location = tool["input"]["location"]
    else:
        location = None
    if "title" in tool["input"]:
        title = tool["input"]["title"]
    else:
        title = None
    if "description" in tool["input"]:
        description = tool["input"]["description"]
    else:
        description = None
        
    # データベースが存在するかどうかを確認
    if not os.path.exists('appointments.db'): 
        return {
            "toolUseId": tool_use_id,
            "status": "error",
            "content": [{"text": f"Appointment {appointment_id} does not exist"}]
        } 
    
    # 予定が存在するかどうかを確認
    conn = sqlite3.connect('appointments.db')
    cursor = conn.cursor()
    
    # 予定テーブルが存在するかどうかを確認する
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments'")
        if not cursor.fetchone():
            conn.close()
            return {
                "toolUseId": tool_use_id,
                "status": "error",
                "content": [{"text": f"Appointments table does not exist"}]
            }
        
        cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
        appointment = cursor.fetchone()
        
        if not appointment:
            conn.close()
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
        
        # 更新クエリの構築
        update_fields = []
        params = []
        
        if date:
            update_fields.append("date = ?")
            params.append(date)
        
        if location:
            update_fields.append("location = ?")
            params.append(location)
        
        if title:
            update_fields.append("title = ?")
            params.append(title)
        
        if description:
            update_fields.append("description = ?")
            params.append(description)
        
        # 更新するフィールドがない場合
        if not update_fields:
            conn.close()
            return {
                "toolUseId": tool_use_id,
                "status": "success",
                "content": [{"text": "No need to update your appointment, you are all set!"}]
            }
        
        # クエリを完了する
        query = f"UPDATE appointments SET {', '.join(update_fields)} WHERE id = ?"
        params.append(appointment_id)
        
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        
        return {
            "toolUseId": tool_use_id,
            "status": "success",
            "content": [{"text": f"Appointment {appointment_id} updated with success"}]
        }
    
    except sqlite3.Error as e:
        conn.close()
        return {
            "toolUseId": tool_use_id,
            "status": "error",
            "content": [{"text": str(e)}]
        }