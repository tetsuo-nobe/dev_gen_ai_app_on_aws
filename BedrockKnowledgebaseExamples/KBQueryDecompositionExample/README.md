# Amazon Bedrock ナレッジベースのクエリ分解

* 1つのプロンプトを

* マネジメントコンソールのナレッジベースのテストでもクエリ分解を有効化できるが、正しい回答は得られない

* AWS SDK の場合は、正しい回答を得られる
    ```
    response = bedrock_agent.retrieve_and_generate(
      input={"text": prompt},
      retrieveAndGenerateConfiguration={
        "type": "KNOWLEDGE_BASE",
        "knowledgeBaseConfiguration": {
            "knowledgeBaseId": KNOWLEDGEBASE_ID,
            "modelArn": model_arn,
            # クエリ分解の設定は下記
            "orchestrationConfiguration": {
                "queryTransformationConfiguration": {"type": "QUERY_DECOMPOSITION"}
            },
        },
      },
    )
    ```
* クエリ分解を有効化しない場合は、モデル呼び出しログは２つのログエントリが作成される
    - Embed モデルを呼び出しプロンプトから Embed 値を取得する
    - cconverse API で プロンプトから基盤モデルに問い合わせる

* クエリ分解を有効化した場合は、モデル呼び出しログのエントリ数は分解された数によって変わる
    - converse API で プロンプトから基盤モデルに問い合わせる(クエリ分解の指示)
    - Embed モデルを呼び出し分解されたプロンプトから Embed 値を取得する
    - Embed モデルを呼び出し分解していないプロンプトから Embed 値を取得する
    - converse API で プロンプトから基盤モデルに問い合わせる（取得したテキストを含めての問い合わせ）
