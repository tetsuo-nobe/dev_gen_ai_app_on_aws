# 必要なライブラリをインポート
from strands import Agent
from dotenv import load_dotenv
import logging

# .envファイルから環境変数を読み込む
load_dotenv()

# ログレベルの指定
logging.getLogger("strands").setLevel(logging.INFO)

# ログハンドラの追加
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s", 
    handlers=[logging.StreamHandler()]
)

# エージェントを作成して起動
agent = Agent("apac.anthropic.claude-sonnet-4-20250514-v1:0")
results = agent("Strandsってどういう意味？")

print("\n")

# エージェントのメッセージの確認
print("-" * 80)
print("\n")
print(agent.messages)
print("\n")

# エージェント使用時のメトリクスを確認
print("-" * 80)
print("\n")
print(results.metrics)