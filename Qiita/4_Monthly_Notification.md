---
title: 【GitHub Actions】Pythonで作ったツールを自動化して、毎月メールでレポートを受け取る方法【投資アルゴリズム第4回】  
---
tags:
  - Python
  - GitHubActions
  - 自動化
  - 投資
private: false
---

## はじめに

こんにちは！ドルコスト平均法を超えるアルゴリズムを検証するシリーズ、第4回です！

さて、個人開発をしていたらいろいろ自動化したくなると思います。

今回は、毎月投資額を自動でメールに通知してくれるワークフローを作成しました。

当初は　
**「楽天証券の取引を全自動化したい！」**
と考えていました。
しかし、いざ自動売買へ！と意気込んだものの、すぐに現実の壁にぶつかります。

- **APIの壁...**: 手軽に使えるWeb APIのようなものが提供されておらず、公式ツール「マーケットスピード」経由での自動化も不可能ではないものの、実装がかなり複雑でシンプルじゃない...
- **安定性の問題**: 無理に作っても、ツールの仕様変更などで動かなくなる可能性があり、安定した運用が難しい。
- **そもそも難易度が高い**: 正直、そこまで作り込むのは大変すぎる！

しかし！

**「完全自動売買は無理でも、投資判断の"半"自動化ならできるじゃないか！」**

それなら簡単です。こちらでメッセージを用意してあげて自動送信できるツールを選べばいいだけです。

AIと壁打ちした結果、Github Actionsでaction send mailを使うことにしました。

この記事では、その過程で構築した**「PythonツールをGitHub Actionsで定期実行し、結果をメールで受け取る」**という、汎用性が高い自動化の仕組みを紹介します。

この方法を使えば、自分のPCの電源がオフでも、決まった日時にクラウド上で処理を実行してくれるようになります。

## 完成イメージ

この仕組みが完成すると、毎月1日になると、以下のような分析結果のメールが自動で届くようになります。

```text
Date: 2025-09-01
Ticker: SPY
Base Amount: JPY 40,000.00
--------------------
Latest Close Price: JPY 543.21
Actual Reference Price: JPY 456.78
Calculated Investment Amount: JPY 35,000.00
```

これで、毎月いくら投資すればいいか一目瞭然です。

## 使っている技術スタック

今回の仕組みは、主に3つの技術で成り立っています。

- **Python**: 株価データを取得し、独自のAAVCアルゴリズムで投資額を計算するコア部分。
- **GitHub Actions**: スクリプトの定期実行とメール送信の自動化を担当する、今回の主役。GitHubリポジトリで使える超便利な自動化機能です。
- **SMTP (Gmailなど)**: `action-send-mail`という便利なActionを利用して、計算結果をメールで送信します。

## 実装の3ステップ

それでは、具体的な実装方法を見ていきましょう。

### STEP 1: 計算と通知メッセージを生成するPythonスクリプト 📝

まずは、投資額を計算してメールの本文を作る `notification_sender.py` というPythonスクリプトを用意します。

このスクリプトがやっていることは、とてもシンプルです。

1.  `config.yaml` から計算対象の銘柄（TICKER）や基準額（AMOUNT）を読み込む。
2.  株価データを取得し、AAVCアルゴリズムで投資額を計算する。
3.  計算結果を、人間が読みやすいように整形して「通知メッセージ」を作成する。
4.  作成したメッセージを、後続のGitHub Actionsのステップで使えるように**出力変数として設定**する。

特に重要なのが4番目です。Pythonスクリプトの実行結果を、次の「メール送信」のステップに渡すための橋渡し役となります。

### STEP 2: 自動化の心臓部！GitHub Actionsのワークフロー

次に、自動化の全体設計図となるワークフローファイルを `.github/workflows/monthly_notification.yml` という名前で作成します。

```yaml
name: Monthly Investment Notification

on:
  # 毎月1日のUTC 0時0分（日本時間午前9時）に実行
  schedule:
    - cron: '0 0 1 * *'
  # 手動実行も可能にする
  workflow_dispatch:

jobs:
  build-and-notify:
    runs-on: ubuntu-latest
    steps:
      # 1. ソースコードを仮想環境に持ってくる
      - name: Checkout repository
        uses: actions/checkout@v4

      # 2. Python環境を準備する
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      # 3. 必要なライブラリをインストールする
      - name: Install dependencies
        run: pip install -r requirements.txt

      # 4. STEP1のPythonスクリプトを実行する
      - name: Run calculation script
        id: calculate # このステップに'calculate'というIDを付ける
        run: python src/AAVC_calculate_tool/notification_sender.py

      # 5. メールを送信する
      - name: Send mail
        uses: dawidd6/action-send-mail@v3
        with:
          # ... (サーバー情報など) ...
          subject: '【月次投資額通知】AAVC自動計算レポート'
          # ↓ ここが重要！前のステップの出力を本文に指定
          body: ${{ steps.calculate.outputs.notification_body }}
          to: ${{ secrets.MAIL_TO }}
          from: AAVC Calculate Tool
```

このファイルのポイントは2つです。

- **`on.schedule.cron`**: `0 0 1 * *` と書くことで、「毎月1日の0時0分(UTC)に実行してね」というスケジュールを設定できます。（日本時間だと午前9時）
- **`body: ${{ steps.calculate.outputs.notification_body }}`**: メール送信ステップの`body`に、前の`calculate`ステップの出力(`outputs.notification_body`)を指定しています。これにより、Pythonスクリプトが生成したメッセージがメール本文にセットされます。

### STEP 3: パスワードを安全に管理するGitHub Secrets

パスワードなどを置いておくのは **GitHub Secrets** です。これは、パスワードなどの機密情報をリポジトリに安全に保存できる機能です。

設定は簡単です。
1.  お使いのGitHubリポジトリの **`Settings`** タブを開きます。
2.  左側のメニューから **`Secrets and variables` > `Actions`** を選択します。
3.  `New repository secret` ボタンから、以下の情報をポチポチ登録していきます。

| Secret名          | 設定する値の例                     | 説明                               |
| ----------------- | ---------------------------------- | ---------------------------------- |
| `MAIL_SERVER`     | `smtp.gmail.com`                   | お使いのメールサーバー             |
| `MAIL_PORT`       | `587`                              | メールサーバーのポート番号         |
| `MAIL_USERNAME`   | `your.email@gmail.com`             | メールアドレス（ユーザー名）       |
| `MAIL_PASSWORD`   | `xxxxxxxxxxxxxxxx`                 | メールパスワード or **アプリパスワード** |
| `MAIL_TO`         | `notify.me@example.com`            | 通知を受け取りたいメールアドレス   |

こうすることで、ワークフローファイルからは `${{ secrets.MAIL_PASSWORD }}` のように、安全にパスワードを呼び出すことができます。

####　「アプリパスワード」とは？

ここは自分も知らなかった部分なのですが、Gmailもアカウントをサードパーティーのサービスなどで操作する場合はアプリパスワードなるものが推奨されているようです。

どうやら通常のGoogleアカウントのパスワードではなく、2段階認証を設定した上で生成できるものです。

やっていなかったので2段階認証を設定してから生成して、Github Secretsに登録しました。

## まとめ

- **PCレスで自動実行**: 自分のPCを起動していなくても、毎月自動で計算が実行される！
- **安全なパスワード管理**: GitHub Secretsのおかげで、機密情報をコードから分離できた！
- **柔軟な連携**: Pythonの実行結果を、後続のActionに簡単に渡せるので、応用が効く！

このGitHub Actionsの使い方は、今回のメール通知以外にも、アイデア次第で本当に色々な自動化ができるなあと思いました。

今まではCICDパイプラインしか作ったことがなかったので目に鱗でした。

---

### 過去の記事

- [第1回: ドルコスト平均法に勝るアルゴリズムのアイデア](https://qiita.com/rikutoyamada01/items/d5e9c00166b1a68f7856)
- [第2回: AAVC・DCA・一括投資の3つの相場での実力検証](https://qiita.com/rikutoyamada01/items/3942c3a26e3f4e6b7b5a)
- [第3回: AAVC発展戦略と長期シミュレーション比較分析](https://qiita.com/rikutoyamada01/items/e0734ea441f17fad55b0)

### ProjectのGithub
本プロジェクトはオープンソースです。改善のアイデアやコントリビュートは大歓迎です！
https://github.com/rikutoyamada01/AAVC_calculate_tool
