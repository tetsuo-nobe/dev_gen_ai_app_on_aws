# ラボ 5: Amazon Bedrock ナレッジベースおよびガードレールと統合された Amazon Bedrock エージェントの開発

## ラボの概要

このラボでは、AnyCompany Outdoor Power Equipment と AnyCompany LawnCare Solutions の 2 社の芝生メンテナンス製品について、質問に答えるショッピングアシスタントエージェントを作成します。まず、AWS マネジメントコンソールを使用して、Amazon Bedrock エージェントを作成します。このとき、事前構築済みの Amazon Bedrock ナレッジベースとガードレールに加え、料金検索と簡単な計算という 2 つの目的を果たす AWS Lambda 関数を使用します。ナレッジベースには、メーカー、説明、評価などの製品の詳細が含まれています。AWS マネジメントコンソールでエージェントをテストした後、JupyterLab Notebook を使用し、AWS SDK を用いて Python で開発されたアプリケーションにてエージェントの使用練習を行います。このノートブックでは、セッションとメモリのパラメータを指定してショッピングアシスタントエージェントを呼び出し、短期メモリと長期メモリがエージェントの行動に与える影響について理解します。また、ナレッジベース、Lambda 関数、ガードレールを使用するように設定したエージェントを呼び出します。さらに、トレースをキャプチャして調査し、エージェントの動作を理解します。

### 目標

このラボを修了すると、以下のことができるようになります。

- Amazon Bedrock エージェントを作成する
- エージェントを Amazon Bedrock ナレッジベースと統合する
- エージェントを Amazon Bedrock ガードレールと統合する
- エージェントを AWS Lambda 関数と統合する
- ナレッジベースとガードレールがエージェントとどのように相互作用するかを分析する
- アクショングループ、メモリ、ガードレールなどのエージェントのコンポーネントを分析する
- メモリ、関数、ナレッジベース、ガードレールにアクセスできるエージェントを使用するアプリケーションを構築する
- トレースをキャプチャして分析し、エージェントの動作を理解する

### このラボで使用するサービス

#### Amazon Bedrock

Amazon Bedrock は、生成 AI アプリケーションとエージェントを構築するための包括的で安全かつ柔軟なサービスです。Amazon Bedrock では、主要な基盤モデル (FM)、エージェントをデプロイおよび運用するためのサービス、モデルのファインチューニング、保護、最適化を行うツール、さらにアプリケーションを最新データに接続するためのナレッジベースを利用できます。そのため、実験から実際のデプロイへの迅速な移行に必要なものがすべて揃っています。

#### Amazon SageMaker Studio

Amazon SageMaker Studio には、データの準備から ML モデルの構築、トレーニング、デプロイ、管理まで、機械学習 (ML) 開発のあらゆるステップを実行するためのさまざまな専用ツールが用意されています。使い慣れた IDE を使用し、データをすばやくアップロードしてモデルを構築できます。ML チームのコラボレーションを効率化し、AI 搭載のコーディングコンパニオンを使用して効率的にコーディングを行い、モデルをチューニングしてデバッグし、本番環境でモデルをデプロイして管理し、ワークフローを自動化します。これらはすべて、単一の統合されたウェブベースのインターフェイスから実行できます。このラボでは、コードを実行するための開発環境を提供するために、Amazon SageMaker Studio の JupyterLab 機能のみを使用します。

---

## タスク 1: エージェントを作成する

このタスクでは、Amazon Bedrock エージェントを一から作成し、設定します。

### タスク 1.1: エージェントのシェルを作成する

1. AWS マネジメントコンソール上部の検索バーで、`Amazon Bedrock` と検索してクリックします。
1. 左側のナビゲーションペインの [**構築**] セクションで、[**エージェント**] をクリックします。
1. <span style="ssb_orange_oval">[**エージェントを作成**]</span> をクリックします。
1. [**名前**] フィールドの現在の名前を、`shopping-assistant` に置き換えます。

<i aria-hidden="true" class="fas fa-exclamation-circle" style="color:#7C5AED"></i> **警告:** エージェント名は必ず **shopping-assistant** にします。そうしないと、後のタスクで JupyterLab Notebook を実行する際に問題が発生します。誤った名前で作成した場合は、[**エージェントビルダー**] ページで名前を変更できます。

1. [**説明 - オプション**] に `ショッピングアシスタントを実装するエージェント` と入力します。
1. [**マルチエージェントコラボレーションを有効にする**] チェックボックスはオフのままにします。
1. <span style="ssb_orange_oval">[**作成**]</span> をクリックします。
1. [**エージェントビルダー**] ページにリダイレクトされます。

### タスク 1.2: エージェントリソースロールを設定する

1. [**エージェントリソースロール**] で [**既存のサービスロールを使用**] を選択します。
1. ロールのリストから `ShoppingAssistantAgentRole` を選択します。
1. 画面の一番上までスクロールして <span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">保存</span> をクリックします。

<i aria-hidden="true" class="fas fa-sticky-note" style="color:#563377"></i> **注意:** このロールは `bedrock.amazonaws.com` サービスが引き受けることができます。このロールにより、エージェントはモデル `anthropic.claude-3-haiku-20240307-v1:0` を呼び出して、事前構築済みのナレッジベースから情報を取得して生成し、同じく事前構築済みのガードレールを適用できます。Lambda 関数を呼び出すために追加のポリシーは必要ありません。これは、Lambda 関数のリソースポリシーに許可されているためです。

### タスク 1.3: エージェントの基盤モデルを設定する

次のステップでは、エージェントがプロンプトに答えるために必要なステップを考え、さまざまな応答を作成するために使用する基礎モデルを設定します。

1. <span style="ssb_orange_oval">モデルを選択</span> をクリックします。
1. [**モデルを選択**] ウィンドウの [**カテゴリ**] で、[**Anthropic**] を選択します。
1. [**モデル**] で [**Claude 3 Haiku**] を選択します。
1. <span style="ssb_orange_oval">[**適用**]</span> をクリックします。
1. 画面の一番上までスクロールして <span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">[**保存**]</span> をクリックします。

### タスク 1.4: エージェント向けの指示を設定する

このタスクでは、前のステップで選択した基盤モデルに渡される、エージェントへの指示を設定し、エージェントの目的と実行すべきことをモデルに説明します。

1. [**エージェント向けの指示**] に次のテキストを入力します。

```plain
あなたはAIショッピングアシスタントとして、商品に関する質問に回答します。芝生の手入れに関するアドバイスは絶対にしないでください。また、憶測や勝手な答えは避けてください。あなたは数学は苦手です。そのため、数学の質問には、提供されているACTION_GROUPで利用可能なMultiFunctionCalculatorToolツールを使用してください。商品の情報はKNOWLEDGE BASEを使用しますが、商品の価格についてはPriceLookup関数を使用して下さい。常に丁寧かつ簡潔に回答してください。
```

まず、モデルに対して推測をしないように指示することで、ナレッジベースへの誘導を促しているのがわかります。次に、数学が苦手であると伝えることで、定義した関数を後のタスクで必ず使用するように導いています。

1. 画面の一番上までスクロールして <span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">[**保存**]</span> をクリックします。

<i aria-hidden="true" class="far fa-thumbs-up" style="color:#008296"></i> **タスク完了:** Amazon Bedrock エージェントを一から作成し、設定できました。

---

## タスク 2: エージェントのナレッジベースを設定する

**shopping-kb** というナレッジベースが既に作成されています。このタスクでは、そのナレッジベースを調査し、エージェントにアタッチします。

### タスク 2.1: ナレッジベースを調べる

1. 左側のナビゲーションペインの [**構築**] セクションで、[**ナレッジベース**] をクリックします。
1. [**ナレッジベース**] のリストに、**shopping-kb** があります。**shopping-kb** の横にあるラジオボタンをクリックします。
1. <span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">[**ナレッジベースをテスト**]</span> をクリックします。
1. 左側の [**設定**] セクションで、[**取得と応答生成**] を展開します。
1. [**取得のみ: データソース**] をクリックします。
1. [**テスト**] セクションで、テキストボックス (下部の「**プロンプトを記述**」と表示されたボックス) に `こんにちは。貴社の商品に興味があります。貴社が販売している商品の製造元を教えてください。` というテキストを入力します。
1. プロンプトフィールドの右下にある [**メッセージを送信**] アイコンをクリックします。
1. ナレッジベースのテキストチャンクのリストが返されるのが確認できます。
1. ナレッジベースの回答の下部にある [**詳細**] をクリックすると、各チャンクの詳細が表示されます。

[**取得のみ: データソース**] オプションを使用する場合、ナレッジベースのテキストを再構成するための LLM は使用されず、**埋め込み**モデルのみが使用されます。次は、このセクションで LLM を使用します。

1. 左側 [**設定**] セクション [**取得と応答生成**] で、[**取得と応答生成: データソースとモデル**] をクリックします。
1. [**モデル**] で <span style="ssb_orange_oval">モデルを選択</span> をクリックします。
1. [**モデルを選択**] ウィンドウの [**カテゴリ**] で、[**Anthropic**] を選択します。
1. [**モデル**] で [**Claude 3 Haiku**] を選択します。
1. <span style="ssb_orange_oval">[**適用**]</span> をクリックします。
1. [**テスト**] セクションで、テキストボックス (下部の「**プロンプトを記述**」と表示されたボックス) に `こんにちは。貴社の商品に興味があります。貴社が販売している商品の製造元を教えてください。` というテキストを入力します。
1. プロンプトフィールドの右下にある [**メッセージを送信**] アイコンをクリックします。
1. 今回は、**Claude 3 Haiku** LLM を使用して、ナレッジベースから返されたチャンクを基に、応答が再構成されたことがわかります。

### タスク 2.2: ナレッジベースをエージェントにアタッチする

**shopping-kb** ナレッジベースが機能していることを確認したので、そのナレッジベースを使用するようにエージェントを設定し、ナレッジベース内の情報を説明する指示を追加します。

1. 左側のナビゲーションペインの [**構築**] セクションで、[**エージェント**] をクリックします。
1. **shopping-assistant** エージェントのリンクをクリックします。
1. <span style="ssb_orange_oval">[**エージェントビルダーで編集**]</span> をクリックします。
1. [**ナレッジベース**] セクションまでスクロールして、<span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">[**追加**]</span> をクリックします。
1. [**ナレッジベースを選択**] で**shopping-kb** を選択します。
1. [**エージェント向けのナレッジベースの指示**] に `顧客が商品の説明、商品の評価、または入手可能な商品について質問したときに、ナレッジベースにアクセスします。` と入力します。
1. <span style="ssb_orange_oval">[**追加**]</span> をクリックします。
1. 画面の一番上までスクロールして <span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">[**保存**]</span> をクリックします。

<i aria-hidden="true" class="far fa-thumbs-up" style="color:#008296"></i> **タスク完了:** ナレッジベースを確認し、エージェントにアタッチできました。

---

## タスク 3: エージェントの Lambda 関数を設定する

このタスクでは、料金検索と簡単な計算機能を提供する、事前構築済みの Lambda 関数を使用するようにエージェントを設定します。まず、その Lambda 関数のコードと**リソースベースのポリシー**を確認します。

### タスク 3.1: ShoppingAssistantFunction を調べる

1. AWS マネジメントコンソール上部の検索バーで、`Lambda` と検索してクリックします。
1. [**関数**] のリストから **ShoppingAssistantFunction** を選択します。
1. [**コード**] セクションで、コードの内容を調査して仕組みを理解します。
   1. 75 行目には、`lambda_handler` と呼ばれる Lambda 関数のエントリポイントがあります。
   1. 81 行目と 83 行目では、LLM が `function` フィールドで選択した値に基づき、2 つの関数のどちらを使用するかを判断しています。
   1. 51 行目では `PriceLookup` 関数を定義しており、これは架空の製品情報を提供します。この関数は、まずエージェント経由で LLM によって提供されたパラメータ内の `productId` を取得します。次に、架空の小規模データベース内で対応する料金を検索します。そのため、エージェントでアクショングループを構築する際には、`productId` をパラメータとして定義しておくことが重要になります。この部分は通常、製品情報が格納されている外部データベースを呼び出す処理になっており、それによって LLM が最新の製品データにアクセスできるようになります。
   1. 3 行目では `MultiFunctionCalculatorTool` 関数を定義しており、これは足し算、引き算、掛け算、割り算を行います。左辺の値を示す `oper1`、右辺の値を示す `oper2`、演算子を示す `operator` を取得し、それに応じた計算処理を行います。次に、指定された内容に基づいて、適切な数学関数を呼び出します。そのため、エージェントでアクショングループを構築する際には、`oper1`、`oper2`、`operator` を各パラメータとして定義しておくことが重要になります。
1. [**コードソース**] セクションの上にある [**設定**] タブをクリックします。
1. 左側のナビゲーションメニューで [**アクセス権限**] を選択します。
1. [**リソースベースのポリシーステートメント**] セクションで、唯一のステートメントの横にあるラジオボタンをクリックします。
1. <span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">ポリシーの表示</span> をクリックします。
1. `bedrock.amazonaws.com` というプリンシパルサービスに、[**リソース**] フィールドで定義されている特定の関数に対して、`lambda:InvokeFunction` アクションを許可するポリシーが設定されているのを確認できます。このポリシーには、アカウントのリージョン内にあるすべてのエージェントの ARN を許可するという条件があります。そのため、エージェントのロールが関数を呼び出せるようにする必要はありません。通常は、アカウント内の特定のエージェントのみがポリシーを使用できるよう、このポリシーをより具体的に設定します。
1. [**閉じる**] をクリックしてポリシーの表示を閉じます。

### タスク 3.2: エージェントにアクショングループを追加する

**ShoppingAssistantFunction** の動作が理解できたので、次はこれをエージェントで使用できるように設定します。

1. AWS マネジメントコンソール上部の検索バーで、`Amazon Bedrock` と検索してクリックします。
1. 左側のナビゲーションペインの [**構築**] セクションで、[**エージェント**] をクリックします。
1. **shopping-assistant** エージェントのリンクをクリックします。
1. <span style="ssb_orange_oval">[**エージェントビルダーで編集**]</span> をクリックします。
1. [**アクショングループ**] セクションまでスクロールして、<span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">[**追加**]</span> をクリックします。
1. [**アクショングループ名を入力**] に `shopping-assistant-ag` と入力します。
1. [**説明 - オプション**] に `基本的な商品クエリ機能を実装するアクショングループ` と入力します。
1. OpenAPI 形式を使用する代わりに、[**関数の詳細で定義**] を使用して関数パラメータを定義します。
1. [**アクショングループの呼び出し**] で [**既存の Lambda 関数を選択してください**] を選択します。
1. [**Lambda 関数を選択**] で `ShoppingAssistantFunction` を選択します。
1. [**Action group function 1**] セクションの右上にある [**JSON エディタ**] をクリックします。
1. テキストボックスに次のコードを入力します。

   ```json
   {
       "name": "PriceLookup",
       "description": "商品の価格を調べるときに便利です。商品IDまたは商品名を入力してください。",
       "parameters": {
           "productId": {
               "description": "product identifier",
               "required": "True",
               "type": "String"
           }
       },
       "requireConfirmation": "DISABLED"
   }
   ```

   * `name`は、Lambda 関数を呼び出す際の `function` プロパティに使用され、コード内で 2 つの関数のどちらを呼び出すかを判断します。
   * `productId` パラメータは、関数の内部データベースでどの製品 ID を検索するかを決定するために使用されます。このパラメータは必須であり、型は `String` です。
1. [**Action group function 1**] の定義の下にある <span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">[**アクショングループ関数を追加**]</span> をクリックして 2 番目の関数を追加します。
1. [**Action group function 2**] セクションの右上にある [**JSON エディタ**] をクリックします。
1. テキストボックスに次のコードを入力します。

   ```json
   {
       "name": "MultiFunctionCalculatorTool",
       "description": "2つの数値を加算、減算、乗算、または除算する必要がある場合に便利です。このツールを使用するには、数値と演算子の両方を指定する必要があります。",
       "parameters": {
           "oper1": {
               "description": "first operand",
               "required": "True",
               "type": "String"
           },
           "oper2": {
               "description": "second operand",
               "required": "True",
               "type": "String"
           },
           "operator": {
               "description": "operator",
               "required": "True",
               "type": "String"
           }
       },
       "requireConfirmation": "DISABLED"
   }
   ```

   * `name` は `function` プロパティに使用されます。
   * `oper1`、`oper2`、`operator` の必須となる文字列パラメータがすべて定義され、Lambda 関数で使用できるようになっています。

1. <span style="ssb_orange_oval">[**作成**]</span> をクリックします。

1. 画面の一番上までスクロールして <span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">[**保存**]</span> をクリックします。

<i aria-hidden="true" class="far fa-thumbs-up" style="color:#008296"></i> **タスク完了:** 料金検索と簡単な計算機能を提供する事前構築済みの Lambda 関数を、エージェントで利用できるよう設定できました。

---

## タスク 4: エージェントのガードレールを設定する

このタスクでは、事前構築済みのガードレールをエージェントに適用します。まず、設定済みのガードレールを確認します。

### タスク 4.1: ガードレールを確認する

1. 左側のナビゲーションペインの [**構築**] セクションで、[**ガードレール**] をクリックします。
1. **shopping-assistant-guardrail** エージェントのリンクをクリックします。
1. [**作業中のドラフト**] セクションで [**作業中のドラフト**] をクリックします。
1. 各セクションをそれぞれ確認します。
   1. **コンテンツフィルター**: コンテンツフィルターは追加されていませんが、<span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">編集</span> をクリックして設定を確認できます。
   1. **拒否トピック**:
      1. [**拒否トピック**] の横にある <span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">編集</span> をクリックします。
      1. [**Lawn Maintenance Advice**] の横にあるチェックボックスをします。
      1. <span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">編集</span> をクリックします。
      1. [**サンプルフレーズの追加 - オプション**] セクションには、ガードレールがどのようなトピックを拒否すべきかを知るのに役立つ、3 つのサンプルフレーズがあります。
      1. [**キャンセル**] をクリックします。
      1. [**終了**] をクリックします。
   1. **ワードフィルター**: 冒涜的な表現やカスタム単語とフレーズが含まれています。ワードフィルターは追加されていませんが、<span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">編集</span> をクリックして設定を確認できます。
   1. **機密情報フィルター**: PII タイプと正規表現パターンが含まれており、該当するタブをクリックすると確認できます。PII タイプと正規表現パターンは追加されていませんが、<span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">編集</span> をクリックして設定を確認できます。
   1. **コンテキストグラウンディング**:コンテキストグラウンディングチェックは追加されていませんが、<span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">編集</span> をクリックして設定を確認できます。
   1. **ブロックされたメッセージ**:プロンプトがブロックされた際に送信されるメッセージを確認できます。このメッセージは、後のセクションでも再び登場するため、覚えておいてください。

### タスク 4.2: ガードレールをテストする

1. 画面右側に [**テスト**] セクションが表示されているはずです。表示されない場合は、ページ上部の <span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">テスト</span> をクリックします。
1. [**テスト**] セクションで <span style="ssb_orange_oval">[**モデルを選択**]</span> をクリックします。
1. [**モデルを選択**] ウィンドウの [**カテゴリ**] で、[**Anthropic**] を選択します。
1. [**モデル**] で [**Claude 3 Haiku**] を選択します。
1. <span style="ssb_orange_oval">[**適用**]</span> をクリックします。
1. [**プロンプト**] テキストボックスに `Can I use a string trimmer to control weeds?` というテキストを入力します。覚えているかと思いますが、このプロンプトは拒否トピックで指定した**サンプルフレーズ**には含まれていません。つまり、考えられるすべての拒否ケースをサンプルとして登録しておく必要はありません。
1. <span style="ssb_orange_oval"><i class="fas fa-caret-right"></i> [**実行**]</span> をクリックします。
1. [**最終応答**] に、先ほど確認したブロックされたメッセージが表示されます。
1. <span style="color:#855900">**介入 (1 インスタンス)**</span> の横にある <span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">[**トレースを表示**]</span> をクリックします。
1. [**拒否トピック**] で、**Lawn Maintenance Advice** が<span style="color:#855900"> **ブロック済み**</span> かつ **Detected: TRUE** になっていることが確認できます。

### タスク 4.3: エージェントのガードレールを設定する

ガードレールの機能が確認できたので、エージェントに適用しましょう。

1. 左側のナビゲーションペインの [**構築**] セクションで、[**エージェント**] をクリックします。
1. **shopping-assistant** エージェントのリンクをクリックします。
1. <span style="ssb_orange_oval">[**エージェントビルダーで編集**]</span> をクリックします。
1. [**ガードレールの詳細**] セクションまでスクロールして <span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">[**編集**]</span> をクリックします。
1. [**ガードレールを選択**] で **shopping-assistant-guardrail** を選択します。
1. [**ガードレールバージョン**] で **1** を選択します。
1. <span style="ssb_orange_oval">[**保存して終了**]</span> をクリックします。
1. 画面の一番上までスクロールして <span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">[**保存**]</span> をクリックします。

<i aria-hidden="true" class="far fa-thumbs-up" style="color:#008296"></i> **タスク完了:** 事前構築済みのガードレールをエージェントに適用できました。

---

## タスク 5: エージェントのメモリを設定する

このタスクでは、エージェントの短期メモリと長期メモリを設定します。

### タスク 5.1: エージェントの短期メモリを設定する

このタスクでは、***アイドルセッションタイムアウト***を設定し、120 秒に下げます。デフォルトでは 600 秒です。つまり、同じ**セッション ID**を使用している場合、エージェントは過去 10 分間の会話を短期メモリとして保持するため、コード内でメモリを管理する必要はありません。ただし、このラボの目的にとって 10 分は長すぎるため、セッションを短時間でタイムアウトする必要があります。そうすることで、セッション内容を要約して次のセクションで設定する長期メモリにコミットできるようにします。

1. [**エージェントの詳細**] セクションの下部にある <span style="font-weight: bold"> **その他の設定**</span> を展開します。
1. [**アイドルセッションタイムアウト**] を `120` **秒**と入力します。
1. 一番上までスクロールして <span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">[**保存**]</span> をクリックします。

### タスク 5.2: エージェントの長期メモリを設定する

このタスクでは、エージェントの長期メモリを有効にして、セッションが提供できる情報以上の内容を保持できるようにします。セッションがタイムアウトすると、基盤モデルを使用してセッションの会話 (短期メモリ) を要約します。これにより、会話の履歴を簡潔にまとめ、今後の呼び出しに使用するトークン数を減らすことができます。

1. [**メモリ**] セクションまでスクロールして [**有効**] をクリックします。
1. 残りの設定は変更しません。
1. 画面の一番上までスクロールして <span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">[**保存**]</span> をクリックします。

<i aria-hidden="true" class="far fa-thumbs-up" style="color:#008296"></i> **タスク完了:** エージェントの短期メモリと長期メモリを設定できました。

---

## タスク 6: エージェントの準備、テスト、デプロイを行う

このタスクでは、エージェントを準備してテストし、デプロイします。

### タスク 6.1: エージェントを準備してテストする

エージェントの設定がすべて完了したので、次はエージェントをテストします。まずは、エージェントを**準備**する必要があります。その後、いくつかのテストを実行します。

1. 一番上までスクロールして <span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">[**準備**]</span> をクリックします。

1. ボタンがグレーになっている場合は、先に <span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">[**保存**]</span> をクリックしてから <span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">[**準備**]</span> をクリックします。

1. <span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">[**テスト**]</span> をクリックします。

1. 画面右側の [**テストエージェント**] セクションで、「**ここにメッセージを入力**」と表示されたテキストボックスに `こんにちは。貴社の商品に興味があります。貴社が販売している商品の製造元を教えてください。` というプロンプトを入力します。

1. <span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">[**実行**]</span> をクリックします。

1. LLM から指示された後にエージェントがナレッジベースと通信し、エージェントの応答メッセージが表示されます。これを検証するには、応答の下部にある **トレースを表示** をクリックします。
1. 画面右側の [**トレース**] セクションで [**前処理トレース**] タブをクリックし、<span style="font-weight: bold">**トレース ステップ 1**</span> を展開します。
1. ガードレールが適用されているものの、何もアクションが実行されなかったことがわかります (`action: NONE`)。
1. [**オーケストレーションとナレッジベース**] タブには、次の 2 つのトレースがあります。
   * <span style="font-weight: bold">**Trace step 2**</span>: これを展開すると、`modelInvocationInput` でエージェントがまず LLM と通信していることがわかります。次に、`modelInvocationOutput` で LLM にナレッジベースの使用を求め、その定義は `rationale` で明確に示されています。その後、`invocationInput` でエージェントがナレッジベースを呼び出します。このとき `text` は、送信した元のプロンプトとは異なることに注意してください。`observation` にナレッジベースの応答が記録されます。
   * <span style="font-weight: bold">**Trace step 3**</span>: これを展開すると、`modelInvocationInput` でエージェントが LLM を呼び出し、先程のトレースで得られたナレッジベースの `content` を渡していることがわかります。次に、`modelInvocationOutput` で LLM から回答が得られます。その内容は `observation` で簡単に確認できます。

1. [**後処理トレース**] タブで <span style="font-weight: bold">**トレース ステップ 4**</span> を展開します。
1. ガードレールが適用されたことが確認できます。
1. 上記と同じ手順を、次のような追加のプロンプトで繰り返し実行すると、アクショングループとガードレールを呼び出すことができます。
   * `「String Trimmer」の価格を教えてください。` は、**PriceLookup** 関数をトリガーします。
   * `「String Trimmer」を2つ購入するといくらかかりますか?` は、**MultiFunctionCalculatorTool** 関数をトリガーします。
   * `Can I use a string trimmer to control weeds?` は、ガードレールをトリガーします。

### タスク 6.2: エージェントのバージョンとエイリアスを作成する

これで、ナレッジベース、2 つの関数、ガードレール、短期セッションメモリ、長期メモリを使用できる動作中の Amazon Bedrock Agent が完成しました。次はこの動作中のエージェントのバージョンを作成し、そのバージョンに `prod` というエイリアスを作成します。

1. 左側のナビゲーションペインの [**構築**] セクションで、[**エージェント**] をクリックします。
1. **shopping-assistant** エージェントのリンクをクリックします。
1. [**エイリアス**] セクションまでスクロールして <span style="ssb_blue_oval; background-color:#ffffff; font-weight:bold; font-size:90%; color:#0872D3; position:relative; top:-1px; padding-top:3px; padding-bottom:3px; padding-left:10px; padding-right:10px;  border-radius:20px; border-color:#0872D3; border-style:solid; border-width:2px; margin-right:5px; white-space:nowrap">[**作成**]</span> をクリックします。
1. [**エイリアス名**] に `prod` と入力します。

<i aria-hidden="true" class="fas fa-exclamation-circle" style="color:#7C5AED"></i> **警告:** エージェント名は必ず **prod** にします。そうしないと、後のタスクで JupyterLab Notebook を実行する際に問題が発生します。誤った名前で作成した場合は、上記の手順をもう一度実行して新しいエイリアスを作成できます。

1. その他の設定は変更せず、[**新しいバージョンを作成し、このエイリアスに関連付けます。**] を選択した状態にしておきます。
1. <span style="ssb_orange_oval">[**エイリアスを作成**]</span> をクリックします。

<i aria-hidden="true" class="fas fa-sticky-note" style="color:#563377"></i> **注意:** タスク 6.1 のテストを再実行することもできますが、テストを実行してから設定を何も変更していないため、動作は既に確認したとおりです。

<i aria-hidden="true" class="far fa-thumbs-up" style="color:#008296"></i> **タスク完了:** エージェントの準備、テスト、デプロイが完了しました。

---

## タスク 7: Amazon SageMaker Studio アプリケーションを起動する

1. この手順の左側にある **SageMakerStudioUrl** の値をコピーします。

1. ブラウザの新しいタブを開き、コピーした **SageMakerStudioUrl** にアクセスします。

これにより、**JupyterLab** ワークスペースインターフェイスが表示されます。

<i aria-hidden="true" class="fas fa-sticky-note" style="color:#563377"></i> **注意:** 初回の起動時は、JupyterLab ワークスペースインターフェイスがロードされるまでに 1～2 分かかる場合があります。

<i aria-hidden="true" class="far fa-thumbs-up" style="color:#008296"></i> **タスク完了:** SageMaker Studio アプリケーションを起動できました。

---

## タスク 8: ノートブック経由でエージェントと対話する

エージェントの構築、テスト、デプロイが **prod** 環境で完了したので、次は AWS SDK を使用して実際にエージェントを使用します。このタスクでは、Amazon SageMaker Studio アプリケーションを起動し、JupyterLab Notebook にアクセスしてコードを実行します。

このタスクでは、ノートブックファイル **Task_ja_jp.ipynb** を実行し、アプリケーションで Bedrock Agent を使用する練習を行います。エージェントを使用して、メーカー、説明、評価などの製品詳細を含むナレッジベースにアクセスします。さらに、エージェントは簡単な計算と料金検索を行う機能にもアクセスできます。

1. 左側のメニューから **Task_ja_jp.ipynb** をダブルクリックしてノートブックを開きます。

1. **Task_ja_jp.ipynb** ノートブックを注意深く進め、各コードセルを実行し、その出力を表示します。セルを実行するには、セル内をクリックして **Shift+Enter** を押すか、ページ上部にある **実行ボタン** をクリックします。

<i aria-hidden="true" class="fas fa-sticky-note" style="color:#563377"></i> **注意:** ノートブックの実行が終了したら、ここに戻ってラボを終了してください。

<i aria-hidden="true" class="far fa-thumbs-up" style="color:#008296"></i> **タスク完了:** **Task_ja_jp.ipynb** 内のすべてのセルを実行して、エージェントが料金検索などの情報をナレッジベースから収集したり、基本的な数学計算を実行したりできるようになりました。

---

## まとめ

次の作業を完了しました。

- Amazon Bedrock エージェントを作成する
- エージェントを Amazon Bedrock ナレッジベースと統合する
- エージェントを Amazon Bedrock ガードレールと統合する
- エージェントを AWS Lambda 関数と統合する
- ナレッジベースとガードレールがエージェントとどのように相互作用するかを分析する
- アクショングループ、メモリ、ガードレールなどのエージェントのコンポーネントを分析する
- メモリ、関数、ナレッジベース、ガードレールにアクセスできるエージェントを使用するアプリケーションを構築する
- トレースをキャプチャして分析し、エージェントの動作を理解する
