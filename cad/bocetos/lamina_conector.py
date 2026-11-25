"""Lamina tecnica de la pieza del cable (conector del CAT6, D-46). Vistas 11 a 17.

Toma los parametros, helpers y el 3D de la capsula de lamina_capsula.py.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "lamina_capsula.py"), encoding="utf-8").read()
exec(_src.split("# =============== lamina")[0])   # parametros, helpers, B (caja) y L (tapa)

OUT = sys.argv[1] if len(sys.argv) > 1 else r"c:\medidorTHR\output\boceto_conector_4.png"

# ---------------- parametros del conector (aprox.)
CW, CD, CR = 29.0, 36.0, 6.0          # ancho, fondo, esquinas verticales
CX = OUT_W / 2                        # centrado con la cara de la capsula
Y0 = OUT_D                            # cara de union
FRONT = 16.0                          # bloque macizo del frente (bolsillo + hembras + tope)
SLOT_D, STOP_T = 14.5, 1.5            # alojamiento de las hembras y tope
WIRE_W, WIRE_H = 9.0, 2.0             # paso de cables en el tope (no pasan las hembras)
POCK_HT = 3.7                         # alto del bolsillo apretado (sale del cupon: 3.6-3.8)
POCK_ZC = POCK_Z0 + POCK_H / 2
PIN_X = CX + FACE_W / 2 - 3           # pin del conector (entra al hueco de la capsula)
HOLE_X = CX - FACE_W / 2 + 3          # hueco (recibe el pin de la capsula)
PIN_L, PIN_D, HOLE_D, HOLE_DEPTH = 7.0, 3.0, 3.2, 9.0
CAT6_D = 5.5
CAT6_ZC = BODY_H - CAT6_D / 2          # la funda queda al ras arriba: la tapa la prensa
CH_W = 5.0                             # canal mas angosto que la funda (5.5)
RIB_T, RIB_H = 1.2, 0.5                # costillas que muerden la funda
RIBS_BODY = [CD - 11.0, CD - 5.0]      # costillas del cuerpo (y local)
RIB_LID = CD - 8.0                     # costilla de la tapa, entre las otras 2
SAD_Y0 = CD - 13.0                     # silla del cable
SCR = [(CX - 11.0, 12.5), (CX + 8.5, CD - 6.0)]   # tornillos en diagonal (y local)
BOSS_D = 7.0
CIN_X0, CIN_X1 = CX - CW / 2 + WALL, CX + CW / 2 - WALL
CIN_Y0, CIN_Y1 = FRONT, CD - WALL


# ---------------- 3D
def cbody3d():
    b = rbox(CW, CD, BODY_H, CR).translate((CX - CW / 2, Y0, 0))
    try:
        b = b.faces("<Z").edges().fillet(2.5)
    except Exception:
        pass
    cav = (cq.Workplane("XY").workplane(offset=FLOOR).center((CIN_X0 + CIN_X1) / 2, Y0 + (CIN_Y0 + CIN_Y1) / 2)
           .rect(CIN_X1 - CIN_X0, CIN_Y1 - CIN_Y0).extrude(IN_H + 1).edges("|Z").fillet(CR - WALL))
    b = b.cut(cav)
    b = b.cut(cq.Workplane("XY").box(POCK_W, POCK_D * 2, POCK_HT).translate((CX, Y0, POCK_ZC)))
    b = b.cut(cq.Workplane("XY").box(ROW_W, SLOT_D * 2, ROW_H).translate((CX, Y0, ROW_ZC)))
    b = b.cut(cq.Workplane("XY").box(WIRE_W, FRONT * 2, WIRE_H).translate((CX, Y0 + SLOT_D, ROW_ZC)))
    b = b.cut(cq.Workplane("XZ").center(HOLE_X, ROW_ZC).circle(HOLE_D / 2).extrude(-HOLE_DEPTH).translate((0, Y0, 0)))
    b = b.union(cq.Workplane("XZ").center(PIN_X, ROW_ZC).circle(PIN_D / 2).extrude(PIN_L + 2).translate((0, Y0 + 2, 0)))
    # silla del cable (de SAD_Y0 a la pared de atras) con canal en U abierto arriba
    zb = CAT6_ZC - CAT6_D / 2
    sad = cq.Workplane("XY").box(CH_W + 5, CD - SAD_Y0, zb - FLOOR).translate((CX, Y0 + (SAD_Y0 + CD) / 2, (FLOOR + zb) / 2))
    b = b.union(sad)
    for yr in RIBS_BODY:
        b = b.union(cq.Workplane("XY").box(CH_W, RIB_T, RIB_H).translate((CX, Y0 + yr, zb + RIB_H / 2)))
    for x in (CX - CH_W / 2 - 1.25, CX + CH_W / 2 + 1.25):
        b = b.union(cq.Workplane("XY").box(2.5, CD - SAD_Y0 - WALL, BODY_H - zb).translate((x, Y0 + (SAD_Y0 + CD - WALL) / 2, (zb + BODY_H) / 2)))
    b = b.cut(cq.Workplane("XY").box(CH_W, WALL * 3, BODY_H - zb + 1).translate((CX, Y0 + CD, (zb + BODY_H + 1) / 2)))
    x, y = SCR[1]
    b = b.union(cq.Workplane("XY").workplane(offset=FLOOR).center(x, Y0 + y).circle(BOSS_D / 2).extrude(IN_H))
    for x, y in SCR:
        b = b.cut(cq.Workplane("XY").workplane(offset=BODY_H - 5).center(x, Y0 + y).circle(2.0).extrude(6))
    return b


def clid3d():
    l = rbox(CW, CD, LID, CR, BODY_H).translate((CX - CW / 2, Y0, 0))
    try:
        l = l.faces(">Z").edges().fillet(3.0)
    except Exception:
        pass
    for x, y in SCR:
        l = l.cut(cq.Workplane("XY").workplane(offset=BODY_H - 1).center(x, Y0 + y).circle(1.7).extrude(LID + 2))
        l = l.cut(cq.Workplane("XY").add(cq.Solid.makeCone(1.7, 3.2, 1.6, cq.Vector(x, Y0 + y, OUT_H - 1.6))))
    w, d = CIN_X1 - CIN_X0 - 2 * LIP_CL, CIN_Y1 - CIN_Y0 - 2 * LIP_CL
    c = ((CIN_X0 + CIN_X1) / 2, Y0 + (CIN_Y0 + CIN_Y1) / 2)
    ring = (cq.Workplane("XY").workplane(offset=BODY_H - LIP_H).center(*c).rect(w, d).extrude(LIP_H)
            .edges("|Z").fillet(CR - WALL - LIP_CL))
    ring = ring.cut(cq.Workplane("XY").workplane(offset=BODY_H - LIP_H - 1).center(*c)
                    .rect(w - 2 * LIP_W, d - 2 * LIP_W).extrude(LIP_H + 1))
    x, y = SCR[1]
    ring = ring.cut(cq.Workplane("XY").workplane(offset=BODY_H - LIP_H - 1).center(x, Y0 + y).circle(BOSS_D / 2 + 0.3).extrude(LIP_H + 1))
    l = l.union(ring)
    l = l.union(cq.Workplane("XY").box(CH_W, RIB_T, RIB_H).translate((CX, Y0 + RIB_LID, BODY_H - RIB_H / 2)))
    return l


def female3d(dy=0.0):
    return cq.Workplane("XY").box(10.16, 14.0, 2.54).translate((CX, Y0 + 0.5 + 7.0 + dy, ROW_ZC))


def clip3d(dy=0.0):
    return cq.Workplane("XY").box(13.2, 19.5, 3.5).translate((CX, Y0 + dy, POCK_ZC))


def cat6_3d(dy=0.0):
    return (cq.Workplane("XZ").center(CX, CAT6_ZC).circle(CAT6_D / 2).extrude(-(CD - SAD_Y0 + 4 + 14))
            .translate((0, Y0 + SAD_Y0 - 4 + dy, 0)))


K, KL = cbody3d(), clid3d()
CK, CKL, CF, CCL, CCAT = "#6aa6dd", "#a9cdf2", "#2c3e50", "#e9c46a", "#7f8c8d"

# =============== lamina
fig = plt.figure(figsize=(22, 15.5))
gs = fig.add_gridspec(3, 3, height_ratios=[1.05, 0.9, 1.0], width_ratios=[0.85, 1.15, 1.2],
                      hspace=0.22, wspace=0.08, left=0.03, right=0.98, top=0.92, bottom=0.06)
a11 = fig.add_subplot(gs[0:2, 0]); a12 = fig.add_subplot(gs[0, 1]); a13 = fig.add_subplot(gs[1, 1])
a15 = fig.add_subplot(gs[2, 0]); a14 = fig.add_subplot(gs[2, 1])
a16 = fig.add_subplot(gs[0:2, 2], projection="3d"); a17 = fig.add_subplot(gs[2, 2], projection="3d")
lx = lambda x: x - CX          # x local (0 al centro)

# ---- 11 superior
ax = a11; title(ax, "11 · Conector · vista superior (sin tapa)")
rr(ax, -CW / 2, 0, CW, CD, CR, fc=BODY_C, ec=RED, lw=2)
rr(ax, lx(CIN_X0), CIN_Y0, CIN_X1 - CIN_X0, CIN_Y1 - CIN_Y0, CR - WALL, fc="white", ec=RED, lw=1)
ax.add_patch(Rectangle((-ROW_W / 2, 0), ROW_W, SLOT_D, fc="none", ec=GREY, ls="--"))
ax.add_patch(Rectangle((-10.16 / 2, 0.5), 10.16, 14.0, fc="#2c3e50", ec="k", alpha=0.35))
ax.add_patch(Rectangle((-POCK_W / 2, 0), POCK_W, POCK_D, fc="none", ec=GREY, ls=":"))
ax.add_patch(Rectangle((lx(HOLE_X) - HOLE_D / 2, 0), HOLE_D, HOLE_DEPTH, fc="none", ec=GREY, ls="--"))
ax.add_patch(Rectangle((lx(PIN_X) - PIN_D / 2, -PIN_L), PIN_D, PIN_L, fc=BODY_C, ec=RED))
for x, y in SCR:
    ax.add_patch(Circle((lx(x), y), 2.0, fc="#e9c46a", ec="k"))
ax.add_patch(Circle((lx(SCR[1][0]), SCR[1][1]), BOSS_D / 2, fc="none", ec=RED))
for sx in (-1, 1):
    ax.add_patch(Rectangle((sx * (CH_W / 2 + 1.25) - 1.25, SAD_Y0), 2.5, CD - SAD_Y0 - WALL, fc=BODY_C, ec=RED))
ax.add_patch(Rectangle((-CAT6_D / 2, SAD_Y0 - 4), CAT6_D, CD - SAD_Y0 + 4 + 8, fc=CCAT, ec="k", alpha=0.85))
for yr in RIBS_BODY:
    ax.add_patch(Rectangle((-CH_W / 2, yr - RIB_T / 2), CH_W, RIB_T, fc=RED, ec="k"))
ax.add_patch(Rectangle((-CH_W / 2, RIB_LID - RIB_T / 2), CH_W, RIB_T, fc=BLUE, ec="k"))
for i in range(4):
    x = (i - 1.5) * 2.54
    ax.plot([x, x, x * 0.4, x * 0.4], [SLOT_D + 1, SLOT_D + 4, SAD_Y0 - 5, SAD_Y0 - 4], color=GREY, lw=1.2)
ax.text(-CW / 2 + 4.5, (SAD_Y0 + CD) / 2, "prensa", ha="center", va="center", fontsize=FS_N, rotation=90)
ax.text(0, CD + 9.0, "CAT6", ha="center", fontsize=FS_N, color=GREY)
ax.text(CW / 2 - 1, -3.0, "cara de unión", ha="right", va="center", fontsize=FS_N, color=GREY)
dim(ax, -CW / 2, -PIN_L - 2.0, CW / 2, -PIN_L - 2.0, f"{CW:.0f}", (0, -1.3))
dim(ax, CW / 2 + 2.2, 0, CW / 2 + 2.2, CD, f"{CD:.0f}", (1.8, 0), rot=90)
ax.text(-CW / 2 + 0.5, CD - 0.5, "R6", color=RED, fontsize=FS_D, va="top")
finish(ax, (-CW / 2 - 3, CW / 2 + 6), (-PIN_L - 6, CD + 11))

# ---- 12 corte lateral (por el centro)
ax = a12; title(ax, "12 · Conector · corte lateral (por el centro)")
prof = [(0, GOTA_IN), (GOTA_IN, 0), (CD - GOTA_IN, 0), (CD, GOTA_IN), (CD, BODY_H), (CIN_Y1, BODY_H),
        (CIN_Y1, FLOOR), (FRONT, FLOOR), (FRONT, BODY_H), (0, BODY_H)]
ax.add_patch(Polygon(prof, fc=BODY_C, ec=RED, lw=1.6))
ax.add_patch(Polygon([(0, BODY_H), (CD, BODY_H), (CD, OUT_H - GOTA_IN), (CD - GOTA_IN, OUT_H), (GOTA_IN, OUT_H),
                      (0, OUT_H - GOTA_IN)], fc=LID_C, ec=BLUE, lw=1.4))
ax.add_patch(Rectangle((0, POCK_ZC - POCK_HT / 2), POCK_D, POCK_HT, fc="white", ec="k"))
ax.add_patch(Rectangle((-POCK_D + 0.5, POCK_ZC - 1.75), 19.5, 3.5, fc=CCL, ec="k", alpha=0.85))
ax.add_patch(Rectangle((0, ROW_ZC - ROW_H / 2), SLOT_D, ROW_H, fc="white", ec="k"))
ax.add_patch(Rectangle((SLOT_D, ROW_ZC - WIRE_H / 2), STOP_T, WIRE_H, fc="white", ec="k"))
ax.add_patch(Rectangle((0.5, ROW_ZC - 1.27), 14.0, 2.54, fc="#2c3e50", ec="k"))
ax.plot([14.5, FRONT + 2, SAD_Y0 - 4], [ROW_ZC, ROW_ZC, CAT6_ZC], color=GREY, lw=1.5)
_zb = CAT6_ZC - CAT6_D / 2
ax.add_patch(Rectangle((SAD_Y0, FLOOR), CD - WALL - SAD_Y0, _zb - FLOOR, fc=BODY_C, ec=RED))
ax.add_patch(Rectangle((CD - WALL, _zb), WALL, BODY_H - _zb, fc="white", ec=RED, ls="--"))
_yy = [SAD_Y0 - 4, RIBS_BODY[0] - 1, RIBS_BODY[0], RIB_LID, RIBS_BODY[1], RIBS_BODY[1] + 1, CD + 8]
_zz = [CAT6_ZC, CAT6_ZC, CAT6_ZC + 0.35, CAT6_ZC - 0.35, CAT6_ZC + 0.35, CAT6_ZC, CAT6_ZC]
ax.plot(_yy, [z + CAT6_D / 2 for z in _zz], color="k", lw=1)
ax.plot(_yy, [z - CAT6_D / 2 for z in _zz], color="k", lw=1)
ax.fill_between(_yy, [z - CAT6_D / 2 for z in _zz], [z + CAT6_D / 2 for z in _zz], color=CCAT, alpha=0.85)
for yr in RIBS_BODY:
    ax.add_patch(Rectangle((yr - RIB_T / 2, _zb), RIB_T, RIB_H, fc=RED, ec="k"))
ax.add_patch(Rectangle((RIB_LID - RIB_T / 2, BODY_H - RIB_H), RIB_T, RIB_H, fc=BLUE, ec="k"))
dim(ax, 0, -2.2, CD, -2.2, f"{CD:.0f}", (0, -1.3))
dim(ax, CD + 10, 0, CD + 10, OUT_H, f"{OUT_H:.1f}", (2.0, 0))
dim(ax, 0, OUT_H + 1.5, SLOT_D, OUT_H + 1.5, f"{SLOT_D}", (0, 1.1))
ax.text(-POCK_D / 2 - 1, POCK_ZC - 3.5, "clip", ha="center", fontsize=FS_N)
ax.text(SLOT_D / 2, ROW_ZC + 2.3, "4 hembras", ha="center", fontsize=FS_N - 1, color="white",
        bbox=dict(fc="#2c3e50", ec="none", pad=1))
ax.text((SAD_Y0 + CD) / 2, -0.6, "prensa de costillas", ha="center", va="top", fontsize=FS_N)
finish(ax, (-POCK_D - 1, CD + 14), (-5, OUT_H + 4))

# ---- 13 frontal (cara de union, vista desde la capsula)
ax = a13; title(ax, "13 · Conector · cara de unión (vista desde la cápsula)")
ax.add_patch(Polygon([(-CW / 2 + GOTA_IN, 0), (CW / 2 - GOTA_IN, 0), (CW / 2, GOTA_IN), (CW / 2, BODY_H), (-CW / 2, BODY_H),
                      (-CW / 2, GOTA_IN)], fc=BODY_C, ec=RED, lw=1.6))
ax.add_patch(Polygon([(-CW / 2, BODY_H), (CW / 2, BODY_H), (CW / 2, OUT_H - GOTA_IN), (CW / 2 - GOTA_IN, OUT_H),
                      (-CW / 2 + GOTA_IN, OUT_H), (-CW / 2, OUT_H - GOTA_IN)], fc=LID_C, ec=BLUE, lw=1.6))
ax.add_patch(Rectangle((-POCK_W / 2, POCK_ZC - POCK_HT / 2), POCK_W, POCK_HT, fc="white", ec="k"))
ax.add_patch(Rectangle((-ROW_W / 2, ROW_ZC - ROW_H / 2), ROW_W, ROW_H, fc="#2c3e50", ec="k"))
for i, n in enumerate(["GND", "3V3", "SDA", "SCL"]):
    x = (i - 1.5) * 2.54
    ax.add_patch(Rectangle((x - 0.5, ROW_ZC - 0.5), 1.0, 1.0, fc="white", ec="k"))
    ax.text(x, ROW_ZC + 2.0, n, ha="center", va="bottom", fontsize=9, rotation=90)
ax.add_patch(Circle((lx(HOLE_X), ROW_ZC), HOLE_D / 2, fc="white", ec="k"))
ax.add_patch(Circle((lx(PIN_X), ROW_ZC), PIN_D / 2, fc=RED, ec="k"))
ax.text(lx(HOLE_X), ROW_ZC - 2.9, "hueco", ha="center", fontsize=9)
ax.text(lx(PIN_X), ROW_ZC - 2.9, "pin Ø3", ha="center", fontsize=9)
dim(ax, -CW / 2, -2.0, CW / 2, -2.0, f"{CW:.0f}", (0, -1.3))
dim(ax, CW / 2 + 1.8, 0, CW / 2 + 1.8, OUT_H, f"{OUT_H:.1f}", (2.0, 0))
dim(ax, -POCK_W / 2 - 1.5, POCK_ZC - POCK_HT / 2, -POCK_W / 2 - 1.5, POCK_ZC + POCK_HT / 2, "3.6–3.8", (-3.2, 0))
ax.text(0, POCK_ZC, "bolsillo apretado", ha="center", va="center", fontsize=9)
finish(ax, (-CW / 2 - 9, CW / 2 + 6), (-4.5, OUT_H + 2))

# ---- 14 tapa lateral
ax = a14; title(ax, "14 · Tapa del conector · vista lateral")
ax.add_patch(Polygon([(0, 0), (CD, 0), (CD, LID - GOTA_IN), (CD - GOTA_IN, LID), (GOTA_IN, LID), (0, LID - GOTA_IN)],
                     fc=LID_C, ec=BLUE, lw=1.6))
l0, l1 = CIN_Y0 + LIP_CL, CIN_Y1 - LIP_CL
ax.add_patch(Polygon([(l0, 0), (l0, -LIP_H + LIP_C), (l0 + LIP_C, -LIP_H), (l1 - LIP_C, -LIP_H), (l1, -LIP_H + LIP_C), (l1, 0)],
                     fc=LID_C, ec=BLUE, lw=1.2))
for _, y in SCR:
    ax.add_patch(Polygon([(y - 3.2, LID), (y + 3.2, LID), (y + 1.7, LID - 1.6), (y + 1.7, 0), (y - 1.7, 0), (y - 1.7, LID - 1.6)],
                         fc="white", ec="k", ls="--"))
dim(ax, 0, LID + 1.6, CD, LID + 1.6, f"{CD:.0f}", (0, 1.1))
dim(ax, CD + 1.6, 0, CD + 1.6, LID, f"{LID}", (1.6, 0))
dim(ax, l1 + 0.3, -LIP_H, l1 + 0.3, 0, f"{LIP_H}", (1.6, 0))
ax.annotate("labio: entrada 0.8×45°", (l0 + 0.4, -LIP_H + 0.3), (l0 - 12, -LIP_H - 3.0),
            arrowprops=dict(arrowstyle="->", color=BLUE), fontsize=FS_N, color=BLUE)
finish(ax, (-3, CD + 6), (-7, LID + 4))

# ---- 15 tapa superior
ax = a15; title(ax, "15 · Tapa del conector · vista superior")
rr(ax, -CW / 2, 0, CW, CD, CR, fc=LID_C, ec=BLUE, lw=2)
rr(ax, -CW / 2 + GOTA_IN, GOTA_IN, CW - 2 * GOTA_IN, CD - 2 * GOTA_IN, CR - GOTA_IN, fc="none", ec=BLUE, lw=0.7)
for x, y in SCR:
    ax.add_patch(Circle((lx(x), y), 3.2, fc="white", ec="k"))
    ax.add_patch(Circle((lx(x), y), 1.7, fc="#ddd", ec="k"))
ax.text(0, CD * 0.55, "CAT6", ha="center", va="center", fontsize=14, color="#7a9cc6", fontweight="bold")
dim(ax, -CW / 2, -2.0, CW / 2, -2.0, f"{CW:.0f}", (0, -1.3))
ax.text(0, -5.5, "cara de unión ↓", ha="center", fontsize=FS_N, color=GREY)
finish(ax, (-CW / 2 - 3, CW / 2 + 3), (-7, CD + 2))

# ---- 16 / 17 isometricas
title(a16, "16 · Cápsula + conector · isométrica")
draw3d(a16, [tris(B, CB), tris(L, CL3), tris(K, CK), tris(KL, CKL), tris(cat6_3d(), CCAT)], zoom=1.15)
title(a17, "17 · Conector · isométrica explosionada")
EY = 22
draw3d(a17, [tris(clip3d(), CCL, (0, -14, 0)), tris(K, CK), tris(KL, CKL, (0, 0, 16)),
             tris(female3d(), CF, (0, -18, 0)), tris(cat6_3d(), CCAT, (0, 14, 0))], zoom=1.2)

fig.suptitle("Conector del CAT6 (pieza del cable) · boceto 4 · 2026-11-25 · medidas aproximadas en mm",
             fontsize=16, fontweight="bold", y=0.985)
fig.text(0.03, 0.02,
         "Notas:  1) Hembras al ras de la cara (ranura = largo de la hembra − 0.1).   2) Bolsillo OpenLOCK apretado: "
         "alto según el cupón.   3) 2 M3 en diagonal + labio.   4) CAT6 sujeto por 3 costillas (2 abajo, 1 en la tapa).   5) Pin Ø3×7 con base r0.8.",
         fontsize=FS_N + 1)
fig.savefig(OUT, dpi=100)
print(OUT)
