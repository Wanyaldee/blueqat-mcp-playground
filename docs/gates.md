# 対応ゲート一覧

`list_gates` ツールで取得した、`run_circuit` / `circuit_info` / `draw_circuit` の `gates` に指定できるゲート名の一覧です。

## 基本ゲート

| ゲート | 意味 |
|--------|------|
| `i` | 恒等（何もしない） |
| `x`, `y`, `z` | パウリ X/Y/Z |
| `h` | アダマール |
| `s`, `sdg` | S / S† (位相 π/2) |
| `t`, `tdg` | T / T† (位相 π/4) |
| `sx`, `sxdg` | √X / (√X)† |
| `p`, `phase` | 位相ゲート（`params: [theta]`） |
| `r` | 回転ゲート |
| `rx`, `ry`, `rz` | X/Y/Z軸回転（`params: [theta]`） |
| `u`, `mat1` | 汎用単一量子ビットゲート |
| `reset` | 量子ビットのリセット |
| `barrier` | 最適化の境界（回路構造には影響しない） |
| `m`, `measure` | 測定 |

## 2量子ビットゲート

制御付きゲートは **「制御 → ターゲット」の順で `qubits` を指定**します
（例: `0`から`1`へのCNOTは `{"gate": "cx", "qubits": [0, 1]}`）。

| ゲート | 意味 |
|--------|------|
| `cx`, `cnot` | 制御NOT（CNOT） |
| `cy`, `cz` | 制御Y / 制御Z |
| `ch` | 制御アダマール |
| `cp`, `cphase`, `cr` | 制御位相 |
| `crx`, `cry`, `crz` | 制御回転 |
| `cu` | 制御U |
| `swap` | SWAP |
| `iswap`, `iswapdg` | iSWAP / (iSWAP)† |
| `exch`, `exchange` | 交換ゲート |
| `rxx`, `ryy`, `rzz` | 2量子ビット回転（Ising結合） |
| `zz`, `zzdg` | ZZ相互作用ゲート |

## 3量子ビットゲート

| ゲート | 意味 |
|--------|------|
| `ccx`, `toffoli` | トフォリゲート（制御2つ + ターゲット1つ） |
| `ccz` | 制御制御Z |
| `cswap` | 制御SWAP（フレドキンゲート） |

## パラメータの渡し方

角度が必要なゲート（`rx`, `ry`, `rz`, `p` など）は `params` にラジアン単位で渡します。

```json
{"gate": "ry", "qubits": [0], "params": [1.5707963267948966]}
```

## 全ビットの `bit_order` について

`run_circuit` の counts / amplitude で返るビット列は **`bitstring[0]` が量子ビット0** です
（一般的な物理の教科書の記法と同じ、q0が最下位ではなく先頭）。一方 `statevector` のインデックスは
**リトルエンディアン**（インデックス `i` のビット `k` が量子ビット `k`）なので、2つの表現で並び方が
逆になっている点に注意してください。
