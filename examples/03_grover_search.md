# 例3: Grover探索（2量子ビット、1反復で確定的に正解）

2量子ビット（探索空間 $N=4$）で $|11\rangle$ を正解としてマークするGroverアルゴリズムです。
N=4のときは1回のGrover反復だけで振幅が理論上100%正解に集まるため、確認しやすい最小例になっています。

## アルゴリズムの構成

1. 全量子ビットに `h` — 一様重ね合わせを作る
2. オラクル: `cz(0,1)` — $|11\rangle$ の位相だけを反転（マーキング）
3. 拡散演算子（振幅増幅）: `h,h → x,x → cz(0,1) → x,x → h,h`
4. 測定

```json
{
  "gates": [
    {"gate": "h", "qubits": [0]},
    {"gate": "h", "qubits": [1]},
    {"gate": "cz", "qubits": [0, 1]},
    {"gate": "h", "qubits": [0]},
    {"gate": "h", "qubits": [1]},
    {"gate": "x", "qubits": [0]},
    {"gate": "x", "qubits": [1]},
    {"gate": "cz", "qubits": [0, 1]},
    {"gate": "x", "qubits": [0]},
    {"gate": "x", "qubits": [1]},
    {"gate": "h", "qubits": [0]},
    {"gate": "h", "qubits": [1]}
  ]
}
```

## 回路図

![Grover search circuit](../assets/03_grover_search.png)

`H`ボックスと制御ドット同士を結ぶ線が `CZ`（オラクル・拡散演算子それぞれに1本ずつ、計2本）です。
`draw_circuit` が実際に返したテキスト表現:

```
Grover search (target |11>, 1 iteration)
q0: H-*-H-X-*-X-H
      |     |
q1: H-*-H-X-*-X-H

凡例: * = 制御, X = 標的(CNOT), x = SWAP, + = 縦線が横切るだけ（無関係）
```

## 実行結果（counts, 256ショット）

```json
{
  "counts": { "11": 256 },
  "shots": 256,
  "bit_order": "bitstring[0] is qubit 0"
}
```

256ショット全てが `11` になりました。理論通り、 $N=4$・1反復のGroverは確定的に正解を返します。

`proof`: [✓ 実行済み sim_20260827_443d461aaff74946](https://mcp.blueqat.app/runs/sim_20260827_443d461aaff74946)

## 応用のヒント

- 探索対象を変えたい場合はオラクル部分（最初の `cz`）を変更します。例えば $|10\rangle$ をマークしたいなら
  オラクルの前後に `x(1)` を挟んで位相反転の対象をずらします。
- 量子ビット数が増えると最適な反復回数は $\frac{\pi}{4}\sqrt{N}$ 回になります（ $N=4$ は特殊ケースで1回が最適）。
  ただし free tier は `max_gates: 200` なので、反復を増やすとゲート数上限に注意してください。
