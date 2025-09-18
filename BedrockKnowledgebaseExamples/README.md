## Rerank 使用時の留意点

1. 使用できるリージョン
    - https://docs.aws.amazon.com/ja_jp/bedrock/latest/userguide/rerank-supported.html
1. ナレッジベースに設定するロール
    - デフォルトでは bedrock:Rerank 操作や、リランク用のモデルの bedrock:invokeModel 操作は許可されていないので、下記を追加する
    - ```
      {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Sid": "BedrockKBRerank",
              "Effect": "Allow",
              "Action": [
                  "bedrock:Rerank",
                  "bedrock:invokeModel"
              ],
              "Resource": [
                  "*"
                ]
            }
        ]
      }
      ```
