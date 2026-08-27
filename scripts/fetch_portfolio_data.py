"""
examples/08 のポートフォリオ選定QUBOを再現するためのデータ取得・QUBO生成スクリプト。

日本株3銘柄+米国株2銘柄の過去1年の株価をyfinanceで取得し、USDJPYで円建て銘柄を
ドル建てに換算した上で年率換算リターン・共分散行列を計算し、Markowitz型の
「k銘柄選択」QUBOを組み立てて標準出力に表示する。

実行: uv run --with yfinance --with pandas --with numpy python3 scripts/fetch_portfolio_data.py

注意: 市場データは実行するたびに最新の値に変わるため、examples/08 に載せている
run_id・数値は「このスクリプトを2026-08-27に実行した結果」のスナップショットである。
再実行すると異なる数値・異なる最適解になり得る。
"""

from __future__ import annotations

import itertools
import json

import numpy as np
import pandas as pd
import yfinance as yf

TICKERS = {
    "7203.T": "Toyota",
    "8306.T": "MUFG",
    "9984.T": "SoftBank Group",
    "AAPL": "Apple",
    "MSFT": "Microsoft",
}
FX_TICKER = "JPY=X"  # USDJPY: 1米ドル=何円か
PERIOD = "1y"
K = 3          # 何銘柄を選ぶか（カーディナリティ制約）
PENALTY = 5.0  # カーディナリティ制約のペナルティ強度
LAMBDAS = {"return_seeking": 0.1, "balanced": 0.5, "risk_averse": 3.0}


def fetch_stats():
    tickers = list(TICKERS.keys())
    px = yf.download(tickers, period=PERIOD, auto_adjust=True, progress=False)["Close"].dropna()
    fx = yf.download(FX_TICKER, period=PERIOD, auto_adjust=True, progress=False)["Close"]
    fx = fx.iloc[:, 0] if hasattr(fx, "columns") else fx
    fx = fx.reindex(px.index).ffill()

    px_usd = px.copy()
    for t in tickers:
        if t.endswith(".T"):
            px_usd[t] = px[t] / fx  # JPY建て価格 / (円/ドル) = ドル建て価格

    log_ret = np.log(px_usd / px_usd.shift(1)).dropna()
    ann_return = (log_ret.mean() * 252)[tickers]
    ann_cov = (log_ret.cov() * 252).loc[tickers, tickers]
    return tickers, ann_return, ann_cov, px.index.min(), px.index.max()


def build_qubo(tickers, ann_return, ann_cov, lam, k=K, penalty=PENALTY):
    n = len(tickers)
    terms = []
    for i in range(n):
        coeff = -ann_return.iloc[i] + lam * ann_cov.iloc[i, i] + penalty * (1 - 2 * k)
        terms.append({"coeff": round(float(coeff), 6), "qubits": [i]})
    for i in range(n):
        for j in range(i + 1, n):
            coeff = 2 * lam * ann_cov.iloc[i, j] + 2 * penalty
            terms.append({"coeff": round(float(coeff), 6), "qubits": [i, j]})
    return terms


def exact_best(tickers, ann_return, ann_cov, lam, k=K):
    """検証用の総当たり: QUBOの目的関数と等価な -return + (lam*k)*variance で厳密解を出す。"""
    n = len(tickers)
    lam_eff = lam * k
    best = None
    for idx in itertools.combinations(range(n), k):
        w = np.zeros(n)
        for i in idx:
            w[i] = 1.0 / k
        r = float(w @ ann_return.values)
        var = float(w @ ann_cov.values @ w)
        obj = -r + lam_eff * var
        if best is None or obj < best[0]:
            best = (obj, idx, r, var)
    return best


def main():
    tickers, ann_return, ann_cov, start, end = fetch_stats()
    print(f"data range: {start.date()} -> {end.date()}")
    print("\nannualized return (USD-adjusted):")
    print(ann_return.round(4).to_string())
    print("\nannualized volatility:")
    print(pd.Series(np.sqrt(np.diag(ann_cov)), index=tickers).round(4).to_string())

    for name, lam in LAMBDAS.items():
        print(f"\n=== {name} (lambda={lam}, k={K}, penalty={PENALTY}) ===")
        qubo = build_qubo(tickers, ann_return, ann_cov, lam)
        print(json.dumps(qubo))
        obj, idx, r, var = exact_best(tickers, ann_return, ann_cov, lam)
        names = [tickers[i] for i in idx]
        print(f"exact optimum: {names}  return={r:.4f} vol={var ** 0.5:.4f}")


if __name__ == "__main__":
    main()
