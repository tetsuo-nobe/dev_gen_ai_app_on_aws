# ユーザーの質問で言及された特定のエンティティ (人、場所、製品など) を含むドキュメントをシステムが検索しているかどうか
# 値は 0～1 の範囲で高いほど再現率が高い

import asyncio
import boto3
from langchain_aws import ChatBedrock
from ragas import SingleTurnSample
from ragas.metrics import ContextEntityRecall

async def main():
    bedrock_client = boto3.client('bedrock-runtime')
    
    evaluator_llm = ChatBedrock(
        model_id="anthropic.claude-3-haiku-20240307-v1:0", 
        client=bedrock_client,
        model_kwargs={"temperature": 0.1}
    )
    
    scorer = ContextEntityRecall(llm=evaluator_llm)
    sample = SingleTurnSample(
        reference="エッフェル塔はパリにあります。", 
        retrieved_contexts=["エッフェル塔があるのは、フランスのパリです。"],
    )
    
    result = await scorer.single_turn_ascore(sample)
    print(f"Context Entity Recall Score: {result}")

if __name__ == "__main__":
    asyncio.run(main())

