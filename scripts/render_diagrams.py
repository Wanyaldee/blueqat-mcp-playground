"""
examples/ で使っている回路図・グラフ図を assets/ にPNGとして書き出すスクリプト。

blueqat MCP の draw_circuit ツールはPNGをチャット表示用に返すだけで、
生のバイト列としてファイル保存できないため、同じ回路をここでmatplotlibで
再描画してリポジトリに実ファイルとして同梱している。

実行: uv run --with matplotlib python3 scripts/render_diagrams.py
"""

from __future__ import annotations

import math
from pathlib import Path

import urllib.request

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch

ASSETS = Path(__file__).resolve().parent.parent / "assets"

_FONT_CACHE_DIR = Path(__file__).resolve().parent / ".fonts_cache"
_JP_FONT = _FONT_CACHE_DIR / "NotoSansJP.ttf"
_JP_FONT_URL = "https://github.com/google/fonts/raw/main/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf"


def _ensure_jp_font():
    """日本語ラベルを描画するため、初回実行時だけNoto Sans JPを取得してキャッシュする。"""
    if not _JP_FONT.exists():
        _FONT_CACHE_DIR.mkdir(exist_ok=True)
        try:
            urllib.request.urlretrieve(_JP_FONT_URL, _JP_FONT)
        except OSError as e:
            print(f"warning: could not fetch Noto Sans JP ({e}); Japanese labels may not render")
            return
    fm.fontManager.addfont(str(_JP_FONT))
    plt.rcParams["font.family"] = fm.FontProperties(fname=str(_JP_FONT)).get_name()


_ensure_jp_font()

WIRE_COLOR = "#8a8478"
BOX_EDGE = "#2b2b2b"
BOX_FACE = "#ffffff"
DOT_COLOR = "#2b2b2b"
TEXT_COLOR = "#2b2b2b"


def draw_circuit(gates, n_qubits, title, out_path, qubit_labels=None):
    """gates: [{"gate": str, "qubits": [int,...]}, ...] を左から右へ時系列で描画する。"""
    n_cols = len(gates)
    fig_w = max(3.2, 1.15 * n_cols + 1.6)
    fig_h = max(1.8, 0.9 * n_qubits + 1.0)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    col_xs = [1.4 + i * 1.15 for i in range(n_cols)]
    row_ys = [-(q * 0.9) for q in range(n_qubits)]

    for q in range(n_qubits):
        ax.plot([0.5, col_xs[-1] + 0.9 if n_cols else 2.2], [row_ys[q], row_ys[q]],
                color=WIRE_COLOR, lw=1.4, zorder=1)
        label = qubit_labels[q] if qubit_labels else f"q{q}"
        ax.text(0.15, row_ys[q], label, ha="right", va="center", fontsize=11, color=TEXT_COLOR)

    box_w, box_h = 0.62, 0.62

    for i, g in enumerate(gates):
        x = col_xs[i]
        name = g["gate"]
        qubits = g["qubits"]

        if name in ("cx", "cnot", "cz", "cy", "ch", "ccx", "toffoli", "ccz"):
            controls, target = qubits[:-1], qubits[-1]
            all_q = qubits
            y_top = row_ys[min(all_q)]
            y_bot = row_ys[max(all_q)]
            ax.plot([x, x], [y_top, y_bot], color=DOT_COLOR, lw=1.4, zorder=2)
            for c in controls:
                ax.add_patch(Circle((x, row_ys[c]), 0.09, color=DOT_COLOR, zorder=3))
            if name in ("cz", "ccz"):
                ax.add_patch(Circle((x, row_ys[target]), 0.09, color=DOT_COLOR, zorder=3))
            else:
                box = FancyBboxPatch((x - box_w / 2, row_ys[target] - box_h / 2), box_w, box_h,
                                      boxstyle="round,pad=0.02,rounding_size=0.05",
                                      linewidth=1.3, edgecolor=BOX_EDGE, facecolor=BOX_FACE, zorder=3)
                ax.add_patch(box)
                ax.text(x, row_ys[target], "X", ha="center", va="center", fontsize=11,
                         color=TEXT_COLOR, zorder=4)
        elif name == "swap":
            y_top, y_bot = row_ys[qubits[0]], row_ys[qubits[1]]
            ax.plot([x, x], [y_top, y_bot], color=DOT_COLOR, lw=1.4, zorder=2)
            for q in qubits:
                d = 0.11
                ax.plot([x - d, x + d], [row_ys[q] - d, row_ys[q] + d], color=DOT_COLOR, lw=1.6, zorder=3)
                ax.plot([x - d, x + d], [row_ys[q] + d, row_ys[q] - d], color=DOT_COLOR, lw=1.6, zorder=3)
        else:
            q = qubits[0]
            box = FancyBboxPatch((x - box_w / 2, row_ys[q] - box_h / 2), box_w, box_h,
                                  boxstyle="round,pad=0.02,rounding_size=0.05",
                                  linewidth=1.3, edgecolor=BOX_EDGE, facecolor=BOX_FACE, zorder=3)
            ax.add_patch(box)
            label = g.get("label", name.upper())
            ax.text(x, row_ys[q], label, ha="center", va="center", fontsize=10.5,
                     color=TEXT_COLOR, zorder=4)

    ax.set_title(title, fontsize=12, color=TEXT_COLOR, pad=12)
    ax.set_xlim(0, col_xs[-1] + 0.9 if n_cols else 2.2)
    ax.set_ylim(min(row_ys) - 0.7, max(row_ys) + 0.7)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    fig.tight_layout()
    fig.savefig(out_path, dpi=180, facecolor="white")
    plt.close(fig)
    print(f"wrote {out_path}")


def draw_triangle_graph(out_path):
    fig, ax = plt.subplots(figsize=(3.6, 3.4))
    pos = {
        0: (0.0, 1.0),
        1: (-0.87, -0.5),
        2: (0.87, -0.5),
    }
    edges = [(0, 1), (1, 2), (0, 2)]
    for a, b in edges:
        xa, ya = pos[a]
        xb, yb = pos[b]
        ax.plot([xa, xb], [ya, yb], color=WIRE_COLOR, lw=2.0, zorder=1)

    for node, (x, y) in pos.items():
        ax.add_patch(Circle((x, y), 0.22, facecolor="#ffffff", edgecolor=BOX_EDGE, lw=1.6, zorder=2))
        ax.text(x, y, f"q{node}", ha="center", va="center", fontsize=11, color=TEXT_COLOR, zorder=3)

    ax.set_title("MaxCut (triangle graph)", fontsize=12, color=TEXT_COLOR, pad=10)
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.1, 1.5)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")
    fig.tight_layout()
    fig.savefig(out_path, dpi=180, facecolor="white")
    plt.close(fig)
    print(f"wrote {out_path}")


SEQ_BLUE = "#2a78d6"
MUTED_GRAY = "#c3c2b7"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
SURFACE = "#fcfcfb"


def draw_qrng_histogram(counts, shots, out_path, title):
    """counts: {"000": 33, ...} 8通りの3bit出力の頻度。dataviz skillのパレットに準拠。"""
    labels = sorted(counts.keys())
    values = [counts[k] for k in labels]
    expected = shots / len(labels)

    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRIDLINE, lw=1.0, zorder=0)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)

    x = range(len(labels))
    bars = ax.bar(x, values, width=0.6, color=SEQ_BLUE, zorder=3)
    for rect, v in zip(bars, values):
        ax.text(rect.get_x() + rect.get_width() / 2, v + max(values) * 0.02, str(v),
                 ha="center", va="bottom", fontsize=9.5, color=INK_SECONDARY)

    ax.axhline(expected, color=INK_MUTED, lw=1.4, ls=(0, (4, 3)), zorder=2)
    ax.text(len(labels) - 0.4, expected + max(values) * 0.02,
             f"期待値(一様分布) {expected:.0f}", ha="right", va="bottom",
             fontsize=9.5, color=INK_MUTED)

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=10, color=INK_SECONDARY, family="monospace")
    ax.set_ylabel(f"count (shots={shots})", fontsize=10, color=INK_SECONDARY)
    ax.set_title(title, fontsize=12, color=INK_PRIMARY, pad=12)
    ax.tick_params(axis="y", colors=INK_MUTED, labelsize=9)
    ax.tick_params(axis="x", length=0)

    fig.tight_layout()
    fig.savefig(out_path, dpi=180, facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {out_path}")


def draw_budget_items(costs, selected, target, out_path, title):
    """costs: [int,...], selected: 選択された案件のindex集合, target: 目標予算"""
    labels = [f"item{i}\n(¥{c})" for i, c in enumerate(costs)]

    fig, ax = plt.subplots(figsize=(5.6, 4.0))
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRIDLINE, lw=1.0, zorder=0)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)

    x = range(len(costs))
    colors = [SEQ_BLUE if i in selected else MUTED_GRAY for i in range(len(costs))]
    bars = ax.bar(x, costs, width=0.55, color=colors, zorder=3)
    for rect, c in zip(bars, costs):
        ax.text(rect.get_x() + rect.get_width() / 2, c + max(costs) * 0.02, f"¥{c}",
                 ha="center", va="bottom", fontsize=9.5, color=INK_SECONDARY)

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=9.5, color=INK_SECONDARY)
    ax.set_ylabel("cost", fontsize=10, color=INK_SECONDARY)
    ax.tick_params(axis="y", colors=INK_MUTED, labelsize=9)
    ax.tick_params(axis="x", length=0)

    selected_sum = sum(costs[i] for i in selected)
    ax.set_title(title, fontsize=12, color=INK_PRIMARY, pad=28)
    ax.text(0.5, 1.04, f"選択合計 = {selected_sum}（目標予算 {target} と一致）",
             transform=ax.transAxes, ha="center", va="bottom", fontsize=10, color=INK_SECONDARY)

    ax.set_ylim(0, max(costs) * 1.28)

    from matplotlib.patches import Patch
    legend_handles = [
        Patch(facecolor=SEQ_BLUE, label="選択"),
        Patch(facecolor=MUTED_GRAY, label="非選択"),
    ]
    ax.legend(handles=legend_handles, loc="upper left", frameon=False, fontsize=9.5,
               labelcolor=INK_SECONDARY)

    fig.tight_layout()
    fig.savefig(out_path, dpi=180, facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {out_path}")


def draw_feature_relevance(features, relevance, selected, out_path, title):
    """features: [str,...], relevance: [float,...] (0-1に正規化済み), selected: 選択されたindex集合"""
    order = sorted(range(len(features)), key=lambda i: relevance[i])
    labels = [features[i] for i in order]
    values = [relevance[i] for i in order]
    colors = [SEQ_BLUE if i in selected else MUTED_GRAY for i in order]

    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color=GRIDLINE, lw=1.0, zorder=0)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)

    y = range(len(labels))
    bars = ax.barh(y, values, height=0.6, color=colors, zorder=3)
    for rect, v in zip(bars, values):
        ax.text(v + 0.015, rect.get_y() + rect.get_height() / 2, f"{v:.2f}",
                 ha="left", va="center", fontsize=9, color=INK_SECONDARY)

    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=9.5, color=INK_SECONDARY)
    ax.set_xlabel("relevance (normalized F-value)", fontsize=10, color=INK_SECONDARY)
    ax.set_xlim(0, 1.15)
    ax.set_title(title, fontsize=12, color=INK_PRIMARY, pad=12)
    ax.tick_params(axis="x", colors=INK_MUTED, labelsize=9)
    ax.tick_params(axis="y", length=0)

    from matplotlib.patches import Patch
    legend_handles = [
        Patch(facecolor=SEQ_BLUE, label="QUBO選択"),
        Patch(facecolor=MUTED_GRAY, label="非選択（冗長 or 低関連度）"),
    ]
    ax.legend(handles=legend_handles, loc="lower right", frameon=False, fontsize=9.5,
               labelcolor=INK_SECONDARY)

    fig.tight_layout()
    fig.savefig(out_path, dpi=180, facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {out_path}")


CAT_ORANGE = "#eb6834"


def draw_return_risk_scatter(assets, out_path, title):
    """assets: [{"label": str, "market": "JP"|"US", "ret": float, "vol": float}, ...]"""
    fig, ax = plt.subplots(figsize=(5.8, 4.6))
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    ax.set_axisbelow(True)
    ax.grid(True, color=GRIDLINE, lw=1.0, zorder=0)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(BASELINE)

    market_color = {"JP": SEQ_BLUE, "US": CAT_ORANGE}
    seen = set()
    for a in assets:
        c = market_color[a["market"]]
        label = a["market"] if a["market"] not in seen else None
        seen.add(a["market"])
        ax.scatter(a["vol"] * 100, a["ret"] * 100, s=110, color=c, zorder=3,
                    edgecolors=SURFACE, linewidths=1.2, label=label)
        dx, dy = a.get("label_offset", (8, 6))
        ax.annotate(a["label"], (a["vol"] * 100, a["ret"] * 100),
                     textcoords="offset points", xytext=(dx, dy), fontsize=9.5, color=INK_SECONDARY)

    ax.axhline(0, color=INK_MUTED, lw=1.0, zorder=1)
    ax.set_xlabel("年率ボラティリティ（％）", fontsize=10, color=INK_SECONDARY)
    ax.set_ylabel("年率リターン（％、USD換算）", fontsize=10, color=INK_SECONDARY)
    ax.set_title(title, fontsize=12, color=INK_PRIMARY, pad=12)
    ax.tick_params(colors=INK_MUTED, labelsize=9)
    legend = ax.legend(loc="upper right", frameon=True, fontsize=9.5, labelcolor=INK_SECONDARY,
                         facecolor=SURFACE, edgecolor=BASELINE, framealpha=1.0)
    legend.get_frame().set_linewidth(1.0)

    fig.tight_layout()
    fig.savefig(out_path, dpi=180, facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {out_path}")


def main():
    ASSETS.mkdir(exist_ok=True)

    draw_circuit(
        gates=[{"gate": "h", "qubits": [0]}, {"gate": "cx", "qubits": [0, 1]}],
        n_qubits=2,
        title="Bell state",
        out_path=ASSETS / "01_bell_state.png",
    )

    draw_circuit(
        gates=[
            {"gate": "h", "qubits": [0]},
            {"gate": "cx", "qubits": [0, 1]},
            {"gate": "cx", "qubits": [1, 2]},
        ],
        n_qubits=3,
        title="GHZ state (3 qubits)",
        out_path=ASSETS / "02_ghz_state.png",
    )

    draw_circuit(
        gates=[
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
            {"gate": "h", "qubits": [1]},
        ],
        n_qubits=2,
        title="Grover search (target |11>, 1 iteration)",
        out_path=ASSETS / "03_grover_search.png",
    )

    draw_triangle_graph(ASSETS / "04_qaoa_maxcut_graph.png")

    draw_circuit(
        gates=[
            {"gate": "ry", "qubits": [0], "label": "RY\nθ0"},
            {"gate": "ry", "qubits": [1], "label": "RY\nθ1"},
            {"gate": "cz", "qubits": [0, 1]},
            {"gate": "ry", "qubits": [0], "label": "RY\nθ2"},
            {"gate": "ry", "qubits": [1], "label": "RY\nθ3"},
            {"gate": "cz", "qubits": [0, 1]},
            {"gate": "ry", "qubits": [0], "label": "RY\nθ4"},
            {"gate": "ry", "qubits": [1], "label": "RY\nθ5"},
        ],
        n_qubits=2,
        title="VQE ansatz (hardware-efficient, layers=2) -- inferred structure",
        out_path=ASSETS / "05_vqe_ansatz.png",
    )

    draw_qrng_histogram(
        counts={"110": 30, "001": 32, "011": 40, "111": 24, "000": 33, "010": 35, "100": 33, "101": 29},
        shots=256,
        out_path=ASSETS / "06_qrng_histogram.png",
        title="3-qubit QRNG: 256 shots (run_id sim_20260827_59a1bc6b732e54fa)",
    )

    draw_budget_items(
        costs=[2, 3, 5, 7],
        selected={0, 1, 2},
        target=10,
        out_path=ASSETS / "07_budget_items.png",
        title="Budget matching QUBO: selected subset",
    )

    draw_return_risk_scatter(
        assets=[
            {"label": "Toyota (7203.T)", "market": "JP", "ret": 0.0094, "vol": 0.3186},
            {"label": "MUFG (8306.T)", "market": "JP", "ret": 0.4557, "vol": 0.3302},
            {"label": "SoftBank G (9984.T)", "market": "JP", "ret": 0.2361, "vol": 0.8857},
            {"label": "Apple (AAPL)", "market": "US", "ret": 0.3365, "vol": 0.2603},
            {"label": "Microsoft (MSFT)", "market": "US", "ret": -0.0135, "vol": 0.3313,
             "label_offset": (8, -14)},
        ],
        out_path=ASSETS / "08_portfolio_return_risk.png",
        title="JP+US basket: annualized return vs. volatility (1y, USD-adjusted)",
    )

    draw_feature_relevance(
        features=[
            "mean radius", "mean texture", "mean perimeter", "mean area",
            "mean smoothness", "mean compactness", "mean concavity",
            "mean concave points", "mean symmetry", "mean fractal dimension",
        ],
        relevance=[0.7169, 0.1041, 0.7729, 0.6144, 0.1037, 0.3666, 0.6828, 1.0, 0.081, 0.0],
        selected={1, 2, 4, 6, 8, 9},
        out_path=ASSETS / "09_feature_selection.png",
        title="QUBO feature selection (breast cancer, mean_* features)",
    )


if __name__ == "__main__":
    main()
