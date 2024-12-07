import boto3

# Bedrock Agent Client: Rerank 使用時はリージョンに注意
region = 'us-west-2'

kb_agent = boto3.client(service_name='bedrock-agent-runtime', region_name=region)

# 
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
model_arn = f'arn:aws:bedrock:{region}::foundation-model/{model_id}'
kb_id = "XXXXXXXXXX" # Knowkedge Base のID
prompt = "AnyCompany社では、社員が結婚するときの休暇は何日ですか？"
#prompt = "AnyCompany社では、6か月以上勤務した場合に与えられる有給休暇は何日ですか？"

model_for_rerank = "cohere.rerank-v3-5:0"
model_for_rerank_arn = f'arn:aws:bedrock:{region}::foundation-model/{model_for_rerank}'

# retrieve with Rerank
response = kb_agent.retrieve(
    retrievalQuery={
        'text': prompt
    },
    knowledgeBaseId=kb_id,
    retrievalConfiguration={
    'vectorSearchConfiguration': {
      'numberOfResults': 5,
      'overrideSearchType': 'SEMANTIC',
      'rerankingConfiguration': {
        'bedrockRerankingConfiguration': {
          "modelConfiguration": {
            "modelArn": model_for_rerank_arn
          },
        },
        'type': 'BEDROCK_RERANKING_MODEL',
      },
    }
  }
)

# result 

print('--- 取得したドキュメントを出力 ---')
for doc in response['retrievalResults']:
  print(doc['score'], doc['content']['text'][0:60])
