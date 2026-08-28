"""
examples/12 のH2分子VQE用のハミルトニアン生成スクリプト。

PySCF + OpenFermion で水素分子(H2, STO-3G基底)の電子構造計算を行い、
Jordan-Wigner変換で4量子ビットのqubitハミルトニアンに変換して、
run_vqe に渡せるJSON形式で出力する。結合長を変えて複数点計算することで、
VQE/FCI(厳密解)/HF(平均場近似)のポテンシャルエネルギー曲線を比較できる。

STO-3G基底のH2は最小構成の量子化学ベンチマークで、Jordan-Wigner変換すると
ちょうど4量子ビット・15項のハミルトニアンになり、free tierの上限
（10量子ビット、ハミルトニアン最大20項）に余裕をもって収まる。

実行: uv run --with pyscf --with openfermion --with openfermionpyscf python3 scripts/build_h2_vqe.py
"""

from __future__ import annotations

import json

from openfermion.chem import MolecularData
from openfermion.transforms import get_fermion_operator, jordan_wigner
from openfermion.utils import count_qubits
from openfermionpyscf import run_pyscf

BOND_LENGTHS = [0.3, 0.5, 0.7414, 1.0, 1.5, 2.0, 2.5]  # Å。0.7414が実験的な平衡結合長


def qubit_op_to_mcp_hamiltonian(qubit_op):
    terms = []
    for pauli_tuple, coeff in qubit_op.terms.items():
        assert abs(coeff.imag) < 1e-8, f"unexpected imaginary coefficient: {coeff}"
        if not pauli_tuple:
            # 定数項（恒等演算子）はqubit0への恒等項として表現できないため、
            # run_vqeの外で別途足し合わせる必要がある。
            terms.append({"coeff": round(float(coeff.real), 8), "paulis": [], "_identity": True})
            continue
        paulis = [{"op": op, "qubit": q} for q, op in pauli_tuple]
        terms.append({"coeff": round(float(coeff.real), 8), "paulis": paulis})
    return terms


def compute_point(bond_length):
    geometry = [("H", (0, 0, 0)), ("H", (0, 0, bond_length))]
    molecule = MolecularData(geometry, "sto-3g", multiplicity=1, charge=0,
                              description=f"h2_{bond_length}")
    molecule = run_pyscf(molecule, run_scf=True, run_fci=True)

    ham = molecule.get_molecular_hamiltonian()
    qubit_op = jordan_wigner(get_fermion_operator(ham))
    n_qubits = count_qubits(qubit_op)
    terms = qubit_op_to_mcp_hamiltonian(qubit_op)

    identity_terms = [t for t in terms if t.get("_identity")]
    identity_offset = sum(t["coeff"] for t in identity_terms)
    pauli_terms = [{"coeff": t["coeff"], "paulis": t["paulis"]} for t in terms if not t.get("_identity")]

    return {
        "bond_length": bond_length,
        "n_qubits": n_qubits,
        "n_terms": len(pauli_terms),
        "hf_energy": molecule.hf_energy,
        "fci_energy": molecule.fci_energy,
        "identity_offset": identity_offset,
        "hamiltonian_without_identity": pauli_terms,
    }


def main():
    for bl in BOND_LENGTHS:
        point = compute_point(bl)
        print(f"\n=== bond_length={bl} Å ===")
        print(f"n_qubits={point['n_qubits']} n_terms={point['n_terms']} "
              f"identity_offset={point['identity_offset']:.6f}")
        print(f"hf_energy={point['hf_energy']:.6f}  fci_energy={point['fci_energy']:.6f}")
        print(json.dumps(point["hamiltonian_without_identity"]))


if __name__ == "__main__":
    main()
