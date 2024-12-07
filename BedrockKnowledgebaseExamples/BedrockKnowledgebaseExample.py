import boto3

# Bedrock Agent runtime Client
kb_agent = boto3.client(service_name='bedrock-agent-runtime')

# 
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
model_arn = f'arn:aws:bedrock:us-east-1::foundation-model/{model_id}'
kb_id = "XXXXXXXXXX" # Knowkedge Base のID
prompt = "AnyCompany社では、社員が結婚するときの休暇は何日ですか？"
#prompt = "AnyCompany社では、6か月以上勤務した場合に与えられる有給休暇は何日ですか？"

# retrieve_and_generate
response = kb_agent.retrieve_and_generate(
    input={
        'text': prompt
    },
    retrieveAndGenerateConfiguration={
        'type': 'KNOWLEDGE_BASE',
        'knowledgeBaseConfiguration': {
            'knowledgeBaseId': kb_id,
            'modelArn': model_arn
        }
    }
)

# result

print('--- 回答を出力 ---')
generated_text = response['output']['text']
print(generated_text)
print('')
################################################################

# retrieve_and_generate_stream
response = kb_agent.retrieve_and_generate_stream(
    input={
        'text': prompt
    },
    retrieveAndGenerateConfiguration={
        'type': 'KNOWLEDGE_BASE',
        'knowledgeBaseConfiguration': {
            'knowledgeBaseId': kb_id,
            'modelArn': model_arn
        }
    }
)

# result as stream
print('--- 回答をストリームで出力 ---')
stream = response.get("stream")

if stream:
    for event in stream:
        if "output" in event:
            print(event['output']['text'], end="", flush=True)

print('')
################################################################

# retrieve
response = kb_agent.retrieve(
    retrievalQuery={
        'text': prompt
    },
    knowledgeBaseId=kb_id
)

# result 

print('--- 取得したドキュメントを出力 ---')
for doc in response['retrievalResults']:
  print(doc)
