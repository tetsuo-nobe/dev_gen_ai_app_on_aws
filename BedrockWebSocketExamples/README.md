# API Gateway WebSocket API + Lambda + Bedrock でストリームレスポンスを取得する

* 東京リージョンで Claude Sonnet 3.5 を有効化しておく

1. CloudFormation で 1_iam.yaml からスタック作成
1. CloudFormation で 2_main.yaml または 3_main_converse.yaml からスタック作成
    - API Gateway の WebSocket API とそれと統合された Lambda 関数を作成
    - sendtext ルートと統合された Lambda 関数では、プロンプトを受信して Bedrock に invokeModelWithResponseStream を実行し、ストリームで返信
    - 2_main.yaml では invokeModelWithResponseStream API を使用。3_main_converse.yaml では Converse API を使用。
1. 出力から API Gateway WebSocket API の URL をメモしておく

1. コマンドプロンプト or ターミナルを 1つ起動して下記を入力

```
 wscat -c wss://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/dev/
```

コマンドプロンプト or ターミナル から下記を送信

```
{"action": "sendtext", "text": "Hello!"}
```

* 下記のような回答が返ってくる
```
< "Hello! How"
< " can"
< " I assist you today"
< "? Feel"
< " free to ask me"
< " any"
< " questions or"
< " let"
< " me know if you"
< " need help"
< " with anything."
```

* 日本語の場合は Unicode エスケープシーケンスで表示される

```
 {"action": "sendtext", "text": "こんにちは。"}
```

```
 < "\u3053"
< "\u3093\u306b\u3061\u306f"
< "\uff01"
< "\u304a"
< "\u624b"
< "\u4f1d\u3044\u3067\u304d"
< "\u308b\u3053\u3068"
< "\u304c\u3042\u308c\u3070\u3069"
< "\u3046\u305e\u304a"
< "\u3063"
< "\u3057\u3083\u3063\u3066"
< "\u304f\u3060\u3055\u3044\u3002\u4f55"
< "\u304b\u8cea\u554f\u3084"
< "\u8a71"
< "\u3057\u305f"
< "\u3044\u30c8"
< "\u30d4\u30c3\u30af\u306f"
< "\u3042\u308a\u307e\u3059\u304b?"
```


* 停止時は Ctrl + c



