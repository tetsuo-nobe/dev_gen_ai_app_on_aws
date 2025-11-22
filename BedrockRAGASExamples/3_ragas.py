# RAGASフレームワークを使用した包括的なRAG評価システム
# Amazon BedrockとKnowledge Basesを使用してRAGシステムの品質を定量的に評価

import boto3
import pprint
from datasets import Dataset
import time
import random
from langchain_aws import ChatBedrock
from langchain_aws import BedrockEmbeddings
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import PromptTemplate
import warnings
import logging

# 警告とログレベルの設定
warnings.filterwarnings('ignore')   # pydantic v1からv2への移行に関する警告を無視
logging.getLogger('root').setLevel(logging.CRITICAL)

from datasets import Dataset

# Knowledge Base ID（1_getKBID.pyで取得したIDを設定）
kb_id = "TOROHCUSM0"

# デバッグ用のプリティプリンター
pp = pprint.PrettyPrinter(indent=2)

# Amazon Bedrockクライアントを初期化
bedrock_client = boto3.client('bedrock-runtime')

# テキスト生成用のLLM（Nova Lite）
llm_for_text_generation = ChatBedrock(model_id="us.amazon.nova-lite-v1:0", client=bedrock_client)
# RAGAS評価用のLLM（Nova Lite）
llm_for_evaluation = ChatBedrock(model_id="us.amazon.nova-lite-v1:0", client=bedrock_client)

# Embedding用のモデル（Titan Embed Text v2）
bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0",client=bedrock_client)

# Knowledge Baseからの情報検索を行うRetriever
retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id=kb_id,
        retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 5}},  # 上位5件を取得
        # endpoint_url=endpoint_url,
        # region_name="us-east-1",
        # credentials_profile_name="<profile_name>",
    )

# RAGシステム用のプロンプトテンプレート
PROMPT_TEMPLATE = """
Human: あなたは優秀なアシスタントであり、ユーザーからの問い合わせに可能な限り事実に基づいて質問に回答します。
以下の情報を用いて、<question>タグで囲まれた質問に簡潔に回答してください。
答えがわからない場合は、「わからない」とだけ伝え、わざわざ答えを作ろうとしないでください。
<context>
{context}
</context>

<question>
{question}
</question>

回答は具体的なものでなければなりません。

Assistant:"""
# プロンプトテンプレートオブジェクトを作成
prompt = PromptTemplate(template=PROMPT_TEMPLATE, 
                               input_variables=["context","question"])

# 検索結果のドキュメントを結合する関数
def format_docs(docs): 
    """Retrieverから取得したドキュメントのpage_contentを結合"""
    return "\n\n".join(doc.page_content for doc in docs)

# RAGチェーンの構築：検索→フォーマット→プロンプト→LLM→パース
chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm_for_text_generation
    | StrOutputParser()
)

# RAGAS評価用のテストデータセット
# 評価用の質問リスト
questions = [
    "AnyCompany では社員が結婚するときに何日間休暇をもらえますか？",
    "AnyCompany では社員が裁判員になった場合休暇が与えられますか？",
    "AnyCompany の休暇の規定は、どのような法律の何条に基づいて定められていますか？"
]

# 各質問に対する正解データ（Ground Truth）
ground_truth = [
    "AnyCompany では社員が結婚するときに7日間の休暇が与えられます。",
    "はい、AnyCompany では社員が裁判員になった場合、休暇が与えられます。裁判員や補充裁判員となった場合、必要な日数分の休暇が与えられ、裁判員候補者となった場合、必要な時間の休暇が与えられます。",
    "AnyCompany の休暇の規定は、労働基準法（労基法）第89条に基づいて定められています。"
]

def get_model_response(query, chain, retriever, max_retries=5, wait_time=15):
    """モデルからの応答を取得（リトライ機能付き）
    
    Args:
        query: 質問文
        chain: RAGチェーン
        retriever: Knowledge Base retriever
        max_retries: 最大リトライ回数
        wait_time: リトライ間の待機時間（秒）
    
    Returns:
        tuple: (回答, コンテキスト) または (None, None)
    """
    for attempt in range(max_retries):
        try:
            # Nova Liteの設定（トークン数増加）
            nova_config = {
                "schemaVersion": "messages-v1",
                "messages": [{
                    "role": "user",
                    "content": [{"text": query}]
                }],
                "inferenceConfig": {
                    "maxTokens": 2048,
                    "temperature": 0.5,
                    "topP": 0.9,
                    "topK": 20
                }
            }
            
            # 設定オーバーライドで実行を試行
            try:
                answer = chain.invoke(
                    query,
                    config_override={"model_kwargs": nova_config}
                )
            except AttributeError:
                # config_overrideが機能しない場合は直接実行
                answer = chain.invoke(query)
            
            # コンテキストを取得
            context = [docs.page_content for docs in retriever.invoke(query)]
            print(f"Successfully processed query on attempt {attempt + 1}")
            return answer, context
            
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Failed after {max_retries} attempts for query: {query[:50]}...")
                print(f"Error: {str(e)}")
                return None, None
            print(f"Attempt {attempt + 1} failed, waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)

# 質問を順次処理してRAGシステムの回答を取得
answers = []  # LLMの回答を格納
contexts = []  # 検索されたコンテキストを格納

print("Starting to process questions...")
for i, query in enumerate(questions, 1):
    print(f"\nProcessing question {i}/{len(questions)}")
    print(f"Query: {query[:100]}...")
    
    # RAGシステムから回答とコンテキストを取得
    answer, context = get_model_response(query, chain, retriever)
    if answer is not None:
        answers.append(answer)
        contexts.append(context)
        print(f"Successfully processed question {i}")
    else:
        print(f"Failed to process question {i}")
    
    # 必要に応じてAPI制限回避のための待機時間を追加
    #if i < len(questions):
    #    print(f"Waiting 60 seconds before next question...")
    #    time.sleep(60)

# RAGAS評価用のデータセットを作成
data = {
    "question": questions[:len(answers)],      # 質問
    "ground_truth": ground_truth[:len(answers)],  # 正解データ
    "answer": answers,                         # LLMの回答
    "contexts": contexts                       # 検索されたコンテキスト
}

# Hugging Face Datasetsフォーマットに変換
dataset = Dataset.from_dict(data)

# データセット作成結果の表示
print("\nDataset Creation Summary:")
print(f"Total questions processed: {len(dataset)} out of {len(questions)}")
print(f"Columns available: {dataset.column_names}")

# サンプルエントリの表示
if len(dataset) > 0:
    print("\nSample Entry (First Question):")
    print(f"Question: {dataset[0]['question']}")
    print(f"Ground Truth: {dataset[0]['ground_truth']}")
    print(f"Model Answer: {dataset[0]['answer']}")
else:
    print("\nNo entries were successfully processed into the dataset.")

# 各質問に対するLLMの回答と正解データを比較表示
i=0
for answer in answers:
    i=i+1
    print(str(i)+').'+questions[i-1]+'\n')
    print("LLM:" +answer+'\n')
    print ("Ground truth: "+ ground_truth[i-1]+'\n')

# Dataset互換性のための関数（古いバージョン対応）
if not hasattr(Dataset, 'from_list'):
    def from_list_compatibility(data_list):
        """Dataset.from_listメソッドの互換性関数"""
        if isinstance(data_list, list) and len(data_list) > 0 and isinstance(data_list[0], dict):
            keys = data_list[0].keys()
            data_dict = {key: [item[key] for item in data_list] for key in keys}
            return Dataset.from_dict(data_dict)
        return Dataset.from_dict({})
    Dataset.from_list = staticmethod(from_list_compatibility)

# RAGAS評価の実行
from ragas import evaluate

# 基本的な評価メトリクス
from ragas.metrics import (
    faithfulness,          # 忠実度：回答がコンテキストに基づいているか
    answer_relevancy,      # 回答関連性：回答が質問に関連しているか
    context_recall,        # コンテキスト再現率：関連情報の網羅性
    context_precision,     # コンテキスト精度：検索文書の関連性
    context_entity_recall, # エンティティ再現率：特定エンティティの検索精度
    answer_similarity,     # 回答類似性：正解との類似度
    answer_correctness     # 回答正確性：回答の正確性
)

# 批評的評価メトリクス
from ragas.metrics.critique import (
harmfulness,   # 有害性評価
maliciousness, # 悪意性評価
coherence,     # 一貫性評価
correctness,   # 正確性評価
conciseness    # 簡潔性評価
)

# 使用する評価メトリクスを指定
metrics = [
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
        context_entity_recall,
        answer_similarity,
        answer_correctness,
        harmfulness, 
        maliciousness, 
        coherence, 
        correctness, 
        conciseness
    ]

# RAGAS評価の実行
try:
    result = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=llm_for_evaluation,        # 評価用LLM
        embeddings=bedrock_embeddings,  # Embedding用モデル
    )
    # 結果をPandas DataFrameに変換
    df = result.to_pandas()
except Exception as e:
    # 評価中にエラーが発生した場合の処理
    print(f"An error occurred: {e}")

# 結果をExcelファイルに出力
import pandas as pd
pd.options.display.max_colwidth = 10  # 表示する最大文字数を設定
df.style.set_sticky(axis="columns")    # 列を固定表示

# スタイル付きExcelファイルとして保存
df.style.to_excel('styled.xlsx', engine='openpyxl')