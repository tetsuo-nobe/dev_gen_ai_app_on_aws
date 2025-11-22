# リファレンス(ground_truth)なしの Context Precision 
# 検索したドキュメントがユーザーの質問に関連しているか
# 値は 0～1 の範囲で高いほど精度が高い
import asyncio
import boto3
from langchain_aws import ChatBedrock
from ragas import SingleTurnSample
from ragas.metrics import LLMContextPrecisionWithoutReference

async def main():
    bedrock_client = boto3.client('bedrock-runtime')
    
    evaluator_llm = ChatBedrock(
        model_id="anthropic.claude-3-haiku-20240307-v1:0", 
        client=bedrock_client,
        model_kwargs={"temperature": 0.1}
    )
    
    context_precision = LLMContextPrecisionWithoutReference(llm=evaluator_llm)
    sample = SingleTurnSample(
        user_input="エッフェル塔はどこにありますか？",
        response="エッフェル塔はパリにあります。", 
        retrieved_contexts=["エッフェル塔があるのは、フランスのパリです。"],
    )
    
    result = await context_precision.single_turn_ascore(sample)
    print(f"Context Precision Score: {result}")

if __name__ == "__main__":
    asyncio.run(main())

