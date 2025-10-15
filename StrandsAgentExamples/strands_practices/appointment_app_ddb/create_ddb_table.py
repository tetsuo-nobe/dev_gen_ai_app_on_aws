import boto3
import botocore
from ddb  import table_name

# テーブルを作成する関数
def create_score_table():
    ddbClient = boto3.client('dynamodb')
    # テーブル作成
    table = ddbClient.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )
    waiter = ddbClient.get_waiter('table_exists') # テーブル作成完了まで待機
    waiter.wait(TableName=table_name) 
    response = ddbClient.describe_table(
        TableName=table_name
    )
    return response

# ここから実行開始
if __name__ == '__main__':
    try:
        response = create_score_table()
        print("Table status:", response['Table']['TableStatus'])
    except botocore.exceptions.ClientError as err:
        print(err.response['Error']['Message'])
    except botocore.exceptions.ParamValidationError as error:
        print(error)  