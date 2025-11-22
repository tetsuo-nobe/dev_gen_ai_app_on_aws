# 回答は質問に対応しているか
# 生成された応答がトピックに沿っていて、脱線していないか
# 通常、スコアは 0 から 1 の間になるが、
# コサイン類似度の数学的範囲は -1 から 1 であるためスコアが保証されるわけではない。
# スコアが高いほど、ユーザー入力との関連性が高いことを示す

import asyncio
import boto3
from langchain_aws import ChatBedrock
from langchain_aws import BedrockEmbeddings
from ragas import SingleTurnSample
from ragas.metrics import ResponseRelevancy

async def main():
    bedrock_client = boto3.client('bedrock-runtime')
    
    evaluator_llm = ChatBedrock(
        model_id="anthropic.claude-3-haiku-20240307-v1:0", 
        client=bedrock_client,
        model_kwargs={"temperature": 0.1}
    )

    evaluator_embeddings = BedrockEmbeddings(
        model_id="amazon.titan-embed-text-v2:0",
        client=bedrock_client
    )

    scorer = ResponseRelevancy(llm=evaluator_llm, embeddings=evaluator_embeddings)
    sample = SingleTurnSample(
        user_input="最初のスーパーボウルはいつでしたか？",
        retrieved_contexts=[
            "第1回AFL-NFLワールドチャンピオンシップゲームは、1967年1月15日にロサンゼルスのロサンゼルスメモリアルコロシアムで行われたアメリカンフットボールの試合でした。"
        ],
        response="最初のスーパーボウルは1967年1月15日に開催されました。"
    )
    
    result = await scorer.single_turn_ascore(sample)
    print(f"Response Relevancy Score: {result}")

if __name__ == "__main__":
    asyncio.run(main())

