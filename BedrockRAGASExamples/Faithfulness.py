# 回答が提供されたコンテキストに基づいているか
# 値は (0,1) の範囲で計測されます。高いほど忠実度が高い

import asyncio
import boto3
from langchain_aws import ChatBedrock
from ragas import SingleTurnSample
from ragas.metrics import Faithfulness

async def main():
    bedrock_client = boto3.client('bedrock-runtime')
    
    evaluator_llm = ChatBedrock(
        model_id="anthropic.claude-3-haiku-20240307-v1:0", 
        client=bedrock_client,
        model_kwargs={"temperature": 0.1}
    )

    scorer = Faithfulness(llm=evaluator_llm)
    sample = SingleTurnSample(
        user_input="最初のスーパーボウルはいつでしたか？",
        retrieved_contexts=[
            "第1回AFL-NFLワールドチャンピオンシップゲームは、1967年1月15日にロサンゼルスのロサンゼルスメモリアルコロシアムで行われたアメリカンフットボールの試合でした。"
        ],
        response="最初のスーパーボウルは1967年1月15日に開催されました。"
    )
    
    result = await scorer.single_turn_ascore(sample)
    print(f"Faithfulness Score: {result}")

if __name__ == "__main__":
    asyncio.run(main())
