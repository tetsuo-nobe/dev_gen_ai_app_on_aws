import boto3
from dotenv import load_dotenv

"""
 * 短期キー
     - 12時間のみ
     - 発行後はどこにも管理されていない
     - 発行したリージョンのみで有効
 * 長期キー
     - 日単位で期間指定可能。無期限の設定も可能
     - 発行後は IAM ユーザ が作成されその Bedrock キーとして管理されている
     - 発行リージョンに関わらず利用可能
 * キーは 環境変数 AWS_BEARER_TOKEN_BEDROCK に指定する
"""

# 環境変数読み込み:AWS_BEARER_TOKEN_BEDROCK でキーを設定しておく
load_dotenv()

bedrock_client = boto3.client('bedrock-runtime', region_name = 'us-east-1')

model_id = "amazon.nova-lite-v1:0"
#model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

# Inference parameters to use.
temperature = 0.5
top_k = 200

# Base inference parameters to use.
inference_config = {"temperature": temperature}
# Additional inference parameters to use.
#additional_model_fields = {"top_k": top_k}

# Setup the system prompts and messages to send to the model.
system_prompts = [{"text": "あなたは優秀なアシスタントです。質問に対して丁寧に回答して下さい。"}]
message_1 = {
    "role": "user",
    "content": [{"text": "こんにちは。京都の観光名所を3つ挙げて下さい。"}]
}

messages = []


# Start the conversation with the 1st message.
messages.append(message_1)

# Send the message.
response = bedrock_client.converse(
        modelId=model_id,
        messages=messages,
        system=system_prompts,
        inferenceConfig=inference_config
#        additionalModelRequestFields=additional_model_fields
)

# Add the response message to the conversation.
output_message = response['output']['message']
messages.append(output_message)

# Show the complete conversation.
for message in messages:
    print(f"Role: {message['role']}")
    for content in message['content']:
        print(f"Text: {content['text']}")
    print()