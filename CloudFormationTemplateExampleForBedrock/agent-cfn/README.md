# Amazon Bedrock の Agent を作成する AWS CloudFormation テンプレート

## 前提

1. ナレッジベース 1 つとアクショングループ 1 つを使用する
2. ナレッジベースは作成済
3. アクショングループの Lambda 関数も併せて作成する
4. アクショングループの Lambda 関数は、簡素化されたスキーマ(関数の詳細)を使用する

## メモ

- スタック作成時に下記のようなエラーが出た場合は、設定している値に問題がある。
  - #/ActionGroups/0/FunctionSchema/Functions/0/Name: failed validation constraint for keyword [pattern]
- 例えば、空白が入っている、規定の命名規則に従っていないなどが原因である可能性がある

## 参考ドキュメント

- [AWS::Bedrock::Agent | AWS CloudFormation ユーザーガイド](https://docs.aws.amazon.com/ja_jp/AWSCloudFormation/latest/UserGuide/aws-resource-bedrock-agent.html)
- [Amazon Bedrock のアクション、リソース、条件キー | Service Authorization Reference](https://docs.aws.amazon.com/ja_jp/service-authorization/latest/reference/list_amazonbedrock.html#amazonbedrock-knowledge-base)
- [Agents for Amazon BedrockをCloudFormationでデプロイするときのポイント](https://qiita.com/hayao_k/items/0764c64cdeaedc67d11e)