# コンテキストが無関係な場合に、破棄されるか
# スコアの範囲は0から1で、値が低いほどパフォーマンスが良いことを示す

import asyncio
import boto3
from langchain_aws import ChatBedrock
from ragas import SingleTurnSample
from ragas.metrics import NoiseSensitivity

async def main():
    bedrock_client = boto3.client('bedrock-runtime')
    
    evaluator_llm = ChatBedrock(
        model_id="anthropic.claude-3-haiku-20240307-v1:0", 
        client=bedrock_client,
        model_kwargs={"temperature": 0.1}
    )
    
    scorer = NoiseSensitivity(llm=evaluator_llm)
    sample = SingleTurnSample(
        user_input="AnyCompanyは何で有名ですか?",
        retrieved_contexts=[
            "AnyCompany は、1956 年の国有化を受けて設立されました。",
            "AnyCompany は米国最大の保険会社として有名です。",
            "米国最大の機関投資家であるAnyCompanyには、5000名以上の従業員がいます。"
        ],
        response="AnyCompany は米国最大の保険会社です。",
        reference="AnyCompanyは1956年に国有化された米国最大の保険会社として有名です。"
    )
    
    result = await scorer.single_turn_ascore(sample)
    print(f"Noise Sensitivity Score: {result}")

if __name__ == "__main__":
    asyncio.run(main())

