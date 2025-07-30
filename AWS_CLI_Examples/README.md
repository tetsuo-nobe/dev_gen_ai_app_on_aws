
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

### 例2: モデルの呼び出し（invoke-model を使用したテキスト生成）
```
aws bedrock-runtime invoke-model \
--model-id "amazon.nova-lite-v1:0"  \
--body '{"messages": [{"role": "user","content": [{"text": "あなたはアシスタントです。質問に回答してください。日本の首都はどこですか?"}]}],"inferenceConfig": {"maxTokens": 50,"stopSequences": [],"temperature": 0.5,"topP": 0.9}}' \
 output.txt
```

### 例3: モデルの呼び出し（converse を使用したテキスト生成）
```
aws bedrock-runtime converse \
--model-id "amazon.nova-lite-v1:0" \
--messages '[{"role":"user","content":[{"text":"あなたはアシスタントです。質問に回答してください。日本の首都はどこですか?"}]}]' \
--inference-config '{"maxTokens":50,"temperature":0.5,"topP":0.9}' \
--additional-model-request-fields '{}' \
--region us-east-1
```

