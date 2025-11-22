# Amazon Knowledge Baseを使用したRAGシステムの実装
# LangChainとAmazon Bedrockを組み合わせた質問応答システム

import boto3
import pprint

from langchain_aws import ChatBedrock
from langchain_aws import BedrockEmbeddings
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever

# Knowledge Base ID（1_getKBID.pyで取得したIDを設定）
kb_id = "TOROHCUSM0"

# デバッグ用のプリティプリンター
pp = pprint.PrettyPrinter(indent=2)

# Amazon Bedrockクライアントを初期化
bedrock_client = boto3.client('bedrock-runtime')

# テキスト生成用のLLM（Nova Lite）
llm_for_text_generation = ChatBedrock(model_id="us.amazon.nova-lite-v1:0", client=bedrock_client)
# 評価用のLLM（将来のRAGAS評価で使用）
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



# プロンプトテンプレートの設定
from langchain.prompts import PromptTemplate

# RAGシステム用のプロンプトテンプレート
# コンテキストと質問を組み合わせて適切な回答を生成
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



# RAGチェーンの構築
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

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

# テスト用のクエリ（他のクエリ例もコメントで残している）
#query = "AnyCompany では社員が結婚するときに何日間休暇をもらえますか？"
#query = "AnyCompany では社員が裁判員になった場合休暇が与えられますか？"
query = "AnyCompany の休暇の規定は、どのような法律の何条に基づいて定められていますか？"

# RAGシステムを実行して回答を取得
response=chain.invoke(query)
print(response)