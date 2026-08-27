# blueqat-mcp-playground

[blueqat MCP](https://github.com/blueqat/blueqatSDK) サーバーで遊んでみたメモと使用例集です。
MCP (Model Context Protocol) 経由で量子回路シミュレータ・QAOA・VQE・実機QPUを呼び出せる `blueqat` サーバーの
ツールを一通り叩き、実際に返ってきた結果を添えてドキュメント化しています。

すべての実行結果には `run_id` が付いており、[verify_run](https://mcp.blueqat.app) で本当に実行されたことを検証できます。
このリポジトリの例に載せた `run_id` もすべて実際にサーバー上で実行したものです（結果を手で書き換えていません）。

<p align="center">
  <img src="assets/03_grover_search.png" alt="Grover search circuit" width="70%">
</p>

## これは何か

blueqat MCP は、JSON形式のゲートリストで量子回路を記述して投げると、クラウド上のシミュレータ(または実機QPU)で
実行してくれる MCP サーバーです。Claude Code / Claude Desktop など MCP 対応クライアントから、SDKのインストールや
Pythonの実行環境なしに量子計算を試せます。

- 回路シミュレーション（counts / amplitude / statevector / expectation）
- QAOA によるQUBO最適化
- VQE による基底エネルギー探索
- 回路図の描画・ゲート数/深さの確認
- 実機QPU（OQC Toshiko Tokyo-1 など）への投入

## クイックスタート

MCPクライアント（Claude Codeなど）から `run_circuit` ツールを、以下のようなJSONで呼び出します。

```json
{
  "gates": [
    {"gate": "h", "qubits": [0]},
    {"gate": "cx", "qubits": [0, 1]}
  ],
  "shots": 256,
  "output": "counts"
}
```

ゲート名の一覧は `list_gates` ツールで取得できます（`docs/gates.md` に一覧を転記済み）。

## 使用例一覧

| # | 例 | 使ったツール | 内容 |
|---|----|-------------|------|
| 1 | [ベル状態](examples/01_bell_state.md) | `run_circuit` | 2量子ビットの最小のエンタングルメント例。counts / statevector / amplitude の3通りの出力を比較 |
| 2 | [GHZ状態](examples/02_ghz_state.md) | `run_circuit`, `circuit_info`, `draw_circuit` | 3量子ビットへの拡張、回路情報の取得と回路図の描画 |
| 3 | [Grover探索](examples/03_grover_search.md) | `run_circuit`, `draw_circuit` | 2量子ビット・1反復のGroverアルゴリズムで100%正解を引く |
| 4 | [QAOAでMaxCut](examples/04_qaoa_maxcut.md) | `run_qaoa` | 三角形グラフの最大カット問題をQUBOとして解く |
| 5 | [VQEで横磁場イジング模型](examples/05_vqe_transverse_ising.md) | `run_vqe` | 2量子ビットの横磁場イジング模型の基底エネルギーを変分法で求める |

## 無料枠の制限（free tier）

`sdk_info` ツールで取得した、このアカウントに適用される制限です。

| 項目 | free | paid |
|------|------|------|
| 最大量子ビット数 | 10 | 20 |
| statevector等の最大量子ビット数 | 10 | 16 |
| 最大ショット数 | 256 | 4000 |
| 最大ゲート数 | 200 | 1000 |
| ハミルトニアン最大項数 | 20 | 50 |
| QAOA最大ステップ数(p) | 2 | 5 |
| タイムアウト | 10秒 | 20秒 |
| 実機ジョブ/月 | 10 | 100 |

詳細は [docs/tiers_and_pricing.md](docs/tiers_and_pricing.md) を参照してください。

## 実機QPU

`list_hardware_qpus` で取得できる、このサーバーから投入可能な実機/エミュレータです。詳細は [docs/hardware.md](docs/hardware.md)。

- **OQC Toshiko Tokyo-1**（日本リージョン、32量子ビット、実機）
- **Lucy Simulator**（英国リージョン、8量子ビット、常時稼働のホステッドシミュレータ）

## リポジトリ構成

```
.
├── README.md
├── LICENSE
├── examples/        使用例（実行結果・run_id付き）
├── assets/          回路図・グラフ図のPNG（examplesから参照）
├── scripts/
│   └── render_diagrams.py  assets/ のPNGを生成するスクリプト
└── docs/
    ├── gates.md              対応ゲート一覧
    ├── tiers_and_pricing.md  ティア制限と実機課金
    └── hardware.md           実機QPU一覧
```

回路図について: `draw_circuit` ツール自体はPNGをチャット表示用に返すだけで生バイト列として保存できないため、
`assets/` の画像は同じ回路構成を [scripts/render_diagrams.py](scripts/render_diagrams.py)（matplotlib）で
このリポジトリ用に再描画したものです。ゲート列や実行結果はすべてMCPサーバーから実際に返ってきたものをそのまま
使用しています。

## ライセンス

MIT License. 詳細は [LICENSE](LICENSE) を参照してください。
blueqat MCP サーバー自体および `blueqat` SDK 本体は別プロジェクトです（[blueqat/blueqatSDK](https://github.com/blueqat/blueqatSDK)）。
