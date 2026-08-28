"""
examples/09 の特徴量選択QUBOを再現するためのデータ準備・QUBO生成スクリプト。

scikit-learn 標準搭載の乳がん診断データセット (load_breast_cancer) から
"mean_*" 系10特徴量を候補プールとして取り出し（free tierの10量子ビット上限に
ちょうど一致する）、目的変数との関連度(relevance)と特徴量間の冗長度(redundancy)
から mRMR型の「関連度は高く・互いに冗長でない」特徴量の組み合わせをQUBOとして
定式化し、`run_qaoa` で解く。

free tierには run_qaoa に渡せるQUBOの項数が20までという制限がある（sdk_infoの
表には出てこず、実際に55項（10候補の全ペア45通り+線形10）を投げてCircuitBuildError
になって初めて分かった）。そのため「ちょうどk個選ぶ」ハードな制約は使わず、冗長度
ペナルティの対象を統計的にも一般的な多重共線性のしきい値 |相関係数| >= 0.8 の
ペアだけに絞る（10候補中9ペアが該当し、線形10項+2次9項=19項で収まる）ことで、
選択する特徴量の個数は固定せずQUBOの最適化に委ねる。

あわせて、
  1. 実際にQAOAへ渡すのと同じQUBO多項式の厳密解（2^10=1024通りの総当たり）
  2. 古典的な特徴量選択 (SelectKBest, ANOVA F値。同数選択での比較用にQUBOの解と
     同じ個数でも計算する)
  3. 全10特徴量をそのまま使う場合
のロジスティック回帰テスト精度を比較用に計算する。

実行: uv run --with scikit-learn --with numpy --with pandas python3 scripts/build_feature_selection_qubo.py

注意: train/test分割に random_state を固定しているため決定論的に再現できる。
テストセットは約171件なので、1%未満の精度差は誤差の範囲として読むこと。
"""

from __future__ import annotations

import itertools
import json

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

MEAN_FEATURES = [
    "mean radius", "mean texture", "mean perimeter", "mean area",
    "mean smoothness", "mean compactness", "mean concavity",
    "mean concave points", "mean symmetry", "mean fractal dimension",
]
ALPHA = 1.0             # relevance（選ぶと得する）の重み
BETA = 1.0              # redundancy（両方選ぶと損する）の重み
CORR_THRESHOLD = 0.8    # この相関係数以上のペアだけを冗長度ペナルティ対象にする（多重共線性の一般的な目安）
RANDOM_STATE = 0


def load_data():
    data = load_breast_cancer(as_frame=True)
    X = data.frame[MEAN_FEATURES]
    y = data.target  # 0=malignant, 1=benign
    return train_test_split(X, y, test_size=0.3, random_state=RANDOM_STATE, stratify=y)


def relevance_redundancy(X_train, y_train):
    f_values, _ = f_classif(X_train, y_train)
    relevance = f_values / f_values.max()  # [0, 1] に正規化
    corr = np.abs(np.corrcoef(X_train.values, rowvar=False))
    return relevance, corr


def build_qubo(relevance, corr, alpha=ALPHA, beta=BETA, corr_threshold=CORR_THRESHOLD):
    n = len(relevance)
    terms = [{"coeff": round(float(-alpha * relevance[i]), 6), "qubits": [i]} for i in range(n)]
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if corr[i, j] >= corr_threshold]
    for i, j in pairs:
        terms.append({"coeff": round(float(beta * corr[i, j]), 6), "qubits": [i, j]})
    return terms, pairs


def evaluate(terms, bits):
    total = 0.0
    for t in terms:
        v = t["coeff"]
        for q in t["qubits"]:
            v *= bits[q]
        total += v
    return total


def exact_best(terms, n=10):
    """qaoaに渡すのと同じQUBO多項式を、全2^n状態で総当たり最小化する（QAOAと同じ探索空間）。"""
    best = None
    for combo in itertools.product([0, 1], repeat=n):
        obj = evaluate(terms, combo)
        if best is None or obj < best[0]:
            best = (obj, combo)
    return best


def accuracy_for(feature_idx, X_train, X_test, y_train, y_test):
    cols = [MEAN_FEATURES[i] for i in feature_idx]
    scaler = StandardScaler().fit(X_train[cols])
    clf = LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)
    clf.fit(scaler.transform(X_train[cols]), y_train)
    return clf.score(scaler.transform(X_test[cols]), y_test)


def main():
    X_train, X_test, y_train, y_test = load_data()
    relevance, corr = relevance_redundancy(X_train, y_train)

    print("features:", MEAN_FEATURES)
    print("relevance (normalized F-value):", np.round(relevance, 4).tolist())

    qubo, pairs = build_qubo(relevance, corr)
    print(f"\nredundancy pairs (|corr| >= {CORR_THRESHOLD}): {len(pairs)}")
    print(f"qubo ({len(qubo)} terms, alpha={ALPHA}, beta={BETA}):")
    print(json.dumps(qubo))

    obj, bits = exact_best(qubo)
    idx = tuple(i for i, b in enumerate(bits) if b == 1)
    k = len(idx)
    exact_names = [MEAN_FEATURES[i] for i in idx]
    print(f"\nexact optimum (brute force over 2^10=1024 states): bits={''.join(map(str, bits))} "
          f"n_selected={k} selected={exact_names} objective={obj:.4f}")
    print(f"  test accuracy with exact-optimum features:      {accuracy_for(idx, X_train, X_test, y_train, y_test):.4f}")

    skb = SelectKBest(f_classif, k=k).fit(X_train, y_train)
    skb_idx = tuple(sorted(np.where(skb.get_support())[0].tolist()))
    skb_names = [MEAN_FEATURES[i] for i in skb_idx]
    print(f"\nSelectKBest (classical, same count k={k}): {skb_names}")
    print(f"  test accuracy with SelectKBest features:        {accuracy_for(skb_idx, X_train, X_test, y_train, y_test):.4f}")

    all_idx = tuple(range(10))
    print(f"\nall {len(all_idx)} features:")
    print(f"  test accuracy with all features:                {accuracy_for(all_idx, X_train, X_test, y_train, y_test):.4f}")


if __name__ == "__main__":
    main()
