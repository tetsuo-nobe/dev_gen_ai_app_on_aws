# RAGAS 評価フレームワーク サンプルコード集

このフォルダには、RAGASフレームワークを使用して RAG（Retrieval-Augmented Generation）システムを評価するための Python サンプルコードが含まれています。

## 概要

RAGAS は、RAG システムの品質を定量的に評価するためのフレームワークです。このサンプル集では、Amazon Bedrock とAmazon Knowledge Bases を使用した RAG システムの評価を実装しています。

## ファイル構成

### セットアップファイル
- `requirements.txt` - 必要な Python パッケージ一覧

### メインファイル
- `1_getKBID.py` - Amazon Knowledge Base の ID を取得
- `2_invokeKB.py` - Knowledge Base を使用した RAG システムの実装
- `3_ragas.py` - 包括的な RAGAS 評価の実行

### 個別評価メトリクス
- `Faithfulness.py` - 忠実度評価（回答がコンテキストに基づいているか）
- `ContextPrecision.py` - コンテキスト精度評価（検索文書の関連性）
- `ContextRecall.py` - コンテキスト再現率評価（関連情報の網羅性）
- `ContextEntityRecall.py` - エンティティ再現率評価（特定エンティティの検索精度）
- `ResponseRelevancy.py` - 回答関連性評価（質問に対する回答の適切性）
- `NoiseSensitivity.py` - ノイズ感度評価（無関係情報の処理能力）

## 評価メトリクス

### 主要メトリクス
1. **Faithfulness** (0-1): 回答がコンテキストに忠実か
2. **Answer Relevancy** (0-1): 回答が質問に関連しているか
3. **Context Precision** (0-1): 検索されたコンテキストの精度
4. **Context Recall** (0-1): 関連情報の再現率
5. **Context Entity Recall** (0-1): エンティティの検索精度

### 参考：その他のメトリクス
- Answer Similarity: 回答の類似性
- Answer Correctness: 回答の正確性
- Harmfulness: 有害性評価
- Maliciousness: 悪意性評価
- Coherence: 一貫性評価
- Correctness: 正確性評価
- Conciseness: 簡潔性評価

## 使用技術

- **LLM**: Amazon Nova Lite (us.amazon.nova-lite-v1:0)
- **LLM**: Anthropic Claude 3 Haiku (anthropic.claude-3-haiku-20240307-v1:0-20240307-v1:0)
- **Embeddings**: Amazon Titan Embed Text v2
- **Knowledge Base**: Amazon Knowledge Bases
- **評価フレームワーク**: RAGAS v0.3.9
- **言語処理**: LangChain

## セットアップ

1. 依存関係のインストール:
```bash
pip install -r requirements.txt
```

2. AWS認証情報の設定（AWS CLIまたは環境変数）

3. Knowledge Base ID の設定:
   - `1_getKBID.py` を実行してKnowledge Base IDを取得
   - 各ファイルの `kb_id` 変数を更新

## 実行方法

### 基本的な実行順序

1. **Knowledge Base ID 取得**:
```bash
python 1_getKBID.py
```

2. **RAG システムのテスト**:
```bash
python 2_invokeKB.py
```

3. **包括的評価の実行**:
```bash
python 3_ragas.py
```

### 個別メトリクスの実行

各評価メトリクスを個別に実行:
```bash
python Faithfulness.py
python ContextPrecision.py
python ContextRecall.py
# その他のメトリクスファイル
```

## 出力

- コンソール出力: 各メトリクスのスコア
- `styled.xlsx`: 詳細な評価結果（Excel 形式）

## 注意事項

- Amazon Bedrock の利用料金が発生します
- Knowledge Base が事前に作成されている必要があります
- 評価には時間がかかる場合があります（API 制限により）
- 日本語での質問・回答に対応しています

## カスタマイズ

- `questions`配列: 評価用の質問を変更
- `ground_truth`配列: 正解データを変更
- `metrics`配列: 使用する評価メトリクスを選択
- モデル設定: 使用する LLM や Embedding モデルを変更

## トラブルシューティング

- API 制限エラー: 実行間隔を調整
- 認証エラー: AWS 認証情報を確認
- Knowledge Base接続エラー: KB ID とリージョンを確認