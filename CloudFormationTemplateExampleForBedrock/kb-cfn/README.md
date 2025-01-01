# Amazon Bedrock のナレッジベースを作成する AWS CloudFormation テンプレート

## 前提

1. ベクトルデータベースに Amazon OpenSearch Serverless を使用
2. データソースに Amazon S3 バケットを使用
3. 上記のリソースも併せて作成する
4. Amazon OpenSearch Serverless のコレクションのインデックスは AWS CloudFormation では作成できないのでカスタムリソースの AWS Lambda 関数から作成する
5. スタックを削除する場合は、事前にデータソースの S3 バケット内のオブジェクトを手動で全て削除する


## 参考ドキュメント

- [Examples | AWS CloudFormation ユーザーガイド](https://docs.aws.amazon.com/ja_jp/AWSCloudFormation/latest/UserGuide/aws-resource-bedrock-knowledgebase.html#aws-resource-bedrock-knowledgebase--examples)
- [AWS CloudFormation を使用した Amazon OpenSearch Serverless コレクションの作成 | Amazon OpenSearch 開発者ガイド](https://docs.aws.amazon.com/ja_jp/opensearch-service/latest/developerguide/serverless-cfn.html)
- [Knowledge Bases for Amazon Bedrock (with OpenSearch Serverless)をSAMで実装してみた](https://dev.classmethod.jp/articles/sam-knowledge-base-for-bedrock-with-oss/)