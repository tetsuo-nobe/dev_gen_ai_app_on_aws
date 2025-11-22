# Amazon Knowledge BaseのIDを取得するスクリプト
# RAGAS評価で使用するKnowledge BaseのIDを特定するために使用

import botocore
import boto3

# AWS セッションを作成
session = boto3.Session()
# Bedrock Agentクライアントを初期化
bedrock_client = session.client('bedrock-agent')

try:
    # Knowledge Baseの一覧を取得（最初の1つのみ）
    response = bedrock_client.list_knowledge_bases(
        maxResults=1  # 最初のKnowledge Baseのみ取得
    )
    knowledge_base_summaries = response.get('knowledgeBaseSummaries', [])

    # Knowledge Baseが存在する場合、IDを表示
    if knowledge_base_summaries:
        kb_id = knowledge_base_summaries[0]['knowledgeBaseId']
        print(f"Knowledge Base ID: {kb_id}")
    else:
        print("No Knowledge Base summaries found.")
        
except botocore.exceptions.ClientError as e:
    # AWS APIエラーをキャッチして表示
    print(f"Error: {e}")