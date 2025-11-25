# Amazon Bedrock の推論プロファイル

* [推論プロファイルを使用してモデル呼び出しリソースを設定する](https://docs.aws.amazon.com/ja_jp/bedrock/latest/userguide/inference-profiles.html)

* 下記 2種類の推論プロファイル
1. クロスリージョン推論用の事前定義済の推論プロファイル
1. 使用状況をコストを識別するためのカスタムの推論プロファイル（アプリケーション推論プロファイル）
    - CloudWatch のメトリクスや、タグをつけてのコスト集計で可視化できる
    - Bedrock の PlayGround からも選択可能

* アプリケーション推論プロファイル
    - マネジメントコンソールでは作成できない
    - AWS CLI で作成する場合は下記

* アプリケーション推論の作成
```
PROFILE_NAME=my_profile
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region)

aws bedrock create-inference-profile \
  --inference-profile-name ${PROFILE_NAME} \
  --model-source copyFrom=arn:aws:bedrock:${AWS_REGION}:${AWS_ACCOUNT}:inference-profile/global.anthropic.claude-haiku-4-5-20251001-v1:0 \
  --tags key=project,value=my_project \
  --no-cli-pager
```

* アプリケーション推論の取得
```
aws bedrock list-inference-profiles \
  --type-equals APPLICATION \
  --no-cli-pager
```

* アプリケーション推論の削除
```
PROFILE_ARN=<アプリケーション推論プロファイルの ARN>

aws bedrock delete-inference-profile \
  --inference-profile-identifier ${PROFILE_ARN}
```