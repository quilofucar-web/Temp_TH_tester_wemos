"""Cupon de retencion del clip OpenLOCK (2026-11-25).

Bloque N: un bolsillo nominal (lado de la capsula).
Bloque T: dos bolsillos lado a lado con el alto reducido (lado del cable),
marcados con puntos en la cara de arriba. Se arma N contra cada bolsillo
de T y se separa: el clip debe quedarse siempre en T.

Orientacion de impresion = la del modelo: bloques acostados, alto del
bolsillo en Z (entre capas), techo en puente. Boca en Y=0.
"""
from pathlib import Path

import cadquery as cq

import parameters as P
from cq_utils import export_versioned

OUT = Path(__file__).resolve().parent.parent / "output"


def openlock_pts():
    """Perfil 2D del bolsillo (X ancho, Y profundidad; boca en Y=0)."""
    hm, hd, hw, hc = (P.OL2_MOUTH_W / 2, P.OL2_MID_W / 2,
                      P.OL2_WAIST_W / 2, P.OL2_CHAMBER_W / 2)
    y1, y2, y3, y4 = (P.OL2_MOUTH_DEPTH, P.OL2_WAIST_DEPTH,
                      P.OL2_WAIST_STRAIGHT_DEPTH, P.OL2_TOTAL_DEPTH)
    return [(-hm, 0), (-hm, y1), (-hd, y1), (-hw, y2), (-hw, y3),
            (-hc, y3), (-hc, y4), (hc, y4), (hc, y3), (hw, y3),
            (hw, y2), (hd, y1), (hm, y1), (hm, 0)]


W1 = P.OL2_CHAMBER_W + 2 * P.OL_COUPON_WALL
D = P.OL2_TOTAL_DEPTH + P.OL_COUPON_WALL
H = P.OL2_BLIND_THICK + 2 * P.OL_COUPON_WALL
ZC = H / 2


def block(n_pockets, heights):
    w = W1 * n_pockets
    b = cq.Workplane("XY").box(w, D, H, centered=(True, False, False))
    xcs = [-w / 2 + W1 * (i + 0.5) for i in range(n_pockets)]
    for xc, ph in zip(xcs, heights):
        p = (cq.Workplane("XY", origin=(xc, 0, ZC - ph / 2))
             .polyline(openlock_pts()).close().extrude(ph))
        b = b.cut(p)
    return b, xcs


def build_n():
    return block(1, [P.OL2_BLIND_THICK])[0]


def build_t():
    b, xcs = block(len(P.OL_COUPON_TIGHT), P.OL_COUPON_TIGHT)
    for xc, n in zip(xcs, P.OL_COUPON_DOTS):
        for i in range(n):
            x = xc + (i - (n - 1) / 2) * P.MARK_DOT_PITCH
            dot = (cq.Workplane("XY", origin=(x, D / 2, H - P.MARK_DOT_DEPTH))
                   .circle(P.MARK_DOT_D / 2).extrude(P.MARK_DOT_DEPTH))
            b = b.cut(dot)
    return b


if __name__ == "__main__":
    for name, s in (("cupon_openlock_N", build_n()), ("cupon_openlock_T", build_t())):
        print(*export_versioned(s, name, OUT))
