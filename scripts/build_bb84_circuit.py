"""
examples/11 のBB84量子鍵配送シミュレーション用の回路生成スクリプト。

各トライアルを「信号量子ビット1個 + アンシラ量子ビット1個」のペアで表現する。
Eveの盗聴（横取り→測定→再送）は、途中測定APIを使わずに次の手順で純粋な
ユニタリ回路として表現する:

  1. 信号をEveの基底に回転
  2. CNOT(信号 -> アンシラ) で「Eveの基底での測定」を表す絡み合いを作る
     （アンシラを二度と読み出さないことが、実際に測定して結果を捨てるのと
     統計的に等価になる。測定＝アンシラへのentangle＋trace-outという
     標準的な等価性を利用している）
  3. 信号をEveの基底から元に戻す

Alice/Bobの基底が一致しているトライアルだけを対象にする（基底が食い違う
トライアルは実際のBB84でも公開比較の後に破棄されるため、シミュレーションの
対象外でよい）。

実行: uv run python3 scripts/build_bb84_circuit.py
"""

from __future__ import annotations

import json
import random

N_TRIALS_PER_ROUND = 5  # 1回路あたりのトライアル数（信号+アンシラで2量子ビット/トライアル、free tierの10量子ビット上限に合わせる）


def alice_bob_gates(bit, basis, signal_q):
    """Alice準備 + (Eveなしの場合の)Bob復号に相当する部分。"""
    gates = []
    if bit == 1:
        gates.append({"gate": "x", "qubits": [signal_q]})
    if basis == "X":
        gates.append({"gate": "h", "qubits": [signal_q]})
    return gates


def eve_gates(basis, signal_q, ancilla_q):
    gates = []
    if basis == "X":
        gates.append({"gate": "h", "qubits": [signal_q]})
    gates.append({"gate": "cx", "qubits": [signal_q, ancilla_q]})
    if basis == "X":
        gates.append({"gate": "h", "qubits": [signal_q]})
    return gates


def bob_unrotate_gates(basis, signal_q):
    gates = []
    if basis == "X":
        gates.append({"gate": "h", "qubits": [signal_q]})
    return gates


def build_round(rng, with_eve, round_label):
    trials = []
    gates = []
    for i in range(N_TRIALS_PER_ROUND):
        signal_q, ancilla_q = 2 * i, 2 * i + 1
        bit = rng.randint(0, 1)
        basis = rng.choice(["Z", "X"])
        gates += alice_bob_gates(bit, basis, signal_q)
        trial = {"trial": f"{round_label}-{i}", "signal_qubit": signal_q, "alice_bit": bit, "basis": basis}
        if with_eve:
            eve_basis = rng.choice(["Z", "X"])
            gates += eve_gates(eve_basis, signal_q, ancilla_q)
            trial["eve_basis"] = eve_basis
            trial["eve_matched_alice"] = (eve_basis == basis)
        gates += bob_unrotate_gates(basis, signal_q)
        trials.append(trial)
    return gates, trials


def main():
    rng = random.Random(0)

    print("=== no Eve (baseline) ===")
    gates, trials = build_round(rng, with_eve=False, round_label="noeve")
    print(json.dumps(trials, indent=2))
    print(json.dumps(gates))

    print("\n=== with Eve, round A ===")
    gates_a, trials_a = build_round(rng, with_eve=True, round_label="eveA")
    print(json.dumps(trials_a, indent=2))
    print(json.dumps(gates_a))

    print("\n=== with Eve, round B ===")
    gates_b, trials_b = build_round(rng, with_eve=True, round_label="eveB")
    print(json.dumps(trials_b, indent=2))
    print(json.dumps(gates_b))


if __name__ == "__main__":
    main()
