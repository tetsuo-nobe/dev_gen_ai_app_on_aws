
# Amazon Bedrock RAG 評価

* Bedrock にはモデル評価と RAG 評価の機能があるが、ここでは RAG 評価の機能についてまとめている。

* [ RAG 評価メトリクス | Bedrock ユーザーガイド](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-metrics.html)

## 準備

* S3 バケットを作成

    - CORS 設定をしておく
    ```
    [
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "GET",
            "PUT",
            "POST",
            "DELETE"
        ],
        "AllowedOrigins": [
            "*"
        ],
        "ExposeHeaders": [
            "Access-Control-Allow-Origin"
        ]
    }
    ]

    ```

* 作成したバケットに、データセットファイルを格納するフォルダと出力用のフォルダを作成しておく

* データセットのファイルは、jsonl 形式で、件数は1件でも評価可能
    - **JSON フォーマットはモデル評価とは異なるので注意が必要**
    - [フォーマット](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-evaluation-prompt-retrieve-generate.html)

## 設定

* 評価対象の Bedrock ナレッジベースの選択
* 下記のいずれかを選択
    - Retrieve-only  
    - Retrieval and response generation
        - 生成に使用する基盤モデル
* メトリクス
    - Quality: 下記から必要なものを選択：1 に近いほど良い 
        - Helpfulness
        - Correctness
        - Logical coherence
        - Faithfulness
        - Completeness
        - Citation precision
        - Citation coverage
    - Responsible AI: 下記から必要なものを選択: 0 近いほど良い
        - Harmfulness
        - Refusal
        - Stereotyping
* 入力データセット(S3 バケットのファイル）
* 出力先フォルダ（S3 バケットのフォルダ）


