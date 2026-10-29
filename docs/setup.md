# セットアップガイド: AIツールから blueqat MCP を使えるようにする

Claude や Codex などのAIツールを [blueqat MCP](https://mcp.blueqat.app) につなぎ、日本語で頼むだけで
量子コンピュータ（シミュレータ・実機）を動かせるようにするまでの手順です。
ワークショップの事前準備にも、そのまま使えます。

> 2026-10-29 時点の画面・コマンドで書いています。各サービスの画面や料金は変わることがあります。

## 全体の流れ

1. **blueqat のアカウントを作り、APIキーを発行する**（全員共通・約5分）
2. **GUI（アプリ・ブラウザ）か CLI（ターミナル）かを選ぶ**
3. **AIツールを1つ入れて、blueqat MCP を登録する**（約15〜30分）
4. **接続確認のプロンプトを試す**

どのツールを選んでも、できることは同じです。

### blueqat MCP とは

AIツールが blueqat の量子コンピュータを操作できるようにする仕組みです（MCP = Model Context Protocol）。
一度つなげば、「コイントスする量子回路を作って実行して」と頼むだけで、AIが量子回路を組んで実行してくれます。
SDK や Python のインストールは要りません。

---

## 0. おすすめの組み合わせ

| OS | GUI（迷ったらこちら） | CLI |
| :--- | :--- | :--- |
| **Windows** | Claude Desktop（またはブラウザの claude.ai） | **WSL（Ubuntu）** の中で Claude Code / Codex CLI / Antigravity CLI |
| **macOS** | Claude Desktop（またはブラウザの claude.ai） | 「ターミナル」アプリで Claude Code / Codex CLI / Antigravity CLI |
| **Linux** | ブラウザの claude.ai | 端末（ターミナル）で Claude Code / Codex CLI / Antigravity CLI |

**GUI と CLI のどちらにするか**

- **GUI**: コマンド操作に慣れていない人向け。インストールなしでも、ブラウザだけで使えます。Claude の無料プランで始められます。
- **CLI**: ターミナルに慣れている人、プロンプトや結果をファイルや Git で管理したい人向け。
  このリポジトリの例題は、すべて WSL の Ubuntu 24.04 上の Claude Code（CLI）で作って実行しています。

**Windows で CLI を使う場合は WSL をおすすめします。** CLI ツールの多くは PowerShell 版もありますが、
このガイドのコマンドは WSL・macOS・Linux で共通になるように書いています。

| ツール | 種類 | 必要なアカウント・料金 |
| :--- | :--- | :--- |
| **Claude**（claude.ai / Claude Desktop） | GUI | Claude アカウント。無料プランで可 |
| **Claude Code** | CLI | Claude の有料プラン（Pro 以上） |
| **Codex CLI** | CLI | ChatGPT アカウント（使えるプランは [公式ドキュメント](https://learn.chatgpt.com/docs/codex/cli) で確認してください） |
| **Antigravity CLI** | CLI | Google アカウント（無料枠あり） |

> 各サービスには、年齢条件などの利用条件があります。登録する前に、それぞれの利用規約を確認してください。

---

## 1. blueqat のアカウントを作り、APIキーを発行する（全員共通）

### 1-1. アカウントを作る

1. [mcp.blueqat.app/login](https://mcp.blueqat.app/login)（「ログイン・新規登録」画面）を開く
2. 次のどれかで登録する。どれも無料で、初めてでもそのまま登録されます
   - **「Googleで続ける」**
   - **「GitHubで続ける」**
   - **「メールアドレスで新規登録（無料）」**
3. ログインできたら、[mcp.blueqat.app/account](https://mcp.blueqat.app/account)（「アカウント」画面）を開く

### 1-2. アカウント画面の見方

アカウント画面には、上から次の項目が並んでいます。このガイドで使うのは **「APIキー」** だけです。

| 項目 | 内容 | このガイドでの扱い |
| :--- | :--- | :--- |
| プラン表示（FREE など）と **「プランを管理」** | 今のプランの確認、有料プランへの切り替え | 無料（FREE）のままで大丈夫です |
| **今月の利用状況** | 実機ジョブの回数、シミュレータの実行回数・ゲート数・ショット数・計算時間の合計。毎月1日（UTC）にリセット | 動いたかどうかの確認に使えます |
| **現在のプランの上限** | 量子ビット数・ショット数などの上限 | 上限が気になったらここを見ます |
| **JPYCで支払う** | 実機ジョブを1件ずつ JPYC（暗号資産）で支払う機能。ウォレット（MetaMask）を接続して使う | **使いません**。実機の有料投入は、投入後のキャンセル・返金ができません |
| **実機ジョブの履歴** | 実機に投入したジョブの一覧と結果 | 使いません |
| **アクセストークン** | 「アクセストークン」（有効期限 約2時間）と「リフレッシュトークン」（約30日）。「再ログイン」で更新 | **使いません**。すぐ失効します |
| **APIキー** | 有効期限のない長期キー。「新しいキーを発行」で作り、「失効」で無効にする | **これを使います** |

### 1-3. APIキーを発行する

1. アカウント画面の **「APIキー」** の欄で **「新しいキーを発行」** を押す
2. 「キーの名前（任意）」を聞かれるので、あとで見分けられる名前を入れる（例: `my-laptop`）。空欄でも構いません
3. **「新しいキー（この画面を離れると二度と表示されません）」** に表示されたキーを **「コピー」** し、
   パスワード管理アプリやメモ帳など、自分だけが見られる場所に保存する
   - 画面を離れると二度と表示されません。なくしたら、新しいキーを発行し直してください

**「アクセストークン」の欄のトークンは使わないでください。** 約2時間で失効するので、前もって設定しておくと使うときには切れています。

**APIキーはパスワードと同じです。** SNS・チャット・スクリーンショット・AIとの会話に貼らないでください。
人に見られたかもしれないときは、アカウント画面の「APIキー」の一覧でそのキーの **「失効」** を押してください（反映まで最大1分ほどかかります）。

### 1-4. 無料プランの上限

アカウント画面の「現在のプランの上限」で確認できます。2026-10-29 時点の
[トップページ](https://mcp.blueqat.app) の表記は次のとおりです（変わることがあります）。

| 項目 | 無料プラン |
| :--- | :--- |
| 量子ビット数（シミュレータ） | 10 以下 |
| ショット数（測定回数） | 256 以下 |
| 1回路のゲート数 | 200 以下 |
| タイムアウト | 10 秒 |
| 実機（量子コンピュータ）での実行 | 月10回まで |

シミュレータの実行回数には月の上限はありません（1回ごとの上限とタイムアウトがかかります）。
詳しくは [tiers_and_pricing.md](tiers_and_pricing.md) を参照してください。

---

## 2. 接続先（全ツール共通）

どのツールでも、登録する内容は次の2つです。

- **URL**: `https://mcp.blueqat.app/mcp`
- **ヘッダー**: `Authorization: Bearer <APIキー>`

以下の手順の `<APIキー>` は、1-3 でコピーした APIキーに置き換えてください（`<` `>` は入れません）。
`Bearer` と APIキーの間には **半角スペースが1つ** 入ります。

---

## 3. GUI: Claude（claude.ai / Claude Desktop）

### 3-1. 準備

1. [claude.ai](https://claude.ai) で Claude のアカウントを作る（無料プランで可）
2. 使い方を選ぶ
   - **Windows / macOS**: [Claude Desktop](https://claude.ai/download) をインストールしてログインする（ブラウザのままでも構いません）
   - **Linux**: ブラウザで claude.ai を使う

### 3-2. blueqat MCP を登録する

1. 「設定」→「コネクタ」を開き、「カスタムコネクタを追加」を選ぶ
2. URL に `https://mcp.blueqat.app/mcp` を入力する
3. リクエストヘッダーに `Authorization: Bearer <APIキー>` を設定して保存する

- ブラウザ版とデスクトップ版のどちらで登録しても、同じアカウントなら両方で使えます。
- 無料プランでは、追加できるカスタムコネクタの数に制限があります。ほかのコネクタを登録済みで追加できないときは、使っていないものを外してください。
- 会話で初めて blueqat のツールが使われるとき、使用の許可を求められます。「許可」を選んでください。

登録できたら [6. 接続確認](#6-接続確認全員) へ進んでください。

---

## 4. CLI の準備（OS ごと）

CLI ツールを入れる前に、ターミナルを用意し、APIキーを環境変数に入れておきます。

### 4-1. Windows: WSL（Ubuntu）を入れる

1. スタートメニューで「PowerShell」を右クリックし、**「管理者として実行」** で開く
2. 次のコマンドを実行する

   ```powershell
   wsl --install
   ```

3. 案内に従って PC を再起動する
4. スタートメニューから **「Ubuntu」** を開き、ユーザー名とパスワードを決める（パスワードは入力しても画面に表示されません）
5. Ubuntu の画面で、次を実行して最新にしておく

   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

以降のコマンドは、すべて **Ubuntu の画面（WSL）** で実行します。PowerShell ではありません。

- `wsl --install` が失敗する場合は、BIOS/UEFI で仮想化（Intel VT-x / AMD-V）が有効になっているか確認してください。
- 詳しくは Microsoft の [WSL のインストール](https://learn.microsoft.com/ja-jp/windows/wsl/install) を参照してください。

### 4-2. macOS: ターミナルを開く

「アプリケーション」→「ユーティリティ」→ **「ターミナル」** を開きます（Spotlight で「ターミナル」と検索しても開けます）。
macOS の標準のシェルは zsh なので、以下の `~/.bashrc` は **`~/.zshrc`** に読み替えてください。

### 4-3. Linux: 端末を開く

いつもの端末（ターミナル）を開きます。`curl` が入っていなければ入れてください（Ubuntu なら `sudo apt install -y curl`）。

### 4-4. APIキーを環境変数に入れる（共通）

APIキーを `BLUEQAT_API_KEY` という環境変数に入れておくと、どの CLI ツールでも同じ書き方で登録できます。

```bash
echo 'export BLUEQAT_API_KEY="<APIキー>"' >> ~/.bashrc   # macOS（zsh）は ~/.zshrc
source ~/.bashrc                                          # macOS（zsh）は ~/.zshrc
```

確認します（キーそのものは表示せず、文字数だけを表示します）。

```bash
echo ${#BLUEQAT_API_KEY}
```

`0` 以外の数字が出れば設定できています。`0` のときは、ターミナルを開き直してからもう一度確認してください。

---

## 5. CLI: ツールを入れて blueqat MCP を登録する

以下の3つから **1つ** 選んでください。コマンドは WSL・macOS・Linux で共通です。

### 5-A. Claude Code

Claude の有料プラン（Pro 以上）が必要です。

**インストールとログイン**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

インストールできたら `claude` を実行し、画面の案内に従って Claude アカウントでログインします。
ログインが終わったら `/exit` で一度終了します。

**blueqat MCP を登録する**

```bash
claude mcp add --transport http --scope user blueqat https://mcp.blueqat.app/mcp --header "Authorization: Bearer $BLUEQAT_API_KEY"
```

- `--scope user` を付けると、どのフォルダで `claude` を起動しても使えます。付けないと、コマンドを実行したフォルダでだけ使えます。
- `--header` は **最後** に書いてください。名前（`blueqat`）や URL より前に書くと、それらがヘッダーとして読まれてしまいます。
- `"..."` はダブルクォートのままにしてください。シングルクォートにすると `$BLUEQAT_API_KEY` が展開されず、認証に失敗します。

**接続を確認する**

```bash
claude mcp list
```

`blueqat: https://mcp.blueqat.app/mcp (HTTP) - ✔ Connected` と表示されれば成功です。
`claude` を起動して [6. 接続確認](#6-接続確認全員) のプロンプトを試してください（起動中に `/mcp` でも状態を確認できます）。

### 5-B. Codex CLI

ChatGPT のアカウントでログインして使います。

**インストールとログイン**

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

Node.js が入っている場合は、`npm install -g @openai/codex` でも入ります。
インストールできたら `codex` を実行し、「Sign in with ChatGPT」を選んでログインします。

**blueqat MCP を登録する**

Codex は、APIキーそのものではなく **環境変数の名前** を登録します（4-4 で設定した `BLUEQAT_API_KEY`）。

```bash
codex mcp add blueqat --url https://mcp.blueqat.app/mcp --bearer-token-env-var BLUEQAT_API_KEY
```

設定は `~/.codex/config.toml` に保存されます。Codex を起動するターミナルで `BLUEQAT_API_KEY` が設定されている必要があります。

**接続を確認する**

```bash
codex mcp list
```

`blueqat` が表示されたら、`codex` を起動して [6. 接続確認](#6-接続確認全員) のプロンプトを試してください。

### 5-C. Antigravity CLI

Google アカウントでログインして使います。

**インストールとログイン**

```bash
curl -fsSL https://antigravity.google/cli/install.sh | bash
```

インストールできたら `agy` を実行すると、ブラウザが開いて Google アカウントでログインできます。

**blueqat MCP を登録する**

```bash
agy mcp add -H "Authorization: Bearer $BLUEQAT_API_KEY" blueqat https://mcp.blueqat.app/mcp
```

- `-H` は **`blueqat` より前** に書いてください（Claude Code とは逆です）。後ろに書くとヘッダーが登録されません。
- 設定は `~/.gemini/config/mcp_config.json` に保存されます。

コマンドで登録できない場合は、`~/.gemini/config/mcp_config.json` を直接編集します。

```json
{
  "mcpServers": {
    "blueqat": {
      "serverUrl": "https://mcp.blueqat.app/mcp",
      "headers": {
        "Authorization": "Bearer <APIキー>"
      }
    }
  }
}
```

- キー名は `serverUrl` です（`url` や `httpUrl` では動きません）。
- このファイルでは `${BLUEQAT_API_KEY}` のような環境変数の書き方は使えません。APIキーをそのまま書いてください。

**接続を確認する**

`agy mcp list` で `blueqat` が `enabled` になっていても、APIキーが正しいかまでは分かりません。
`agy` を起動して [6. 接続確認](#6-接続確認全員) のプロンプトを試してください（起動中に `/mcp` でも状態を確認できます）。

---

## 6. 接続確認（全員）

AIツールに次のように話しかけてください。

```
Blueqat MCPで利用できるゲート一覧を教えて
```

H、X、RY、CNOT などのゲートの一覧が返ってくれば準備完了です（一覧は [gates.md](gates.md) にもあります）。

余裕があれば、量子コイントスも試してみましょう。

```
Blueqat MCPを使って、1量子ビットの重ね合わせ状態を作り、測定して0か1かのコイントスを100回行ってください
```

0 と 1 がだいたい半分ずつ出れば成功です。アカウント画面の「今月の利用状況」で、シミュレータの実行回数が増えていることも確認できます。

次は [ワークショップ進行ガイド](workshop.md) や、[README の使用例一覧](../README.md#使用例一覧) の例を試してみてください。

---

## うまくいかないとき

| 症状 | 確認すること |
| :--- | :--- |
| 401 エラー / 認証エラー | APIキーのコピーミス。`Bearer` の付け忘れ（`Bearer` の後ろに半角スペース）。「アクセストークン」（約2時間で失効）を使っていないか。キーを「失効」していないか |
| CLI で認証エラー | `echo ${#BLUEQAT_API_KEY}` が `0` になっていないか。環境変数を設定したあと、ターミナルを開き直したか |
| Claude Code で `Connected` にならない | `--header` をコマンドの最後に書いたか。`"..."` をダブルクォートにしたか |
| ツールが呼び出されない | ツールの使用許可のポップアップを見落としていないか。AIツールを再起動したか |
| WSL でログイン用のブラウザが開かない | ターミナルに表示された URL を Windows のブラウザに貼り付けて開く |
| `wsl --install` が失敗する | PowerShell を「管理者として実行」で開いたか。仮想化が有効か（4-1 参照） |
| 上限のエラーが出る | 量子ビット数・ショット数などが、アカウント画面の「現在のプランの上限」を超えていないか |

APIキーを登録し直したいときは、いったん削除してから 5. の登録コマンドを実行し直します。

```bash
claude mcp remove --scope user blueqat   # Claude Code
codex mcp remove blueqat                 # Codex CLI
```

Antigravity CLI は `~/.gemini/config/mcp_config.json` の `blueqat` の部分を書き直してください。

## 使い終わったら

- しばらく使わない、または人に見られたかもしれないときは、アカウント画面の「APIキー」でそのキーを **「失効」** してください。
- 4-4 で `~/.bashrc`（`~/.zshrc`）に書いた `export BLUEQAT_API_KEY=...` の行も消しておくと安全です。

## 動作確認の状況

| ツール | 状況（2026-10-29 時点） |
| :--- | :--- |
| Claude Code（WSL・Ubuntu 24.04） | 接続・ツール実行を確認済み。このリポジトリの例題はすべてこの環境で実行 |
| Claude（claude.ai / Claude Desktop） | 手順は [湊さんの記事](https://zenn.dev/yuichirominato/articles/4888146fe31adb) に基づく |
| Codex CLI | `codex mcp add` のオプションはヘルプで確認済み。接続は未確認 |
| Antigravity CLI | 手順は公式ドキュメントと第三者の記事に基づく。接続は未確認。カスタムMCPのツールを呼び出せない不具合の報告あり（[google-antigravity/antigravity-cli#71](https://github.com/google-antigravity/antigravity-cli/issues/71)） |

うまくいった・いかなかった報告は、このリポジトリの Issue で歓迎します。

## 参考

- [AIに話しかけるだけ！「blueqat MCP」で始める環境構築ゼロの量子計算入門](https://zenn.dev/yuichirominato/articles/4888146fe31adb)（blueqat 湊雄一郎さんの記事）
- [mcp.blueqat.app](https://mcp.blueqat.app)（blueqat MCP 公式ページ・料金と上限）
- [tiers_and_pricing.md](tiers_and_pricing.md)（無料・有料プランの上限と実機の料金）
