import json
import sqlite3
import os
from strands import tool

@tool
def list_appointments() -> str:
    """
    データベースから利用可能なすべての予定を一覧表示します。

    戻り値:
      str: 利用可能な予定
    """
    # データベースが存在するかどうかを確認
    if not os.path.exists('appointments.db'):
        return "No appointment available"
    
    conn = sqlite3.connect('appointments.db')
    conn.row_factory = sqlite3.Row  # This enables column access by name
    cursor = conn.cursor()
    
    # データベースが存在するかどうかを確認
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='appointments'")
        if not cursor.fetchone():
            conn.close()
            return "No appointment available"
        
        cursor.execute("SELECT * FROM appointments ORDER BY date")
        rows = cursor.fetchall()
        
        # 行を辞書型に変換する
        appointments = []
        for row in rows:
            appointment = {
                'id': row['id'],
                'date': row['date'],
                'location': row['location'],
                'title': row['title'],
                'description': row['description']
            }
            appointments.append(appointment)
        
        conn.close()
        return json.dumps(appointments)
    
    except sqlite3.Error:
        conn.close()
        return []