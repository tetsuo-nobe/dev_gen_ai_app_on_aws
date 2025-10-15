import boto3

# DynamoDB クライアントの作成
client = boto3.client("dynamodb")

# DynamoDB テーブル名
table_name = "appointments"