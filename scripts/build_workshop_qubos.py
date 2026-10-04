"""
examples/14〜19（ワークショップ向けの応用例）のQUBOを生成し、古典的な手法で答え合わせするスクリプト。

各題材について
  1. `run_qaoa` にそのまま渡せるQUBO（最小化形式、0/1変数）をJSONで出力する
  2. 同じQUBOを全探索（2^n通り）して厳密な最適解を求める
  3. 一部の題材では、人間がやりがちな貪欲法（良さそうな順に取る）の結果も並べる

free tierでは run_qaoa に渡せるQUBOの項数が20まで（sdk_infoの max_hamiltonian_terms）、
量子ビットは10までなので、どの題材もこの範囲に収まる規模にしている。
題材の数値はすべてワークショップ用に作った架空のもの。

実行: python3 scripts/build_workshop_qubos.py            # 全題材の要約を表示
      python3 scripts/build_workshop_qubos.py --json 16  # 例16のQUBOだけJSONで出力

外部ライブラリは使わない（標準ライブラリのみ）。
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from collections import defaultdict

# ---------------------------------------------------------------------------
# QUBO多項式の最小限の実装
# 項は「変数番号のタプル → 係数」の辞書。() は定数項。0/1変数なので x*x = x。
# ---------------------------------------------------------------------------


def const(c: float) -> dict:
    return {(): c}


def var(i: int, coeff: float = 1.0) -> dict:
    return {(i,): coeff}


def add(*polys: dict) -> dict:
    out: dict = defaultdict(float)
    for p in polys:
        for k, v in p.items():
            out[k] += v
    return {k: v for k, v in out.items() if abs(v) > 1e-12}


def mul(a: dict, b: dict) -> dict:
    out: dict = defaultdict(float)
    for ka, va in a.items():
        for kb, vb in b.items():
            key = tuple(sorted(set(ka) | set(kb)))  # x*x = x
            out[key] += va * vb
    return {k: v for k, v in out.items() if abs(v) > 1e-12}


def scale(p: dict, c: float) -> dict:
    return {k: v * c for k, v in p.items()}


def square(p: dict) -> dict:
    return mul(p, p)


def same_group(xi: dict, xj: dict) -> dict:
    """2つの0/1変数が同じ値なら1、違えば0（= 1 - xi - xj + 2 xi xj）。"""
    return add(const(1.0), scale(xi, -1), scale(xj, -1), scale(mul(xi, xj), 2))


def to_qubo_terms(p: dict) -> list[dict]:
    """定数項を落として run_qaoa 形式に変換する。"""
    return [
        {"coeff": round(v, 6), "qubits": list(k)}
        for k, v in sorted(p.items(), key=lambda kv: (len(kv[0]), kv[0]))
        if k
    ]


def evaluate(p: dict, bits) -> float:
    return sum(v for k, v in p.items() if all(bits[i] for i in k))


def brute_force(p: dict, n: int) -> tuple[float, list[tuple[int, ...]], float]:
    """全探索。最小値・最小値を取る全ビット列・所要時間(秒)を返す。"""
    start = time.perf_counter()
    best, argbest = float("inf"), []
    for bits in itertools.product((0, 1), repeat=n):
        v = evaluate(p, bits)
        if v < best - 1e-9:
            best, argbest = v, [bits]
        elif abs(v - best) <= 1e-9:
            argbest.append(bits)
    return best, argbest, time.perf_counter() - start


def bitstr(bits) -> str:
    return "".join(str(b) for b in bits)


# ---------------------------------------------------------------------------
# 例14: 相性を考えたチーム分け（6人を3人ずつ2チームへ）
# ---------------------------------------------------------------------------
TEAM_PEOPLE = ["佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺"]
# 正 = 同じチームだと嬉しい（仲が良い・補い合う）、負 = 同じチームだと気まずい
TEAM_AFFINITY = {
    (0, 1): +2, (2, 3): -3, (4, 5): +1,
    (0, 2): -2, (1, 5): -1, (3, 4): +2,
}
TEAM_SIZE = 3
TEAM_PENALTY = 10  # 人数が3人からずれたときの罰点（相性の合計より十分大きく）


def team_variable(person: int) -> dict:
    """佐藤さん(0)はチームA固定（AとBを入れ替えただけの重複解を消す）。他は q0..q4。"""
    return const(1.0) if person == 0 else var(person - 1)


def build_team() -> tuple[dict, int]:
    affinity = add(*(
        scale(same_group(team_variable(i), team_variable(j)), -w)
        for (i, j), w in TEAM_AFFINITY.items()
    ))
    size_a = add(*(team_variable(p) for p in range(len(TEAM_PEOPLE))))
    balance = square(add(size_a, const(-TEAM_SIZE)))
    return add(affinity, scale(balance, TEAM_PENALTY)), len(TEAM_PEOPLE) - 1


def describe_team(bits) -> str:
    team_a = [TEAM_PEOPLE[0]] + [TEAM_PEOPLE[i + 1] for i, b in enumerate(bits) if b]
    team_b = [TEAM_PEOPLE[i + 1] for i, b in enumerate(bits) if not b]
    full = (1,) + tuple(bits)
    score = sum(w for (i, j), w in TEAM_AFFINITY.items() if full[i] == full[j])
    return f"A={team_a} B={team_b} 相性合計={score}"


# ---------------------------------------------------------------------------
# 例15: 週末当番の割当（3人 × 土日、各日ちょうど1人、1人は最大1日）
# ---------------------------------------------------------------------------
SHIFT_PEOPLE = ["Aさん", "Bさん", "Cさん"]
SHIFT_DAYS = ["土", "日"]
# 負担感（小さいほど本人にとって楽）。NGの日は大きな値にする
SHIFT_BURDEN = {
    (0, 0): 9, (0, 1): 1,   # Aさん: 土曜は家族の予定でNG、日曜は平気
    (1, 0): 2, (1, 1): 3,   # Bさん: どちらでもよいが土曜のほうが楽
    (2, 0): 1, (2, 1): 2,   # Cさん: 土曜希望
}
SHIFT_PENALTY = 20


def shift_var(person: int, day: int) -> int:
    return person * len(SHIFT_DAYS) + day


def build_shift() -> tuple[dict, int]:
    n = len(SHIFT_PEOPLE) * len(SHIFT_DAYS)
    burden = add(*(var(shift_var(p, d), c) for (p, d), c in SHIFT_BURDEN.items()))
    per_day = add(*(
        square(add(*(var(shift_var(p, d)) for p in range(len(SHIFT_PEOPLE))), const(-1)))
        for d in range(len(SHIFT_DAYS))
    ))
    # 1人が土日両方入るのを禁止（x_土 * x_日 に罰点）
    at_most_one = add(*(
        mul(var(shift_var(p, 0)), var(shift_var(p, 1))) for p in range(len(SHIFT_PEOPLE))
    ))
    return add(burden, scale(add(per_day, at_most_one), SHIFT_PENALTY)), n


def describe_shift(bits) -> str:
    out = []
    for d, day in enumerate(SHIFT_DAYS):
        who = [SHIFT_PEOPLE[p] for p in range(len(SHIFT_PEOPLE)) if bits[shift_var(p, d)]]
        out.append(f"{day}={who}")
    burden = sum(c for (p, d), c in SHIFT_BURDEN.items() if bits[shift_var(p, d)])
    return " ".join(out) + f" 負担合計={burden}"


# ---------------------------------------------------------------------------
# 例16: 出店候補地の選定（5候補からちょうど2店）
# ---------------------------------------------------------------------------
STORE_SITES = ["駅前", "大学前", "住宅街", "国道沿い", "商店街"]
STORE_SALES = [10, 7, 6, 8, 5]  # 単独で出したときの見込み月商（百万円）
# 近い候補同士は客を奪い合う（両方出すと合計がこれだけ減る）
STORE_CANNIBAL = {(0, 1): 4, (0, 4): 5, (2, 3): 1, (1, 4): 2, (0, 3): 3}
STORE_COUNT = 2
STORE_PENALTY = 30


def build_store() -> tuple[dict, int]:
    n = len(STORE_SITES)
    sales = add(*(var(i, -s) for i, s in enumerate(STORE_SALES)))
    cannibal = add(*(scale(mul(var(i), var(j)), c) for (i, j), c in STORE_CANNIBAL.items()))
    count = square(add(*(var(i) for i in range(n)), const(-STORE_COUNT)))
    return add(sales, cannibal, scale(count, STORE_PENALTY)), n


def store_greedy() -> list[int]:
    """単独の月商が大きい順に2つ取る（共食いを考えない、ありがちな選び方）。"""
    return sorted(range(len(STORE_SITES)), key=lambda i: -STORE_SALES[i])[:STORE_COUNT]


def describe_store(bits) -> str:
    chosen = [i for i, b in enumerate(bits) if b]
    total = sum(STORE_SALES[i] for i in chosen) - sum(
        c for (i, j), c in STORE_CANNIBAL.items() if i in chosen and j in chosen
    )
    return f"{[STORE_SITES[i] for i in chosen]} 合計見込み月商={total}"


# ---------------------------------------------------------------------------
# 例17: 会議のスケジュール調整（5会議を午前/午後の2枠へ）
# ---------------------------------------------------------------------------
MEETINGS = ["定例", "採用面接", "予算会議", "顧客打合せ", "1on1"]
# 同じ枠に入れると困る組み合わせ（値 = 重複して出席する人数）
# 定例・採用面接・予算会議は三角形なので、2枠ではどこか1組が必ず重なる
MEETING_OVERLAP = {
    (0, 1): 2, (1, 2): 1, (0, 2): 3,
    (2, 3): 2, (3, 4): 1, (0, 4): 1,
}


def build_meeting() -> tuple[dict, int]:
    clash = add(*(
        scale(same_group(var(i), var(j)), w) for (i, j), w in MEETING_OVERLAP.items()
    ))
    return clash, len(MEETINGS)


def describe_meeting(bits) -> str:
    am = [MEETINGS[i] for i, b in enumerate(bits) if not b]
    pm = [MEETINGS[i] for i, b in enumerate(bits) if b]
    clash = [
        f"{MEETINGS[i]}×{MEETINGS[j]}({w}人)"
        for (i, j), w in MEETING_OVERLAP.items() if bits[i] == bits[j]
    ]
    return f"午前={am} 午後={pm} 重なり={clash}"


# ---------------------------------------------------------------------------
# 例18: 実験条件のスクリーニング（6候補から、費用を意識しつつ冗長でない組を選ぶ）
# ---------------------------------------------------------------------------
EXPERIMENTS = ["高温", "低温", "触媒A", "触媒B", "高圧", "長時間"]
EXP_INFO = [6, 4, 7, 6, 5, 3]   # 見込める情報量（得点）
EXP_COST = [3, 2, 4, 4, 3, 1]   # 費用（万円）
# 似た情報しか得られない組み合わせ（両方やると情報量がこれだけ目減りする）
EXP_REDUNDANCY = {(0, 4): 3, (2, 3): 5, (0, 5): 2, (1, 5): 1}
EXP_COST_WEIGHT = 1.0  # 費用1万円を情報量いくつ分と見るか


def build_experiment() -> tuple[dict, int]:
    n = len(EXPERIMENTS)
    gain = add(*(var(i, -v) for i, v in enumerate(EXP_INFO)))
    cost = add(*(var(i, EXP_COST_WEIGHT * c) for i, c in enumerate(EXP_COST)))
    redundant = add(*(scale(mul(var(i), var(j)), r) for (i, j), r in EXP_REDUNDANCY.items()))
    return add(gain, cost, redundant), n


def experiment_greedy() -> list[int]:
    """単独で見て「情報量 > 費用」のものを全部やる（冗長性を考えない、ありがちな選び方）。"""
    return [i for i in range(len(EXPERIMENTS)) if EXP_INFO[i] - EXP_COST_WEIGHT * EXP_COST[i] > 0]


def describe_experiment(bits) -> str:
    chosen = [i for i, b in enumerate(bits) if b]
    info = sum(EXP_INFO[i] for i in chosen) - sum(
        r for (i, j), r in EXP_REDUNDANCY.items() if i in chosen and j in chosen
    )
    cost = sum(EXP_COST[i] for i in chosen)
    return f"{[EXPERIMENTS[i] for i in chosen]} 実質情報量={info} 費用={cost}万円 差引={info - cost}"


# ---------------------------------------------------------------------------
# 例19: 査読担当の割当（論文2本 × 候補3人、各論文1人、1人は最大1本、利益相反は除外）
# ---------------------------------------------------------------------------
PAPERS = ["論文X(画像認識)", "論文Y(自然言語処理)"]
REVIEWERS = ["Y先生", "N先生", "K先生"]
# 専門の一致度（大きいほど適任）
REVIEW_MATCH = {
    (0, 0): 5, (0, 1): 2, (0, 2): 4,
    (1, 0): 3, (1, 1): 5, (1, 2): 4,
}
REVIEW_COI = {(1, 1)}  # N先生は論文Yの著者と共同研究中（利益相反）
REVIEW_PENALTY = 20


def review_var(paper: int, reviewer: int) -> int:
    return paper * len(REVIEWERS) + reviewer


def build_review() -> tuple[dict, int]:
    n = len(PAPERS) * len(REVIEWERS)
    match = add(*(var(review_var(p, r), -m) for (p, r), m in REVIEW_MATCH.items()))
    coi = add(*(var(review_var(p, r), REVIEW_PENALTY) for (p, r) in REVIEW_COI))
    per_paper = add(*(
        square(add(*(var(review_var(p, r)) for r in range(len(REVIEWERS))), const(-1)))
        for p in range(len(PAPERS))
    ))
    per_reviewer = add(*(
        mul(var(review_var(0, r)), var(review_var(1, r))) for r in range(len(REVIEWERS))
    ))
    return add(match, coi, scale(add(per_paper, per_reviewer), REVIEW_PENALTY)), n


def review_greedy() -> list[int]:
    """論文順に、まだ空いている一番適任の先生を割り当てる（利益相反だけは避ける）。"""
    taken, bits = set(), [0] * (len(PAPERS) * len(REVIEWERS))
    for p in range(len(PAPERS)):
        candidates = [
            r for r in range(len(REVIEWERS)) if r not in taken and (p, r) not in REVIEW_COI
        ]
        best = max(candidates, key=lambda r: REVIEW_MATCH[(p, r)])
        bits[review_var(p, best)] = 1
        taken.add(best)
    return bits


def describe_review(bits) -> str:
    pairs, score = [], 0
    for p in range(len(PAPERS)):
        for r in range(len(REVIEWERS)):
            if bits[review_var(p, r)]:
                pairs.append(f"{PAPERS[p]}→{REVIEWERS[r]}")
                score += REVIEW_MATCH[(p, r)]
    return f"{pairs} 一致度合計={score}"


# ---------------------------------------------------------------------------

PROBLEMS = {
    "14": ("相性を考えたチーム分け", build_team, describe_team),
    "15": ("週末当番の割当", build_shift, describe_shift),
    "16": ("出店候補地の選定", build_store, describe_store),
    "17": ("会議のスケジュール調整", build_meeting, describe_meeting),
    "18": ("実験条件のスクリーニング", build_experiment, describe_experiment),
    "19": ("査読担当の割当", build_review, describe_review),
}

GREEDY = {
    "16": ("貪欲法(月商順に2つ)", lambda n: [1 if i in store_greedy() else 0 for i in range(n)]),
    "18": ("貪欲法(単独で黒字なら全部)", lambda n: [1 if i in experiment_greedy() else 0 for i in range(n)]),
    "19": ("貪欲法(論文順に最適任)", lambda n: review_greedy()),
}


def summarize(key: str) -> None:
    title, build, describe = PROBLEMS[key]
    p, n = build()
    terms = to_qubo_terms(p)
    offset = p.get((), 0)
    best, argbest, elapsed = brute_force(p, n)
    print(f"=== 例{key}: {title} ===")
    print(f"  量子ビット数={n} QUBO項数={len(terms)} 定数項={offset:g}")
    print(f"  全探索: {2 ** n}通りを {elapsed * 1000:.2f} ms で評価")
    for bits in argbest:
        print(f"  最適解 {bitstr(bits)} (QUBO値={best - offset:g}): {describe(bits)}")
    if key in GREEDY:
        label, greedy = GREEDY[key]
        bits = greedy(n)
        print(f"  {label} {bitstr(bits)} (QUBO値={evaluate(p, bits) - offset:g}): {describe(bits)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="ワークショップ用QUBOの生成と全探索による答え合わせ")
    parser.add_argument("--json", metavar="EXAMPLE", choices=sorted(PROBLEMS))
    args = parser.parse_args()
    if args.json:
        p, _ = PROBLEMS[args.json][1]()
        print(json.dumps(to_qubo_terms(p), ensure_ascii=False))
        return
    for key in PROBLEMS:
        summarize(key)


if __name__ == "__main__":
    main()
