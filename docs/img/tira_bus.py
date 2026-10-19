"""Genera el diagrama 2D de la tira de bus (docs/img/tira_bus_N.png).

Cada conexion externa se marca con un numero en su agujero y se explica en la
leyenda (asi ningun cable dibujado cruza sobre otras tiras). Solo los 2
puentes se dibujan como lineas, porque si van sobre la placa.

Uso:  cd docs/img && python3 tira_bus.py
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "cad"))
from cq_utils import next_version_number, versioned  # noqa: E402

PITCH = 2.54
COLS, ROWS = 10, 6
STRIPS = [("1", "3V3", "#d62728"), ("2", "GND", "#222222"), ("3", "SCL", "#c79a00"),
          ("4", "SDA", "#1f77b4"), ("5", "CSB", "#8c564b"), ("6", "SDO", "#7f7f7f")]

# (numero, columna, tira, color del marcador, texto de la leyenda, grupo)
CONEXIONES = [
    (1, 1, 1, "#d62728", "3V3 del Wemos", "WEMOS (un solo cable por pad)"),
    (2, 1, 2, "#222222", "GND del Wemos", "WEMOS (un solo cable por pad)"),
    (3, 1, 3, "#c79a00", "D1 (SCL) del Wemos", "WEMOS (un solo cable por pad)"),
    (4, 1, 4, "#1f77b4", "D2 (SDA) del Wemos", "WEMOS (un solo cable por pad)"),
    (5, 3, 1, "#4a90d9", "CAT6 azul (3V3)", "CAT6 AL SENSOR REMOTO 0x77 (soldado directo)"),
    (6, 4, 1, "#a9c8ec", "CAT6 blanco-azul (3V3)", "CAT6 AL SENSOR REMOTO 0x77 (soldado directo)"),
    (7, 3, 2, "#f4b183", "CAT6 blanco-naranja (GND)", "CAT6 AL SENSOR REMOTO 0x77 (soldado directo)"),
    (8, 4, 2, "#9fd89f", "CAT6 blanco-verde (GND)", "CAT6 AL SENSOR REMOTO 0x77 (soldado directo)"),
    (9, 3, 3, "#2ca02c", "CAT6 verde (SCL)", "CAT6 AL SENSOR REMOTO 0x77 (soldado directo)"),
    (10, 3, 4, "#ff7f0e", "CAT6 naranja (SDA)", "CAT6 AL SENSOR REMOTO 0x77 (soldado directo)"),
    (11, 6, 2, "#222222", "GND al LCD (cable al Dupont del PCF8574)", "OTROS GND"),
    (12, 7, 2, "#222222", "GND al botón (su otro polo va a D7)", "OTROS GND"),
]


def xy(col, row):
    """Centro del agujero (col 1..COLS, tira 1..ROWS; tira 1 arriba)."""
    return col * PITCH, (ROWS + 1 - row) * PITCH


def main():
    fig, ax = plt.subplots(figsize=(15, 9))
    w, h = (COLS + 1) * PITCH, (ROWS + 1) * PITCH
    ax.add_patch(FancyBboxPatch((0, 0), w, h, boxstyle="round,pad=0.2",
                                fc="#e9d8a6", ec="#9c8b5e", lw=1.5, zorder=0))
    for i, (num, sig, col) in enumerate(STRIPS, start=1):
        _, y = xy(1, i)
        ax.add_patch(Rectangle((PITCH * 0.55, y - 0.9), (COLS - 0.1) * PITCH, 1.8,
                               fc="#d9a066", ec="#b07a3a", lw=0.8, zorder=1))
        ax.text(-0.6, y, f"tira {num}  {sig}", ha="right", va="center",
                fontsize=11, color=col, fontweight="bold")
        for c in range(1, COLS + 1):
            ax.plot(*xy(c, i), "o", ms=4.5, mfc="white", mec="#7a5a2a", zorder=2)
    for c in range(1, COLS + 1):
        ax.text(xy(c, 1)[0], h + 0.5, str(c), ha="center", fontsize=7, color="#7a5a2a")

    # marcadores numerados
    for n, c, r, colr, _, _ in CONEXIONES:
        x, y = xy(c, r)
        ax.add_patch(Circle((x, y), 1.05, fc=colr, ec="k", lw=0.8, zorder=6))
        dark = colr in ("#222222", "#d62728", "#1f77b4", "#2ca02c", "#4a90d9")
        ax.text(x, y, str(n), ha="center", va="center", fontsize=7.5,
                color="white" if dark else "black", fontweight="bold", zorder=7)

    # puentes (cables sobre la placa)
    for c, r0, r1, colr in [(8, 5, 1, "#d62728"), (9, 6, 2, "#222222")]:
        (x, y0), (_, y1) = xy(c, r0), xy(c, r1)
        ax.plot([x, x], [y0, y1], color=colr, lw=2.6, ls="--", zorder=5)
        ax.plot([x, x], [y0, y1], "o", color=colr, ms=7, zorder=6)
    ax.text(xy(8, 5)[0], -1.4, "A", ha="center", fontsize=10, fontweight="bold", color="#d62728")
    ax.text(xy(9, 6)[0], -1.4, "B", ha="center", fontsize=10, fontweight="bold")

    # cabezal hembra + BME280 de ambiente
    x10 = xy(COLS, 1)[0]
    ax.add_patch(Rectangle((x10 - 1.2, xy(1, ROWS)[1] - 1.3), 2.4, (ROWS - 1) * PITCH + 2.6,
                           fc="#333", ec="k", zorder=6))
    for r in range(1, ROWS + 1):
        ax.plot(*xy(COLS, r), "s", ms=5, mfc="#bbb", mec="k", zorder=7)
    bme_y0 = xy(1, ROWS)[1] - 1.9
    ax.add_patch(Rectangle((x10 + 1.6, bme_y0), 11.5, 15.3, fc="#6a3d9a", ec="k",
                           alpha=0.9, zorder=6))
    for r, p in enumerate(["VCC", "GND", "SCL", "SDA", "CSB", "SDO"], start=1):
        ax.text(x10 + 2.3, xy(1, r)[1], p, color="white", fontsize=8, va="center", zorder=8)
    ax.text(x10 + 8.2, bme_y0 + 7.6, "BME280\nAMBIENTE\n0x76", color="white",
            ha="center", va="center", fontsize=9.5, fontweight="bold", zorder=8)
    ax.text(x10 + 7.4, bme_y0 - 1.4, "C: cabezal hembra 6 pines (col. 10)\n"
            "el BME asoma del borde → ranura al\ncompartimento inferior (D-04)",
            ha="center", va="top", fontsize=8.5)

    # leyenda
    lx, ly = 44, h + 1.5
    grupo_actual = None
    for n, _, _, colr, txt, grupo in CONEXIONES:
        if grupo != grupo_actual:
            ly -= 1.2
            ax.text(lx, ly, grupo, fontsize=9.5, fontweight="bold", va="center")
            ly -= 1.9
            grupo_actual = grupo
        ax.plot(lx + 0.9, ly, "o", ms=15, mfc=colr, mec="k", mew=0.6, zorder=6)
        ax.text(lx + 0.9, ly, str(n), ha="center", va="center", fontsize=6.5, zorder=7,
                color="white" if colr in ("#222222", "#d62728", "#1f77b4", "#2ca02c", "#4a90d9")
                else "black", fontweight="bold")
        ax.text(lx + 2.4, ly, txt, fontsize=9, va="center")
        ly -= 1.9
    ly -= 1.2
    ax.text(lx, ly, "PUENTES SOBRE LA PLACA", fontsize=9.5, fontweight="bold", va="center")
    for letra, txt in [("A", "tira 5 (CSB) → tira 1 (3V3): BME en modo I2C"),
                       ("B", "tira 6 (SDO) → tira 2 (GND): dirección 0x76")]:
        ly -= 1.9
        ax.text(lx + 0.9, ly, letra, ha="center", va="center", fontsize=9.5, fontweight="bold")
        ax.text(lx + 2.4, ly, txt, fontsize=9, va="center")
    ly -= 3.0
    ax.text(lx, ly,
            "Notas:\n"
            "• Tiras de cobre continuas, SIN cortes.\n"
            "• 3V3 y GND del CAT6: 2 hilos por señal (pares trenzados,\n"
            "   D-02), cada uno en su propio agujero de la misma tira.\n"
            "• La bornera de desconexión va en la CÁPSULA remota:\n"
            "   una bornera de paso 5.08 no cae en tiras vecinas\n"
            "   (paso 2.54).\n"
            "• Verificar el orden de pines de TU módulo BME antes\n"
            "   de soldar el cabezal.",
            fontsize=8.8, va="top")

    ax.set_title("Tira de bus — stripboard 6 tiras × 10 agujeros (paso 2.54 mm, ≈ 28 × 18 mm), "
                 "vista del lado de componentes (cobre dibujado por transparencia)", fontsize=11.5)
    ax.set_xlim(-12, 82)
    ax.set_ylim(ly - 2, h + 3)          # que la leyenda completa quede dentro de los ejes
    ax.set_aspect("equal")
    ax.axis("off")

    out = HERE / "tira_bus.png"
    path = versioned(out, next_version_number(out))
    fig.savefig(path, dpi=110, bbox_inches="tight")
    print(path)


if __name__ == "__main__":
    main()
