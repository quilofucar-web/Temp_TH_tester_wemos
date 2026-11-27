"""Conector del CAT6 (pieza del cable), checkpoint 1: cuerpo, tapa y cara de union.

Cuerpo: caja de esquinas R4 en la cara de union y R6 atras, orilla de la base
en gota r3.5. Cara de union (en espejo con la capsula): bolsillo OpenLOCK
apretado de 3.8, ranura de las 4 hembras (fondo = largo - 0.1) con tope y paso
de cables, pin en gota a +X y hueco a -X. Atras, la prensa del CAT6: silla con
canal en U de 5.0, 2 costillas abajo y salida por la pared de atras. 2 postes
M3 en diagonal.

Tapa: placa con la orilla de arriba en gota, labio completo con entrada a 45
grados, costilla que muerde la funda entre las 2 del cuerpo y 2 M3 avellanados.

Coordenadas de la capsula (parameters.py): la cara de union esta en Y = CAP_D.
El cuerpo se imprime sobre su base; la tapa, boca abajo.

Uso:  cd cad && python3 conector.py
"""
from pathlib import Path

import cadquery as cq

import parameters as P
from capsula import (build_assembly as capsule_assembly, cyl_z, drop_xz, gota, hole_csk,
                     prism_y, rrect_prism)
from cq_utils import export_assembly_versioned, export_versioned
from geom import box_between

OUTPUT = Path(__file__).resolve().parent.parent / "output"

Y0 = P.CAP_D                       # cara de union
Y1 = P.CAP_D + P.CON_D             # cara de atras
XW = P.CON_W / 2


def ly(y):
    """y local (desde la cara de union) -> y de la capsula."""
    return Y0 + y


def outline(z0, z1):
    """Planta del conector: R4 en la cara de union, R6 atras."""
    s = box_between((-XW, Y0, z0), (XW, Y1, z1))
    s = s.edges("|Z and >Y").fillet(P.CON_R_BACK)
    return s.edges("|Z and <Y").fillet(P.CON_R_FACE)


def _cavity(z0, z1, inset=0.0):
    r = P.CAP_IN_R - inset
    return rrect_prism(-XW + P.CAP_WALL + inset, ly(P.CON_FRONT) + inset,
                       XW - P.CAP_WALL - inset, Y1 - P.CAP_WALL - inset,
                       z0, z1, r if r > 0.05 else 0.05)


def screws():
    return [(x, ly(y)) for x, y in P.CON_SCREWS]


def boss_fill(i, grow=0.0):
    """Relleno entre el poste i y sus paredes: el poste queda redondo solo
    hacia la cavidad, sin medias lunas. El de atras tambien se une a la pared
    del canal del CAT6 (sin rendija)."""
    x, y = screws()[i]
    r, g = P.CON_BOSS_D / 2, grow
    z0, z1 = P.CAP_FLOOR - 0.5, P.CAP_BODY_H
    xw = XW - P.CAP_WALL + 0.5
    if i == 1:                                    # atras a la der.: pared lateral y de atras
        yw = Y1 - P.CAP_WALL + 0.5
        return (box_between((x - r - g, y - g, z0), (xw + g, yw + g, z1))
                .union(box_between((x - g, y - r - g, z0), (xw + g, yw + g, z1)))
                .union(box_between((P.CON_CH_W / 2 + P.CON_SAD_WALL - 0.1 - g, y - g, z0), (x + g, yw + g, z1))))
    yf = ly(P.CON_FRONT) - 0.5                    # adelante a la izq.: pared lateral y bloque del frente
    return (box_between((-xw - g, yf - g, z0), (x + r + g, y + g, z1))
            .union(box_between((-xw - g, yf - g, z0), (x + g, y + r + g, z1))))


def cat6_zc():
    return P.CAP_BODY_H - P.CAT6_D / 2          # la funda queda al ras: la tapa la prensa


def openlock_pocket_out(y_face, z0, h):
    """Bolsillo OpenLOCK con la boca en y_face, hacia +Y."""
    from cupon_openlock import openlock_pts
    pts = [(x, y_face + (y if y > 0 else -0.5)) for x, y in openlock_pts()]
    return cq.Workplane("XY", origin=(0, 0, z0)).polyline(pts).close().extrude(h)


# ---------------------------------------------------------------- cuerpo
def build_body():
    h = P.CAP_BODY_H
    zr = P.CAP_ROW_ZC
    b = outline(0, h)
    b = gota(b, "<Z", 0.0)
    b = b.cut(_cavity(P.CAP_FLOOR, h + 1))
    # prensa del CAT6: silla con canal en U abierto arriba y 2 costillas
    zb = cat6_zc() - P.CAT6_D / 2
    ys0, ys1 = Y1 - P.CON_SAD_L, Y1 - P.CAP_WALL + 0.5
    xs = P.CON_CH_W / 2 + P.CON_SAD_WALL
    b = b.union(box_between((-xs, ys0, P.CAP_FLOOR - 0.5), (xs, ys1, zb)))
    for sx in (-1, 1):
        b = b.union(box_between((sx * P.CON_CH_W / 2, ys0, zb - 0.5), (sx * xs, ys1, h)))
    for yr in P.CON_RIBS_BODY:
        b = b.union(box_between((-P.CON_CH_W / 2, ly(yr) - P.CON_RIB_T / 2, zb - 0.5),
                                (P.CON_CH_W / 2, ly(yr) + P.CON_RIB_T / 2, zb + P.CON_RIB_H)))
    b = b.cut(box_between((-P.CON_CH_W / 2, Y1 - P.CAP_WALL, zb), (P.CON_CH_W / 2, Y1 + 1, h + 1)))
    # esquinas del frente de la prensa cortadas a 45 grados (vista superior)
    c = P.CON_SAD_CH
    for sx in (-1, 1):
        tri = [(sx * (xs - c), ys0 - 1), (sx * (xs + 1), ys0 - 1), (sx * (xs + 1), ys0 + c + 1)]
        b = b.cut(cq.Workplane("XY", origin=(0, 0, P.CAP_FLOOR)).polyline(tri).close().extrude(h))
    # postes de los M3 en diagonal
    for x, y in screws():
        b = b.union(cyl_z(x, y, P.CON_BOSS_D, P.CAP_FLOOR - 0.5, h))
    keep = _cavity(P.CAP_FLOOR - 0.5, h, -0.5)    # el relleno solo entra 0.5 a las paredes
    for i in range(2):
        b = b.union(boss_fill(i).intersect(keep))
    # cara de union (despues de los postes: el de la izq. llega hasta el hueco del pin)
    # bolsillo apretado, centrado en el de la capsula
    zc = P.CAP_POCK_Z0 + P.CAP_POCK_H / 2
    b = b.cut(openlock_pocket_out(Y0, zc - P.CON_POCK_H / 2, P.CON_POCK_H))
    # hembras: ranura con fondo = largo - 0.1, tope y paso de cables
    b = b.cut(box_between((-P.CAP_ROW_W / 2, Y0 - 1, zr - P.CAP_ROW_H / 2),
                          (P.CAP_ROW_W / 2, ly(P.DUP_F_SLOT_DEPTH), zr + P.CAP_ROW_H / 2)))
    b = b.cut(box_between((-P.CAP_ROW_WIRE_W / 2, ly(P.DUP_F_SLOT_DEPTH) - 0.1, zr - P.CAP_ROW_WIRE_H / 2),
                          (P.CAP_ROW_WIRE_W / 2, ly(P.CON_FRONT) + 1, zr + P.CAP_ROW_WIRE_H / 2)))
    # hueco del pin de la capsula (-X)
    b = b.cut(prism_y(drop_xz(-P.CAP_PIN_DX, zr, P.CAP_HOLE_D / 2, up=True, down=True),
                      Y0 - 1, P.CAP_HOLE_DEPTH + 1))
    b = b.cut(hole_csk(-P.CAP_PIN_DX, zr, Y0, 1))
    # pin (+X): gota con la punta abajo, punta con chaflan, base con redondeo
    pin = prism_y(drop_xz(P.CAP_PIN_DX, zr, P.CAP_PIN_D / 2, down=True), Y0 - P.CAP_PIN_L, P.CAP_PIN_L + 0.5)
    pin = pin.faces("<Y").edges().chamfer(P.CAP_PIN_TIP_C)
    b = b.union(pin)
    sel = cq.selectors.BoxSelector((P.CAP_PIN_DX - 3, Y0 - 0.01, zr - 3), (P.CAP_PIN_DX + 3, Y0 + 0.01, zr + 3))
    b = b.edges(sel).fillet(P.CAP_PIN_ROOT_R)
    for x, y in screws():
        b = b.cut(cyl_z(x, y, P.INS_M3_HOLE_D, h - P.CAP_INS_M3_DEPTH, h + 1))
    return b


# ---------------------------------------------------------------- tapa
def build_lid():
    z0, z1 = P.CAP_BODY_H, P.CAP_H
    lid = outline(z0, z1)
    lid = gota(lid, ">Z", z1, min(P.CAP_GOTA_R, P.CAP_LID_T - 0.05))
    ring = _cavity(z0 - P.CAP_LIP_H, z0, P.CAP_LIP_CL)
    ring = ring.faces("<Z").edges().chamfer(P.CAP_LIP_C)
    ring = ring.cut(_cavity(z0 - P.CAP_LIP_H - 1, z0 + 1, P.CAP_LIP_CL + P.CAP_LIP_W))
    for x, y in screws():                         # libra los postes
        ring = ring.cut(cyl_z(x, y, P.CON_BOSS_D + 2 * P.CAP_LIP_CL, z0 - P.CAP_LIP_H - 1, z0 + 1))
    for i in range(2):
        ring = ring.cut(boss_fill(i, P.CAP_LIP_CL).translate((0, 0, 2.0)))
    xs = P.CON_CH_W / 2 + P.CON_SAD_WALL + P.CAP_LIP_CL   # libra la prensa y el CAT6
    ring = ring.cut(box_between((-xs, Y1 - P.CON_SAD_L - P.CAP_LIP_CL, z0 - P.CAP_LIP_H - 1), (xs, Y1, z0 + 1)))
    lid = lid.union(ring)
    lid = lid.union(box_between((-P.CON_CH_W / 2, ly(P.CON_RIB_LID) - P.CON_RIB_T / 2, z0 - P.CON_RIB_H),
                                (P.CON_CH_W / 2, ly(P.CON_RIB_LID) + P.CON_RIB_T / 2, z0 + 0.5)))
    d = P.M3_CSK_D + 2 * P.M3_CSK_CLEAR
    for x, y in screws():
        lid = lid.cut(cyl_z(x, y, P.M3_CLEAR_D, z0 - 1, z1 + 1))
        hc = (d - P.M3_CLEAR_D) / 2
        lid = lid.cut(cq.Workplane(obj=cq.Solid.makeCone(
            P.M3_CLEAR_D / 2, d / 2 + 1.0, hc + 1.0, cq.Vector(x, y, z1 - hc), cq.Vector(0, 0, 1))))
    return lid


def build_body_print():
    return build_body().translate((0, -Y0, 0))


def build_lid_print():
    return build_lid().rotate((0, 0, 0), (0, 1, 0), 180).translate((0, -Y0, P.CAP_H))


# ---------------------------------------------------------------- envolventes
def female_envelope():
    """Las 4 hembras: sobresalen 0.1 de la cara (D-49)."""
    w, zr, hh = 4 * 2.54 / 2, P.CAP_ROW_ZC, P.DUP_W / 2
    return box_between((-w, ly(P.DUP_F_SLOT_DEPTH - P.DUP_F_L), zr - hh),
                       (w, ly(P.DUP_F_SLOT_DEPTH), zr + hh))


def cat6_envelope():
    zc = cat6_zc()
    y0 = Y1 - P.CON_SAD_L - 4.0
    return cq.Workplane(obj=cq.Solid.makeCylinder(
        P.CAT6_D / 2, Y1 + 15.0 - y0, cq.Vector(0, y0, zc), cq.Vector(0, 1, 0)))


def build_assembly():
    a = capsule_assembly()
    blue, light, orange = cq.Color(0.42, 0.65, 0.87), cq.Color(0.66, 0.8, 0.95), cq.Color(1.0, 0.55, 0.1)
    a.add(build_body(), name="conector_cuerpo", color=blue)
    a.add(build_lid(), name="conector_tapa", color=light)
    a.add(female_envelope(), name="dupont_hembras", color=orange)
    a.add(cat6_envelope(), name="cat6", color=cq.Color(0.5, 0.55, 0.55))
    return a


if __name__ == "__main__":
    print(export_versioned(build_body_print(), "conector_cuerpo", OUTPUT))
    print(export_versioned(build_lid_print(), "conector_tapa", OUTPUT))
    print(export_assembly_versioned(build_assembly(), "conector_ensamble", OUTPUT))
