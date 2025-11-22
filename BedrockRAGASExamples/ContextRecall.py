# ナレッジベースに存在するすべての関連情報を収集しているか
# 値は 0～1 の範囲で高いほど再現率が高い

import asyncio
import boto3
from langchain_aws import ChatBedrock
from ragas import SingleTurnSample
from ragas.metrics import LLMContextRecall

async def main():
    bedrock_client = boto3.client('bedrock-runtime')
    
    evaluator_llm = ChatBedrock(
        model_id="anthropic.claude-3-haiku-20240307-v1:0", 
        client=bedrock_client,
        model_kwargs={"temperature": 0.1}
    )
    
    context_recall = LLMContextRecall(llm=evaluator_llm)
    sample = SingleTurnSample(
        user_input="エッフェル塔はどこにありますか？",
        reference="エッフェル塔はパリにあります。", 
        retrieved_contexts=["エッフェル塔があるのは、フランスのパリです。"],
    )
    
    result = await context_recall.single_turn_ascore(sample)
    print(f"Context Recall Score: {result}")

if __name__ == "__main__":
    asyncio.run(main())

