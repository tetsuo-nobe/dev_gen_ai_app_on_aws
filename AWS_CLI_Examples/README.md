
### 例1: 指定したリージョンにおいてサポートされているモデルの一覧の表示
```
aws bedrock list-foundation-models \
--region us-east-1 \
--query "modelSummaries[].
[providerName,
modelId,
inputModalities[0],
outputModalities[0]]" \
--output text | sort
```

### 例2: モデルの呼び出し（invoke-model を使用したテキスト生成: Meta LLama3）
```
aws bedrock-runtime invoke-model \
--model-id "meta.llama3-8b-instruct-v1:0"  \
--body '{ "prompt": "user: あなたはアシスタントです。質問に回答してください。日本の首都はどこですか? assistant: ","max_gen_len": 50,"temperature": 0.9}' \
 output-llma3.txt
```

### 例3: モデルの呼び出し（invoke-model を使用したテキスト生成: Anthropic Claude）
```
aws bedrock-runtime invoke-model \
--model-id "anthropic.claude-3-sonnet-20240229-v1:0"  \
--body '{ "anthropic_version": "bedrock-2023-05-31","max_tokens": 200, "temperature": 0.1, "top_p": 0.9, "messages": [ {"role": "user", "content": [ {"type":"text", "text": "あなたはアシスタントです。質問に回答してください。生成AIとは何ですか？"}]}]}' \
 output-claude.txt
```

### 例4: モデルの呼び出し（converse を使用したテキスト生成: Meta LLama3）
```
aws bedrock-runtime converse \
--model-id "meta.llama3-8b-instruct-v1:0" \
--messages '[{"role":"user","content":[{"text":"あなたはアシスタントです。質問に回答してください。日本の首都はどこですか?"}]}]' \
--inference-config '{"maxTokens":50,"temperature":0.5,"topP":0.9}' \
--additional-model-request-fields '{}' \
--region us-east-1
```

### 例5: モデルの呼び出し（converse を使用したテキスト生成: Anthropic Claude）
```
aws bedrock-runtime converse \
--model-id "anthropic.claude-3-sonnet-20240229-v1:0" \
--messages '[{"role":"user","content":[{"text":"あなたはアシスタントです。質問に回答してください。生成AIとは何ですか？"}]}]' \
--inference-config '{"maxTokens":512,"temperature":0.5,"topP":0.9}' \
--additional-model-request-fields '{}' \
--region us-east-1
```
