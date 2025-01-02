# AWS CloudFormation で Amazon Bedrock のナレッジベースやエージェントを作成する

- kb-cfn フォルダ
  - ナレッジベースを作成するテンプレートやカスタムリソースの AWS Lambda 関数などのリソース群
- agent-cfn フォルダ
  - エージェントを作成するテンプレートやエージェントのアクショングループの AWS Lambda 関数などのリソース群
  - kb-cfn フォルダのリソースで作成したナレッジベースを使用する