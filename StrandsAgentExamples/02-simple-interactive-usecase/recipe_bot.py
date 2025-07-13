# Agent と tool のインポート
from strands import Agent, tool
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import RatelimitException, DuckDuckGoSearchException
import logging

# logging の構成
logging.getLogger("strands").setLevel(logging.INFO) # より詳細なログを表示するにはDEBUGに設定する

# Define a websearch tool
@tool
def websearch(keywords: str, region: str = "us-en", max_results: int | None = None) -> str:
    """ウェブを検索して最新情報を取得します。
      引数:
          keywords (str): 検索クエリキーワード
          region (str): 検索地域: wt-wt、us-en、uk-en、ru-ru など
          max_results (int | None): 返される結果の最大件数
      戻り値:
          検索結果を含む辞書型のリスト
    """
    try:
        results = DDGS().text(keywords, region=region, max_results=max_results)
        return results if results else "結果が見つかりませんでした。"
    except RatelimitException:
        return "RatelimitException: しばらくしてからもう一度お試しください。"
    except DuckDuckGoSearchException as d:
        return f"DuckDuckGoSearchException: {d}"
    except Exception as e:
        return f"Exception: {e}"
    

# Create a recipe assistant agent
recipe_agent = Agent(
    model = "anthropic.claude-3-sonnet-20240229-v1:0",
    system_prompt="""あなたはRecipeBot、料理アシスタントです。
    ユーザーが食材に基づいてレシピを探すのを手伝ったり、料理に関する質問に答えたりしましょう。
    ユーザーが食材について言及したときにレシピを検索したり、料理情報を調べたりするには、ウェブ検索ツールをご利用ください。""",
    tools=[websearch],
)


if __name__ == "__main__":
    print("\n👨‍🍳 RecipeBot: レシピや料理について尋ねてください！終了するには exit と入力してください。\n")
    
    # Run the agent in a loop for interactive conversation
    while True:
        user_input = input("\nYou > ")
        if user_input.lower() == "exit":
            print("Happy cooking! 🍽️")
            break
        response = recipe_agent(user_input)
        print(f"\nRecipeBot > {response}")