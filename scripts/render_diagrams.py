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

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch

ASSETS = Path(__file__).resolve().parent.parent / "assets"

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


if __name__ == "__main__":
    main()
