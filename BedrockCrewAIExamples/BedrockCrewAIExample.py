"""
CrewAIを使用した協調ブログ記事作成システム
2つのAgent（リサーチャーとライター）が協力してブログ記事を作成します
"""

import os
from crewai import LLM, Agent, Task, Crew, Process
from duckduckgo_search import DDGS

# Amazon Bedrock用のLLM設定
def get_bedrock_llm():
    """Amazon BedrockのClaude 4 Sonnetモデルを初期化"""
    llm = LLM(
       model="bedrock/global.anthropic.claude-sonnet-4-20250514-v1:0",
       region_name="us-east-1"
    )
    return llm

# LLMインスタンスを作成
llm = get_bedrock_llm()


# Agent 1: リサーチャー
researcher = Agent(
    role="コンテンツリサーチャー",
    goal="指定されたトピックについて詳細な調査を行い、正確で価値のある情報を収集する",
    backstory="""あなたは経験豊富なリサーチャーです。
    複雑なトピックを理解し、重要なポイントを抽出する能力に優れています。
    常に信頼性の高い情報源を探し、読者に価値を提供することを心がけています。
    Web検索ツールを積極的に活用して、最新の情報を収集します。
    検索する際は、具体的なキーワードを指定してツールを複数回検索を実行します。""",
    allow_delegation=False,
    llm=llm
)

# Agent 2: ライター
writer = Agent(
    role="ブログライター",
    goal="リサーチ結果を基に、読みやすく魅力的なブログ記事を執筆する",
    backstory="""あなたはプロのブログライターです。
    複雑な情報を分かりやすく伝え、読者を引き込む文章を書くことが得意です。
    SEOを意識しながらも、読者ファーストの記事作成を心がけています。""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# タスク1: リサーチタスク
research_task = Task(
    description="""トピック「{topic}」について徹底的にリサーチしてください。
    
    以下の点を含めてください：
    - トピックの基本的な説明
    - 主要なポイントや特徴
    - 最新のトレンドや動向
    - 読者が知るべき重要な情報
    - 具体例や事例
    
    リサーチ結果は構造化された形式でまとめてください。""",
    agent=researcher,
    expected_output="トピックに関する詳細なリサーチレポート（構造化された形式）"
)

# タスク2: 執筆タスク
writing_task = Task(
    description="""リサーチ結果を基に、魅力的なブログ記事を執筆してください。
    
    記事の構成：
    1. 魅力的なタイトル
    2. 導入部分（読者の興味を引く）
    3. 本文（リサーチ内容を分かりやすく展開）
    4. まとめ（重要ポイントの再確認）
    
    要件：
    - 読みやすい文章
    - 適切な見出しと段落構成
    - 具体例を含める
    - 1500-2000文字程度
    - 日本語で執筆""",
    agent=writer,
    expected_output="完成したブログ記事（タイトル、本文、まとめを含む）",
    context=[research_task]  # リサーチタスクの結果を利用
)

# Crewの作成
blog_crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential,  # タスクを順次実行
    verbose=True
)

def create_blog_post(topic: str) -> str:
    """
    指定されたトピックでブログ記事を作成
    
    Args:
        topic: ブログ記事のトピック
        
    Returns:
        完成したブログ記事
    """
    print(f"\n{'='*60}")
    print(f"ブログ記事作成開始: {topic}")
    print(f"{'='*60}\n")
    
    result = blog_crew.kickoff(inputs={"topic": topic})
    
    print(f"\n{'='*60}")
    print("ブログ記事作成完了！")
    print(f"{'='*60}\n")
    
    return result

if __name__ == "__main__":
    # 使用例
    topic = "京都の観光地としての魅力"

    # 必要な環境変数の確認
    missing_vars = []    

    blog_post = create_blog_post(topic)
        
    # 結果をファイルに保存
    with open("blog_post.md", "w", encoding="utf-8") as f:
        f.write(str(blog_post))
        
    print("\n記事が blog_post.md に保存されました")
