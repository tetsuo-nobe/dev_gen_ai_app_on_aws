# AWS Lambda 関数の FunctionURL を使用して Amazon Bedrock の基盤モデルからストリームの応答を表示する

- AWS Lambda のストリームレスポンス機能を使用するので、ランタイムは Node.js を使用する
- curl コマンドの -N (--no-buffer) オプションをつけることでストリームのレスポンスを確認する 

```
ENDPOINT=https://t3bumwxlkjx4oatvdmcwshwdoq0lvsac.lambda-url.us-east-1.on.aws/   
curl -N ${ENDPOINT}  -H "Content-Type: application/json" -d '{"prompt": "こんにちは"}'

curl -N ${ENDPOINT}  -H "Content-Type: application/json" -d '{"prompt": "京都の有名な観光名所を5つ挙げてください。"}'

```
