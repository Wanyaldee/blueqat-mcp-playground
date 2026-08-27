# 例2: GHZ状態（3量子ビットへの拡張）

ベル状態を3量子ビットに拡張した GHZ 状態 `1/√2 (|000⟩ + |111⟩)` です。
`circuit_info` で実行前に回路のゲート数・深さを確認し、`draw_circuit` で回路図を描画してから実行しています。

## 回路

```json
{
  "gates": [
    {"gate": "h", "qubits": [0]},
    {"gate": "cx", "qubits": [0, 1]},
    {"gate": "cx", "qubits": [1, 2]}
  ]
}
```

## 1. circuit_info（実行せずに回路の情報だけ取得）

### 結果

```json
{
  "n_qubits": 3,
  "depth": 3,
  "gate_counts": { "h": 1, "cx": 2 }
}
```

シミュレータを実際に走らせる前に、ゲート数が上限（freeティアで200）に収まっているか等をここで確認できます。

## 2. draw_circuit（回路図。実行はされない）

`draw_circuit` はPNG画像とテキスト表現の両方を返します。PNGが表示できない環境ではテキスト表現が正になります。

```
GHZ state (3 qubits)
q0: H-*--
      |
q1: --X-*
        |
q2: ----X

凡例: * = 制御, X = 標的(CNOT), x = SWAP, + = 縦線が横切るだけ（無関係）
```

`draw_circuit` は `run_id` を発行しません（何も実行していないため）。回路の見た目の確認専用です。

## 3. run_circuit（counts, 256ショット）

### 結果

```json
{
  "counts": { "000": 124, "111": 132 },
  "shots": 256,
  "bit_order": "bitstring[0] is qubit 0"
}
```

3量子ビットとも常に一致した測定結果（`000` か `111` のみ）が得られ、3体エンタングルメントになっていることが分かります。

`proof`: [✓ 実行済み sim_20260827_aa78a1c58d7283b9](https://mcp.blueqat.app/runs/sim_20260827_aa78a1c58d7283b9)
