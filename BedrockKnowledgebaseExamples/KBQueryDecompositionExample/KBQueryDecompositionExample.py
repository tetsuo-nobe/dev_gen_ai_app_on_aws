#
# Bedrock ナレッジベースのクエリ分解のサンプル
#
import boto3

KNOWLEDGEBASE_ID = "PIVKFRIMYF"  # ナレッジベース ID 
model_arn = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0"
bedrock_agent = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

prompt = (
    "AnyCompany社の就業規則は労働基準法の第何条に基づいて規定されていますか？社員が結婚するときに何日間休暇が与えられますか？社員が裁判員になった場合に休暇は与えられますか？"
)

response = bedrock_agent.retrieve_and_generate(
    input={"text": prompt},
    retrieveAndGenerateConfiguration={
        "type": "KNOWLEDGE_BASE",
        "knowledgeBaseConfiguration": {
            "knowledgeBaseId": KNOWLEDGEBASE_ID,
            "modelArn": model_arn,
            # クエリ分解の設定は下記
            "orchestrationConfiguration": {
                "queryTransformationConfiguration": {"type": "QUERY_DECOMPOSITION"}
            },
        },
    },
)
print(response["output"]["text"],flush=False)
#print(response,flush=False)

