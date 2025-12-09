# Bedrock Inline Agent サンプル

Amazon Bedrock の Inline Agent 機能を使用したPythonサンプルプログラムです。

## 概要

Inline Agent は、エージェントを事前に作成せずに、API呼び出し時に動的にエージェントを定義・実行できる機能です。カスタムツールやCode Interpreterを使用して、LLMに高度な機能を追加できます。

## 前提条件

- Python 3.7以上
- boto3ライブラリ
- AWS認証情報の設定
- Amazon Bedrockへのアクセス権限

```bash
pip install boto3
```

## サンプルプログラム

### 1. inline_agent_code_interpreier.py

**概要**: Code Interpreterツールを使用して数学計算を実行するサンプル

**機能**:
- Amazon Bedrockの組み込みCode Interpreterツールを使用
- 複雑な数学計算（累乗計算など）をPythonコードで実行
- トレース情報の出力

**重要な注意点**:
- **リージョン制限**: `us-east-1` または `us-west-2` のみサポート
- **instruction**: 40文字以上必須

**実行例**:
```bash
python inline_agent_code_interpreier.py
```

**使用例**:
```python
input_text = "3.14 を 0.12345乗した値を計算して下さい。"
```

---

### 2. inline_agent_custom_tool.py

**概要**: カスタムツール（Python関数）を動的にエージェントに組み込むサンプル

**機能**:
- Python関数を自動的にBedrockエージェント用のツールスキーマに変換
- 複数のカスタムツールを同時に使用可能
- ツール実行結果をエージェントにフィードバックして最終回答を生成
- 型アノテーションとdocstringから自動的にスキーマを生成

**カスタムツール例**:
- `add(a: int, b: int)`: 2つの数値を足し算
- `get_product(product_id: str)`: 製品情報を取得

**実行例**:
```bash
python inline_agent_custom_tool.py
```

**使用例**:
```python
input_text = "製品 ID が P001 の製品の情報を教えてください。"
```

**仕組み**:
1. Python関数の型アノテーションとdocstringからツールスキーマを自動生成
2. エージェントがツール実行を要求（`returnControl`）
3. クライアント側で実際のPython関数を実行
4. 実行結果をエージェントに返して最終回答を生成

---

## 共通の設定項目

### instruction（エージェントへの指示）
- **最小文字数**: 40文字以上必須
- エージェントの役割や振る舞いを定義

### リージョン
- **使用可能リージョン**: `us-east-1` または `us-west-2`
- 東京リージョンでは、下記のエラーが出る
    - CodeInterpreter action cannot be specified for model

### enableTrace
- `True`: 詳細なトレース情報を出力（デバッグ用）
- `False`: トレース情報を非表示

## エラー対処

### `Invalid length for parameter instruction`
- instructionが40文字未満の場合に発生
- 解決策: instructionを40文字以上に修正

## 参考資料

- [Qiita記事: Bedrock Inline Agentの使い方](https://qiita.com/moritalous/items/5c12ca179fac7ca416c3)
- [AWS Bedrock Agent Runtime API ドキュメント](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_InvokeInlineAgent.html)

## ライセンス

サンプルコードは学習・参考用途で自由に使用できます。
