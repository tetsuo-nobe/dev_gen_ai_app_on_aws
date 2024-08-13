
### 例1: 指定したリージョンにおいてサポートされているモデルの一覧の表示
```
aws bedrock list-foundation-models \
--region us-east-1 \
--query "modelSummaries[].
[providerName,
modelId,
inputModalities[0],
outputModalities[0]]" \
--output text | tr '\t' ',' | column -s, -t | sort
```

### 例2: モデルの呼び出し（converse を使用したテキスト生成: Meta LLama3）
```
aws bedrock-runtime converse \
--model-id "meta.llama3-8b-instruct-v1:0" \
--messages '[{"role":"user","content":[{"text":"日本の首都はどこですか"}]}]' \
--inference-config '{"maxTokens":512,"temperature":0.5,"topP":0.9}' \
--additional-model-request-fields '{}' \
--region us-east-1
```

### 例3: モデルの呼び出し（invoke-model を使用したテキスト生成: Meta LLama3）
```
aws bedrock-runtime invoke-model \
--model-id "meta.llama3-8b-instruct-v1:0"  \
--body '{ "prompt": "アメリカの首都はどの都市ですか？","max_gen_len": 512,"temperature": 0.5}' \
 output-llma3.txt
```

### 例4: モデルの呼び出し（invoke-model を使用したテキスト生成: Amazon Titan Text）
```
aws bedrock-runtime invoke-model \
--model-id amazon.titan-text-express-v1 \
--body '{"inputText": "Describe the purpose of a \"hello world\" program in one line.", "textGenerationConfig" : {"maxTokenCount": 512, "temperature": 0.5, "topP": 0.9}}' \
 invoke-model-output-text.txt
```

