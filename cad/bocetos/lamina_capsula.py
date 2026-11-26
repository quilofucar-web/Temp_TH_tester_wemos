"""Lamina tecnica de la capsula del INA219 (boceto; modulo GY-219 medido el 2026-11-25)."""
import sys
import numpy as np
import cadquery as cq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, FancyBboxPatch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

OUT = sys.argv[1] if len(sys.argv) > 1 else r"c:\medidorTHR\output\boceto_capsula_10.png"

# ---------------- parametros (aprox.)
WALL, FLOOR, LID, CL = 2.4, 2.0, 3.5, 0.3
R_OUT, GOTA_R, GOTA_IN = 8.0, 3.5, 2.05
IN_R = 2.0                       # radio interior de las esquinas (antes R_OUT - WALL = 5.6)
EX = 0.293 * (IN_R) - CL
CLX = CL + EX
# GY-219 medido por Carlos (2026-11-25). En la capsula la bornera mira al frente (-Y):
# ML = lado de la bornera (B 20.3), MW = de la bornera al header (A 20.9).
ML, MW, PCB_T = 20.3, 20.9, 1.5
HOLE_D = 2.9                     # 2 barrenos, ambos del lado de la bornera -> M2.5
HOLE_X0, HOLE_X1 = 1.0 + HOLE_D / 2, ML - (1.1 + HOLE_D / 2)   # D2 / D1 (orilla -> orilla del hueco)
HOLE_Y = 2.5 + HOLE_D / 2        # E: orilla de la bornera -> centro del barreno
TB_P, TB_L, TB_D, TB_H = 5.0, 9.7, 10.0, 10.0   # bornera: G1 = G2 = 5.3 (centrada), F 10, J 10
TB_PIN = 1.5                     # L: pines bajo la placa
HDR_Y = 1.8                      # header (desoldado): orilla de atras -> fila de pines (aprox.)
SUP_W, SUP_Y = 1.6, 5.0          # apoyo bajo el lado del header (orilla de atras -> centro)
POST_H = 3.5                     # inserto M2.5x4x3.5 (barreno 4.5, deja 1 de piso) + M2.5 avellanado
GL, GD, GH, GP = 10.0, 7.85, 10.0, 5.0
GAP, WIRE_GAP = 1.0, 5.0         # el cable GND va por la pared derecha
TBH_Z = 1.0 + 5.0 / 2            # K 1.0 + medio hueco de 5 (como la bornera de 2 polos)
G_HOLE_Z0, G_HOLE_H = 0.92, 5.0  # bornera GND (medida)
WIN_W, WIN_H, WIN_R = 9.5, 6.5, 1.0
G_PIN_CUT = 2.0                  # pines de la bornera GND cortados
BACK = 12.8                      # bloque macizo de atras (bolsillo 10.8 + 2)
LIP_W, LIP_H, LIP_C, LIP_CL = 1.2, 2.0, 0.8, 0.2
SLOT_W = 4.5
FACE_W, FACE_H = 25.0, 13.0
POCK_W, POCK_H, POCK_D = 14.0, 4.2, 10.8
ROW_W, ROW_H = 11.0, 3.4

_mxc = WALL + CLX + ML / 2
_gxc = WALL + CLX + ML + GAP + GL / 2
OUT_W = _mxc + _gxc                       # ventanas en espejo respecto al centro
IN_W = OUT_W - 2 * WALL
IN_D = CLX + MW + WIRE_GAP
OUT_D = WALL + IN_D + BACK
HOLE_ZC = FLOOR + POST_H + PCB_T + TBH_Z  # altura comun de los huecos de cable
G_BASE = HOLE_ZC - (G_HOLE_Z0 + G_HOLE_H / 2)
IN_H = max(POST_H + PCB_T + TB_H, G_BASE - FLOOR + GH) + 1.0
BODY_H = FLOOR + IN_H
OUT_H = BODY_H + LID
CAV_Y1 = WALL + IN_D
SCREW_DX = OUT_W / 2 - 6.5           # avellanado a >= 3 de la orilla (fillet de la tapa)

mx0, my0 = WALL + CLX, WALL + CLX
mxc = mx0 + ML / 2
gx0 = mx0 + ML + GAP
gxc = gx0 + GL / 2
gy0 = WALL + CLX
z_pcb = FLOOR + POST_H
FACE_Z0 = FLOOR
POCK_Z0 = FACE_Z0 + 1.6
ROW_ZC = POCK_Z0 + POCK_H + 3.4
SCREW_Y = OUT_D - BACK / 2
posts = [(mx0 + HOLE_X0, my0 + HOLE_Y), (mx0 + HOLE_X1, my0 + HOLE_Y)]

# ---------------- estilo
RED, BLUE, GRN, GREY = "#c0392b", "#1f6fd1", "#2fa84f", "#555"
BODY_C, LID_C = "#f6d9d3", "#d6e7f7"
FS_T, FS_D, FS_N = 13, 11, 11
plt.rcParams.update({"font.size": FS_N})


def dim(ax, x0, y0, x1, y1, t, off=(0, 0), c=RED, rot=0):
    ax.annotate("", (x0, y0), (x1, y1), arrowprops=dict(arrowstyle="<->", color=c, lw=1.1))
    ax.text((x0 + x1) / 2 + off[0], (y0 + y1) / 2 + off[1], t, color=c, fontsize=FS_D,
            ha="center", va="center", rotation=rot)


def rr(ax, x, y, w, h, r, **kw):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", **kw))


def slot(ax, xc, yc, length, w, **kw):
    ax.add_patch(FancyBboxPatch((xc - length / 2 + w / 2, yc), length - w, 0,
                                boxstyle=f"round,pad={w / 2}", **kw))


def title(ax, t):
    ax.set_title(t, fontsize=FS_T, fontweight="bold", loc="left")


def finish(ax, xl, yl):
    ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(*xl); ax.set_ylim(*yl)


# =============== 3D aproximado
def rbox(w, d, h, r, z0=0.0):
    return (cq.Workplane("XY").workplane(offset=z0).center(w / 2, d / 2)
            .rect(w, d).extrude(h).edges("|Z").fillet(r))


def body3d():
    b = rbox(OUT_W, OUT_D, BODY_H, R_OUT)
    try:
        b = b.faces("<Z").edges().fillet(2.5)
    except Exception:
        pass
    cav = (cq.Workplane("XY").workplane(offset=FLOOR).center(WALL + IN_W / 2, WALL + IN_D / 2)
           .rect(IN_W, IN_D).extrude(IN_H + 1).edges("|Z").fillet(IN_R))
    b = b.cut(cav)
    # ventanas del frente
    for xc in (mxc, gxc):
        b = b.cut(cq.Workplane("XZ").center(xc, HOLE_ZC).rect(WIN_W, WIN_H).extrude(-WALL * 3)
                  .translate((0, -WALL, 0)).edges("|Y").fillet(WIN_R))
    b = b.union(cq.Workplane("XY").box(GL + 1.0, GD, G_BASE - FLOOR).translate((gxc, gy0 + GD / 2, (FLOOR + G_BASE) / 2))
                .cut(cq.Workplane("XY").box(GL - 2.0, GD - 2.0, G_BASE - FLOOR).translate((gxc, gy0 + GD / 2, (FLOOR + G_BASE) / 2 + 1.0))))
    # cara del conector
    b = b.cut(cq.Workplane("XY").box(POCK_W, POCK_D * 2, POCK_H).translate((OUT_W / 2, OUT_D, POCK_Z0 + POCK_H / 2)))
    b = b.cut(cq.Workplane("XY").box(ROW_W, BACK * 3, ROW_H).translate((OUT_W / 2, OUT_D, ROW_ZC)))
    b = b.cut(cq.Workplane("XZ").center(OUT_W / 2 + FACE_W / 2 - 3, ROW_ZC).circle(1.6).extrude(-9.5)
              .translate((0, OUT_D, 0)))
    pin = cq.Workplane("XZ").center(OUT_W / 2 - FACE_W / 2 + 3, ROW_ZC).circle(1.5).extrude(-7.0).translate((0, OUT_D + 7.0, 0))
    b = b.union(pin)
    # insertos de la tapa
    for s in (-1, 1):
        b = b.cut(cq.Workplane("XY").workplane(offset=BODY_H - 5).center(OUT_W / 2 + s * SCREW_DX, SCREW_Y)
                  .circle(2.0).extrude(6))
    # postes y costilla
    for x, y in posts:
        b = b.union(cq.Workplane("XY").workplane(offset=FLOOR).center(x, y).circle(2.6).extrude(POST_H))
    b = b.union(cq.Workplane("XY").box(TB_L, TB_D, POST_H).translate((mxc, my0 + TB_D / 2, FLOOR + POST_H / 2)))
    b = b.union(cq.Workplane("XY").box(ML - 6.0, SUP_W, POST_H).translate((mxc, my0 + MW - SUP_Y, FLOOR + POST_H / 2)))
    return b


def lid3d():
    l = rbox(OUT_W, OUT_D, LID, R_OUT, BODY_H)
    try:
        l = l.faces(">Z").edges().fillet(3.0)
    except Exception:
        pass
    for xc, p, yc in ((mxc, TB_P, my0 + TB_D / 2), (gxc, GP, gy0 + GD / 2)):
        l = l.cut(cq.Workplane("XY").workplane(offset=BODY_H - 1).center(xc, yc)
                  .slot2D(p + SLOT_W, SLOT_W).extrude(LID + 2))
    for s in (-1, 1):
        l = l.cut(cq.Workplane("XY").workplane(offset=BODY_H - 1).center(OUT_W / 2 + s * SCREW_DX, SCREW_Y)
                  .circle(1.7).extrude(LID + 2))
        cone = cq.Solid.makeCone(1.7, 3.2, 1.6, cq.Vector(OUT_W / 2 + s * SCREW_DX, SCREW_Y, OUT_H - 1.6))
        l = l.cut(cq.Workplane("XY").add(cone))
    ow, od = IN_W - 2 * LIP_CL, IN_D - 2 * LIP_CL
    ring = (cq.Workplane("XY").workplane(offset=BODY_H - LIP_H).center(WALL + IN_W / 2, WALL + IN_D / 2)
            .rect(ow, od).extrude(LIP_H).edges("|Z").fillet(IN_R - LIP_CL))
    inner = (cq.Workplane("XY").workplane(offset=BODY_H - LIP_H - 1).center(WALL + IN_W / 2, WALL + IN_D / 2)
             .rect(ow - 2 * LIP_W, od - 2 * LIP_W).extrude(LIP_H + 1).edges("|Z").fillet(IN_R - LIP_CL - LIP_W))
    ring = ring.cut(inner)
    ring = ring.cut(cq.Workplane("XY").box(OUT_W - 2 * R_OUT, 6, LIP_H + 2).translate((OUT_W / 2, WALL + 2, BODY_H - LIP_H / 2)))
    l = l.union(ring)
    for x in (WALL + 2.0 + 3.0, OUT_W - WALL - 2.0 - 3.0):
        l = l.union(cq.Workplane("XY").box(6.0, 1.8, 3.2).translate((x, WALL + CL + 0.9, BODY_H - 1.6)))
    return l


def module3d():
    m = cq.Workplane("XY").box(ML, MW, PCB_T).translate((mxc, my0 + MW / 2, z_pcb + PCB_T / 2))
    m = m.union(cq.Workplane("XY").box(TB_L, TB_D, TB_H).translate((mxc, my0 + TB_D / 2, z_pcb + PCB_T + TB_H / 2)))
    return m


def gnd3d():
    return cq.Workplane("XY").box(GL, GD, GH).translate((gxc, gy0 + GD / 2, G_BASE + GH / 2))


def cable3d():
    c = cq.Workplane("XY").box(FACE_W, 22, FACE_H).translate((OUT_W / 2, OUT_D + 11, FACE_Z0 + FACE_H / 2))
    try:
        c = c.edges("|Y").fillet(2.0)
    except Exception:
        pass
    c = c.union(cq.Workplane("XZ").center(OUT_W / 2, FACE_Z0 + FACE_H / 2).circle(2.75).extrude(-18)
                .translate((0, OUT_D + 22 + 18, 0)))
    return c


def tris(shape, color, off=(0, 0, 0)):
    v, t = shape.val().tessellate(0.15, 0.3)
    V = np.array([(p.x + off[0], p.y + off[1], p.z + off[2]) for p in v])
    T = np.array(t)
    return V[T], color


def subdiv(P, maxlen=2.5):
    for _ in range(7):
        e = np.max(np.linalg.norm(P - np.roll(P, 1, axis=1), axis=2), axis=1)
        big = e > maxlen
        if not big.any():
            break
        Q = P[big]
        a, b, c = Q[:, 0], Q[:, 1], Q[:, 2]
        ab, bc, ca = (a + b) / 2, (b + c) / 2, (c + a) / 2
        new = np.concatenate([np.stack([a, ab, ca], 1), np.stack([ab, b, bc], 1),
                              np.stack([ca, bc, c], 1), np.stack([ab, bc, ca], 1)])
        P = np.concatenate([P[~big], new])
    return P


def draw3d(ax, parts, elev=26, azim=-58, zoom=1.0):
    polys, cols = [], []
    el, az = np.radians(elev), np.radians(azim)
    view = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    parts = [(subdiv(P), c) for P, c in parts]
    light = np.array([-0.4, -0.7, 0.9]); light /= np.linalg.norm(light)
    for P, col in parts:
        n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
        nn = np.linalg.norm(n, axis=1, keepdims=True); nn[nn == 0] = 1
        sh = 0.55 + 0.45 * np.clip((n / nn) @ light, -1, 1) * 0.5 + 0.2
        base = np.array(matplotlib.colors.to_rgb(col))
        vis = ((n / nn) @ view) > -0.02
        for tri, s in zip(P[vis], sh[vis]):
            polys.append(tri); cols.append(np.clip(base * s, 0, 1))
    pc = Poly3DCollection(polys, facecolors=cols, edgecolors=cols, linewidths=0.35)
    ax.add_collection3d(pc)
    allp = np.concatenate([p for p, _ in parts]).reshape(-1, 3)
    mn, mx = allp.min(0), allp.max(0)
    ax.set_xlim(mn[0], mx[0]); ax.set_ylim(mn[1], mx[1]); ax.set_zlim(mn[2], mx[2])
    ax.set_box_aspect(mx - mn, zoom=zoom)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()


B, L, M, G, C = body3d(), lid3d(), module3d(), gnd3d(), cable3d()
CB, CL3, CM, CG, CC = "#e07a6b", "#8db8e8", "#a77bd0", "#3fae5a", "#6aa6dd"

# =============== lamina
fig = plt.figure(figsize=(22, 15.5))
gs = fig.add_gridspec(4, 3, height_ratios=[1, 0.8, 0.8, 1], width_ratios=[1, 1, 1.15],
                      hspace=0.18, wspace=0.08, left=0.03, right=0.98, top=0.92, bottom=0.06)
a01 = fig.add_subplot(gs[0:2, 0]); a02 = fig.add_subplot(gs[0, 1]); a08 = fig.add_subplot(gs[1, 1])
a03 = fig.add_subplot(gs[2, 1]); a05 = fig.add_subplot(gs[2:4, 0]); a04 = fig.add_subplot(gs[3, 1])
a06 = fig.add_subplot(gs[0:2, 2], projection="3d"); a07 = fig.add_subplot(gs[2:4, 2], projection="3d")

# ---- 01 caja superior
ax = a01; title(ax, "01 · Caja · vista superior")
rr(ax, 0, 0, OUT_W, OUT_D, R_OUT, fc=BODY_C, ec=RED, lw=2)
rr(ax, WALL, WALL, IN_W, IN_D, IN_R, fc="white", ec=RED, lw=1)
ax.add_patch(Rectangle((OUT_W / 2 - ROW_W / 2, CAV_Y1), ROW_W, BACK, fc="none", ec=GREY, ls="--"))
ax.add_patch(Rectangle((OUT_W / 2 - POCK_W / 2, OUT_D - POCK_D), POCK_W, POCK_D, fc="none", ec=GREY, ls=":"))
for s in (-1, 1):
    ax.add_patch(Circle((OUT_W / 2 + s * SCREW_DX, SCREW_Y), 2.0, fc="#e9c46a", ec="k"))
ax.add_patch(Rectangle((mx0, my0), ML, MW, fc="#c9a7e6", ec="k"))
ax.add_patch(Rectangle((mx0 + 3.0, my0 + MW - SUP_Y - SUP_W / 2), ML - 6.0, SUP_W, fc="none", ec=RED, ls="--"))
for x, y in posts:
    ax.add_patch(Circle((x, y), HOLE_D / 2, fc="white", ec="k"))
for i in range(6):   # de izq. a der.: VIN+ VIN- SDA SCL GND VCC (usados los 4 de la derecha)
    ax.add_patch(Rectangle((mxc + (i - 2.5) * 2.54 - 0.45, my0 + MW - HDR_Y - 0.45), 0.9, 0.9,
                           fc="#888" if i >= 2 else "white", ec="k", lw=0.6))
ax.add_patch(Rectangle((mxc - TB_L / 2, my0), TB_L, TB_D, fc="#4da3e0", ec="k"))
ax.add_patch(Rectangle((gx0, gy0), GL, GD, fc=GRN, ec="k"))
for s in (-1, 1):
    ax.add_patch(Circle((mxc + s * TB_P / 2, my0 + TB_D / 2), 1.0, fc="#ddd", ec="k"))
    ax.add_patch(Circle((gxc + s * GP / 2, gy0 + GD / 2), 1.2, fc="#ddd", ec="k"))
hy = my0 + MW - HDR_Y
ax.add_patch(Rectangle((gx0 - 0.5, gy0), GL + 1.0, GD, fc="none", ec=RED, lw=1, ls="--"))
_xw = WALL + IN_W - 1.5
ax.plot([mxc + 1.5 * 2.54, mxc + 1.5 * 2.54, _xw, _xw, gx0 + GL - 1.0], [hy, hy + 2.2, hy + 2.2, gy0 + GD / 2, gy0 + GD / 2],
        color=GRN, ls="--", lw=2)
for i in range(4):
    x0 = mxc + (i - 0.5) * 2.54
    xe = OUT_W / 2 + (i - 1.5) * 2.54
    ax.plot([x0, x0, xe, xe], [hy, hy + 3.2 + 0.5 * i, hy + 3.2 + 0.5 * i, CAV_Y1], color=GREY, ls=":", lw=1)
for xc, w in ((mxc, WIN_W), (gxc, WIN_W)):
    ax.add_patch(Rectangle((xc - w / 2, 0), w, WALL, fc="white", ec=RED, ls="--"))
ax.text(mxc, my0 + MW / 2 + 1.0, "GY-219", ha="center", fontsize=FS_N)
ax.text(gxc, gy0 + GD + 1.4, "GND (cuna)", ha="center", fontsize=FS_N, color=GRN, fontweight="bold")
ax.text(mxc, -2.0, "VIN+ VIN−", ha="center", va="top", fontsize=FS_N, color=BLUE, fontweight="bold")
dim(ax, 0, -5.8, OUT_W, -5.8, f"{OUT_W:.1f}", (0, -1.4))
dim(ax, -2.5, 0, -2.5, OUT_D, f"{OUT_D:.1f}", (-1.6, 0), rot=90)
ax.text(OUT_W - 2.0, OUT_D - 2.0, "R8", color=RED, fontsize=FS_D, ha="right", va="top")
ax.text(OUT_W / 2, OUT_D + 2.5, "CAT6 ↑", ha="center", fontsize=FS_N, color=GREY)
ax.add_patch(Rectangle((OUT_W / 2 - FACE_W / 2 + 3 - 1.5, OUT_D), 3.0, 7.0, fc=BODY_C, ec=RED))
dim(ax, OUT_W / 2 - FACE_W / 2 + 3 - 3.2, OUT_D, OUT_W / 2 - FACE_W / 2 + 3 - 3.2, OUT_D + 7.0, "7", (-1.2, 0))
ax.text(OUT_W / 2 - FACE_W / 2 + 3, OUT_D + 8.2, "pin Ø3", ha="center", fontsize=9)
finish(ax, (-7, OUT_W + 3), (-10, OUT_D + 10))

# ---- 02 caja corte lateral
ax = a02; title(ax, "02 · Caja · corte lateral (por la bornera del módulo)")
prof = [(GOTA_IN, 0), (OUT_D - GOTA_IN, 0), (OUT_D, GOTA_IN), (OUT_D, BODY_H), (OUT_D - BACK, BODY_H),
        (OUT_D - BACK, FLOOR), (WALL, FLOOR), (WALL, BODY_H), (0, BODY_H), (0, GOTA_IN)]
ax.add_patch(Polygon(prof, fc=BODY_C, ec=RED, lw=1.6))
ax.add_patch(Rectangle((-0.01, HOLE_ZC - WIN_H / 2), WALL + 0.02, WIN_H, fc="white", ec=RED, ls="--"))
ax.add_patch(Rectangle((OUT_D - POCK_D, POCK_Z0), POCK_D, POCK_H, fc="white", ec=GREY, ls="--"))
ax.add_patch(Rectangle((OUT_D - BACK, ROW_ZC - ROW_H / 2), BACK, ROW_H, fc="white", ec=GREY, ls="--"))
ax.add_patch(Rectangle((SCREW_Y - 2.0, BODY_H - 5), 4.0, 5, fc="#e9c46a", ec="k"))
ax.add_patch(Rectangle((my0, FLOOR), TB_D, POST_H, fc=BODY_C, ec=RED, hatch="///"))
ax.add_patch(Rectangle((my0 + MW - SUP_Y - SUP_W / 2, FLOOR), SUP_W, POST_H, fc=BODY_C, ec=RED))
ax.add_patch(Rectangle((my0, z_pcb), MW, PCB_T, fc="#c9a7e6", ec="k"))
ax.add_patch(Rectangle((my0, z_pcb + PCB_T), TB_D, TB_H, fc="#4da3e0", ec="k"))
dim(ax, 0, -2.2, OUT_D, -2.2, f"{OUT_D:.1f}", (0, -1.3))
dim(ax, OUT_D + 2.2, 0, OUT_D + 2.2, BODY_H, f"{BODY_H:.1f}", (2.2, 0))
ax.text(my0 + TB_D / 2, FLOOR + POST_H / 2, "costilla", ha="center", va="center", fontsize=9)
ax.text(my0 + MW - SUP_Y, FLOOR - 1.2, "apoyo", ha="center", va="top", fontsize=9)
ax.text(OUT_D - BACK / 2, BODY_H + 1.2, "inserto M3", ha="center", fontsize=FS_N)
finish(ax, (-3, OUT_D + 7), (-5, BODY_H + 3))

# ---- 03 caja posterior
ax = a03; title(ax, "03 · Caja · vista posterior (desde afuera)")
ax.add_patch(Polygon([(GOTA_IN, 0), (OUT_W - GOTA_IN, 0), (OUT_W, GOTA_IN), (OUT_W, BODY_H), (0, BODY_H), (0, GOTA_IN)],
                     fc=BODY_C, ec=RED, lw=1.6))
fx = OUT_W / 2 - FACE_W / 2
ax.add_patch(Rectangle((fx, FACE_Z0), FACE_W, FACE_H, fc="none", ec=GREY, ls="--"))
ax.add_patch(Rectangle((OUT_W / 2 - POCK_W / 2, POCK_Z0), POCK_W, POCK_H, fc="white", ec="k"))
ax.add_patch(Rectangle((OUT_W / 2 - ROW_W / 2, ROW_ZC - ROW_H / 2), ROW_W, ROW_H, fc="#2c3e50", ec="k"))
for i, n in enumerate(["GND", "3V3", "SDA", "SCL"]):
    x = OUT_W / 2 - (i - 1.5) * 2.54
    ax.add_patch(Circle((x, ROW_ZC), 0.45, fc="gold", ec="k"))
    ax.text(x, ROW_ZC + 2.0, n, ha="center", va="bottom", fontsize=9, rotation=90)
ax.add_patch(Circle((fx + FACE_W - 3, ROW_ZC), 1.5, fc=RED, ec="k"))
ax.add_patch(Circle((fx + 3, ROW_ZC), 1.6, fc="white", ec="k"))
dim(ax, 0, -2.0, OUT_W, -2.0, f"{OUT_W:.1f}", (0, -1.3))
dim(ax, fx, BODY_H + 1.3, fx + FACE_W, BODY_H + 1.3, f"{FACE_W:.0f}", (0, 1.1))
dim(ax, OUT_W + 1.8, FACE_Z0, OUT_W + 1.8, FACE_Z0 + FACE_H, f"{FACE_H:.0f}", (1.8, 0))
ax.text(fx + FACE_W - 3, ROW_ZC - 2.8, "pin Ø3", ha="center", fontsize=9)
ax.text(fx + 3, ROW_ZC - 2.8, "hueco", ha="center", fontsize=9)
finish(ax, (-3, OUT_W + 6), (-4.5, BODY_H + 4))

# ---- 08 caja frontal
ax = a08; title(ax, "08 · Caja · vista frontal")
ax.add_patch(Polygon([(GOTA_IN, 0), (OUT_W - GOTA_IN, 0), (OUT_W, GOTA_IN), (OUT_W, BODY_H), (0, BODY_H), (0, GOTA_IN)],
                     fc=BODY_C, ec=RED, lw=1.6))
ax.add_patch(Polygon([(0, BODY_H), (OUT_W, BODY_H), (OUT_W, OUT_H - GOTA_IN), (OUT_W - GOTA_IN, OUT_H),
                      (GOTA_IN, OUT_H), (0, OUT_H - GOTA_IN)], fc=LID_C, ec=BLUE, lw=1.6))
ax.plot([OUT_W / 2, OUT_W / 2], [-1, OUT_H + 1], color=GREY, ls=(0, (8, 3, 2, 3)), lw=0.8)
ax.plot([-1, OUT_W + 1], [HOLE_ZC, HOLE_ZC], color=GREY, ls=(0, (8, 3, 2, 3)), lw=0.8)
for xc in (mxc, gxc):
    rr(ax, xc - WIN_W / 2, HOLE_ZC - WIN_H / 2, WIN_W, WIN_H, WIN_R, fc="white", ec="k", lw=1.4)
for sx in (-1, 1):
    ax.add_patch(Rectangle((mxc + sx * TB_P / 2 - 2.0, HOLE_ZC - 2.5), 4.0, 5.0, fc="none", ec=BLUE, ls="--"))
    ax.add_patch(Rectangle((gxc + sx * GP / 2 - 2.0, HOLE_ZC - 2.5), 4.0, 5.0, fc="none", ec=GRN, ls="--"))
ax.text(mxc, HOLE_ZC + WIN_H / 2 + 0.6, "VIN+  VIN−", ha="center", va="bottom", fontsize=FS_N, color=BLUE, fontweight="bold")
ax.text(gxc, HOLE_ZC + WIN_H / 2 + 0.6, "GND  GND", ha="center", va="bottom", fontsize=FS_N, color=GRN, fontweight="bold")
dim(ax, 0, -2.0, OUT_W, -2.0, f"{OUT_W:.1f}", (0, -1.3))
dim(ax, OUT_W + 1.8, 0, OUT_W + 1.8, OUT_H, f"{OUT_H:.1f}", (2.0, 0))
dim(ax, -1.8, 0, -1.8, HOLE_ZC, f"{HOLE_ZC:.1f}", (-1.8, 0))
dim(ax, mxc, HOLE_ZC - WIN_H / 2 - 1.4, gxc, HOLE_ZC - WIN_H / 2 - 1.4, f"{gxc - mxc:.1f}", (0, -1.1))
ax.text(gxc + WIN_W / 2 + 0.8, HOLE_ZC, f"{WIN_W}×{WIN_H}", ha="left", va="center", fontsize=FS_D, color=RED)
finish(ax, (-5, OUT_W + 6), (-4.5, OUT_H + 2))

# ---- 04 tapa lateral
ax = a04; title(ax, "04 · Tapa · vista lateral (frente a la izquierda)")
z0 = 0.0
ax.add_patch(Polygon([(0, z0), (OUT_D, z0), (OUT_D, z0 + LID - GOTA_IN), (OUT_D - GOTA_IN, z0 + LID),
                      (GOTA_IN, z0 + LID), (0, z0 + LID - GOTA_IN)], fc=LID_C, ec=BLUE, lw=1.6))
lx0, lx1 = WALL + LIP_CL, CAV_Y1 - LIP_CL
ax.add_patch(Polygon([(lx0, z0), (lx0, z0 - LIP_H + LIP_C), (lx0 + LIP_C, z0 - LIP_H), (lx1 - LIP_C, z0 - LIP_H),
                      (lx1, z0 - LIP_H + LIP_C), (lx1, z0)], fc=LID_C, ec=BLUE, lw=1.2))
ax.add_patch(Rectangle((WALL + CL, z0 - 3.2), 1.8, 3.2, fc="#9cc3ec", ec=BLUE, lw=1.2))
for s in (-1,):
    ax.add_patch(Polygon([(SCREW_Y - 3.2, z0 + LID), (SCREW_Y + 3.2, z0 + LID), (SCREW_Y + 1.7, z0 + LID - 1.6),
                          (SCREW_Y + 1.7, z0), (SCREW_Y - 1.7, z0), (SCREW_Y - 1.7, z0 + LID - 1.6)],
                         fc="white", ec="k", ls="--"))
dim(ax, 0, LID + 1.6, OUT_D, LID + 1.6, f"{OUT_D:.1f}", (0, 1.1))
dim(ax, OUT_D + 1.6, z0, OUT_D + 1.6, z0 + LID, f"{LID}", (1.6, 0))
dim(ax, lx1 + 1.4, z0 - LIP_H, lx1 + 1.4, z0, f"{LIP_H}", (1.6, 0))
ax.annotate("labio: entrada 0.8×45°", (lx0 + 0.4, z0 - LIP_H + 0.3), (lx0 + 5, z0 - LIP_H - 3.2),
            arrowprops=dict(arrowstyle="->", color=BLUE), fontsize=FS_N, color=BLUE)
ax.annotate("lengüeta", (WALL + CL + 0.9, z0 - 3.2), (WALL - 1, z0 - 6.0),
            arrowprops=dict(arrowstyle="->", color=BLUE), fontsize=FS_N, color=BLUE)
ax.text(SCREW_Y, LID + 3.6, "M3 avellanado", ha="center", fontsize=FS_N)
finish(ax, (-3, OUT_D + 6), (-8, LID + 6))

# ---- 05 tapa superior
ax = a05; title(ax, "05 · Tapa · vista superior")
rr(ax, 0, 0, OUT_W, OUT_D, R_OUT, fc=LID_C, ec=BLUE, lw=2)
rr(ax, GOTA_IN, GOTA_IN, OUT_W - 2 * GOTA_IN, OUT_D - 2 * GOTA_IN, R_OUT - GOTA_IN, fc="none", ec=BLUE, lw=0.7)
for xc, p, yc, labs, col in ((mxc, TB_P, my0 + TB_D / 2, ("VIN+", "VIN−"), BLUE),
                             (gxc, GP, gy0 + GD / 2, ("GND", "GND"), GRN)):
    slot(ax, xc, yc, p + SLOT_W, SLOT_W, fc="white", ec="k")
    for s, lab in zip((-1, 1), labs):
        ax.text(xc + s * (p / 2 + 0.6), yc + SLOT_W / 2 + 1.0, lab, ha="left" if s > 0 else "right",
                fontsize=FS_N - 1, color=col, fontweight="bold")
    dim(ax, xc - (p + SLOT_W) / 2, yc - SLOT_W / 2 - 1.6, xc + (p + SLOT_W) / 2, yc - SLOT_W / 2 - 1.6,
        f"{p + SLOT_W:.1f}×{SLOT_W}", (0, -1.4))
for s in (-1, 1):
    ax.add_patch(Circle((OUT_W / 2 + s * SCREW_DX, SCREW_Y), 3.2, fc="white", ec="k"))
    ax.add_patch(Circle((OUT_W / 2 + s * SCREW_DX, SCREW_Y), 1.7, fc="#ddd", ec="k"))
ax.text(OUT_W / 2, OUT_D * 0.6, "INA219", ha="center", va="center", fontsize=16, color="#7a9cc6", fontweight="bold")
dim(ax, 0, -6.5, OUT_W, -6.5, f"{OUT_W:.1f}", (0, -1.4))
finish(ax, (-3, OUT_W + 3), (-10, OUT_D + 2))

# ---- 06 / 07 isometricas
title(a06, "06 · Ensamble · isométrica")
draw3d(a06, [tris(B, CB), tris(L, CL3), tris(C, CC)], zoom=1.15)
title(a07, "07 · Ensamble · isométrica explosionada")
draw3d(a07, [tris(B, CB), tris(M, CM, (0, 0, 14)), tris(G, CG, (0, 0, 14)), tris(L, CL3, (0, 0, 34)),
             tris(C, CC, (0, 26, 0))], zoom=1.15)

# ---- notas y cuadro de datos
fig.suptitle("Cápsula INA219 · boceto 15 · 2026-11-25 · mm (módulo medido; caja aprox.)", fontsize=16, fontweight="bold", y=0.985)
fig.text(0.03, 0.02,
         "Notas:  1) GY-219 medido; postes con inserto M2.5×4×3.5 y M2.5 avellanado.   2) Esquinas R8; orillas de base y tapa en gota r3.5.   "
         "3) Machos en la cápsula, hembras en el cable (D-46).   4) Labio sin tramo al frente.   5) Pines de la bornera GND cortados a 2.",
         fontsize=FS_N + 1)
fig.savefig(OUT, dpi=100)
print(OUT, round(OUT_W, 1), round(OUT_D, 1), round(OUT_H, 1))
