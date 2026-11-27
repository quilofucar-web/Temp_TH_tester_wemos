"""Capsula del INA219 (GY-219), checkpoint 1: cuerpo, tapa y posiciones.

Cuerpo: caja de esquinas R8 por fuera y R2 por dentro, orilla de la base en
gota r3.5, 2 ventanas simetricas al frente, bloque macizo atras (ahi iran el
bolsillo OpenLOCK, la fila Dupont y el pin en el checkpoint 2), postes del
modulo con inserto M2.5, costilla bajo su bornera, apoyo bajo el lado del
header, cuna hueca de la bornera GND con la entrada del cable a la derecha,
canal del cable GND junto a la pared derecha e insertos M3 de la tapa.

Tapa: placa con la orilla de arriba en gota r3.5, labio con entrada a 45
grados (sin tramo al frente), 2 lenguetas al frente, collar que fija la
bornera GND, 2 M3 avellanados atras y 2 ranuras ovaladas sobre los tornillos
de las borneras.

Coordenadas: ver parameters.py (seccion CAPSULA). El cuerpo se imprime sobre
su base; la tapa, boca abajo (build_lid_print).

Uso:  cd cad && python3 capsula.py
"""
from pathlib import Path

import cadquery as cq

import parameters as P
from cq_utils import export_assembly_versioned, export_versioned
from geom import box_between

OUTPUT = Path(__file__).resolve().parent.parent / "output"


# ---------------------------------------------------------------- primitivas
def rrect_prism(x0, y0, x1, y1, z0, z1, r):
    """Prisma de planta rectangular con esquinas verticales de radio r."""
    return (cq.Workplane("XY").workplane(offset=z0)
            .center((x0 + x1) / 2, (y0 + y1) / 2)
            .rect(x1 - x0, y1 - y0).extrude(z1 - z0).edges("|Z").fillet(r))


def gota(solid, side, z_edge, r=P.CAP_GOTA_R):
    """Orilla en gota (D-51) en la cara '<Z' o '>Z': arco r3.5 hasta el punto
    a 45 grados y de ahi recta a 45 grados hasta la cara. Se arma como
    redondeo U (chaflan 45 grados recortado a la franja junto a la cara)."""
    t = r * (1 - 0.5 ** 0.5)
    fil = solid.faces(side).edges().fillet(r)
    cham = solid.faces(side).edges().chamfer(2 * t)
    bb = solid.val().BoundingBox()
    z0, z1 = (z_edge, z_edge + t) if side == "<Z" else (z_edge - t, z_edge)
    slab = box_between((bb.xmin - 1, bb.ymin - 1, z0), (bb.xmax + 1, bb.ymax + 1, z1))
    return fil.union(cham.intersect(slab)).clean()


def cyl_z(x, y, d, z0, z1):
    return cq.Workplane(obj=cq.Solid.makeCylinder(
        d / 2, z1 - z0, cq.Vector(x, y, z0), cq.Vector(0, 0, 1)))


def _cavity(z0, z1, inset=0.0):
    return rrect_prism(-P.CAP_W / 2 + P.CAP_WALL + inset, P.CAP_WALL + inset,
                       P.CAP_W / 2 - P.CAP_WALL - inset, P.CAP_CAV_Y1 - inset,
                       z0, z1, P.CAP_IN_R - inset if P.CAP_IN_R - inset > 0.05 else 0.05)


def ina_holes():
    return [(P.INA_X0 + hx, P.INA_Y0 + P.INA_HOLE_Y) for hx in P.INA_HOLE_X]


def tb_screws():
    """(x, y) de los tornillos de las 2 borneras (para las ranuras de la tapa)."""
    ym = P.INA_Y0 + P.INA_TB_D / 2
    yg = P.GND_Y0 + P.BORNE2_D / 2
    return (P.INA_XC, ym), (P.GND_XC, yg)


# ---------------------------------------------------------------- cara del conector
def drop_xz(x, z, r, up=False, down=False):
    """Perfil en el plano XZ: circulo r con punta a 45 grados arriba y/o abajo."""
    s = cq.Sketch().push([(x, z)]).circle(r)
    for flag, sz in ((up, 1), (down, -1)):
        if flag:
            s = s.push([(x, z + sz * r / 2 ** 0.5)]).rect(r, r, angle=45, mode="a")
    return s.clean()


def prism_y(sketch, y0, length):
    """Extruye un perfil del plano XZ de y0 hacia +Y."""
    return cq.Workplane("XZ", origin=(0, y0, 0)).placeSketch(sketch).extrude(-length)


def hole_csk(x, z, y_face, sign):
    """Avellanado de 45 grados en la boca del hueco del pin (sign: hacia donde entra)."""
    r0 = P.CAP_HOLE_D / 2 + P.CAP_HOLE_CSK
    c = P.CAP_HOLE_CSK
    return cq.Workplane(obj=cq.Solid.makeCone(
        r0 + 0.5, P.CAP_HOLE_D / 2, c + 0.5, cq.Vector(x, y_face - sign * 0.5, z), cq.Vector(0, sign, 0)))


def openlock_pocket(y_face, z0, h):
    """Bolsillo OpenLOCK con la boca en y_face, hacia -Y (perfil del cupon)."""
    from cupon_openlock import openlock_pts
    pts = [(x, y_face - (y if y > 0 else -0.5)) for x, y in openlock_pts()]
    return cq.Workplane("XY", origin=(0, 0, z0)).polyline(pts).close().extrude(h)


def connector_face(b):
    """Cara de atras: bolsillo OpenLOCK de 4.2, ranura de los 4 machos al ras con
    su tope en la cavidad, pin en gota a -X y hueco a +X."""
    yf, zr = P.CAP_D, P.CAP_ROW_ZC
    b = b.cut(openlock_pocket(yf, P.CAP_POCK_Z0, P.CAP_POCK_H))
    # tope de los machos: placa contra la pared de atras de la cavidad, del piso
    # hasta arriba de la ranura, con el paso de los cables
    y1 = P.CAP_CAV_Y1
    zt = zr + P.CAP_ROW_H / 2 + P.CAP_ROW_STOP_T
    stop = box_between((-P.CAP_ROW_STOP_W / 2, y1 - P.CAP_ROW_STOP_T, P.CAP_FLOOR - 0.5),
                       (P.CAP_ROW_STOP_W / 2, y1 + 0.5, zt))
    b = b.union(stop)
    b = b.cut(box_between((-P.CAP_ROW_WIRE_W / 2, y1 - P.CAP_ROW_STOP_T - 1, zr - P.CAP_ROW_WIRE_H / 2),
                          (P.CAP_ROW_WIRE_W / 2, y1 + 1, zr + P.CAP_ROW_WIRE_H / 2)))
    b = b.cut(box_between((-P.CAP_ROW_W / 2, y1, zr - P.CAP_ROW_H / 2),
                          (P.CAP_ROW_W / 2, yf + 1, zr + P.CAP_ROW_H / 2)))
    # hueco del pin de la pieza del cable (+X)
    b = b.cut(prism_y(drop_xz(P.CAP_PIN_DX, zr, P.CAP_HOLE_D / 2, up=True, down=True),
                      yf - P.CAP_HOLE_DEPTH, P.CAP_HOLE_DEPTH + 1))
    b = b.cut(hole_csk(P.CAP_PIN_DX, zr, yf, -1))
    # pin (-X): gota con la punta abajo, punta con chaflan, base con redondeo
    pin = prism_y(drop_xz(-P.CAP_PIN_DX, zr, P.CAP_PIN_D / 2, down=True), yf - 0.5, P.CAP_PIN_L + 0.5)
    pin = pin.faces(">Y").edges().chamfer(P.CAP_PIN_TIP_C)
    b = b.union(pin)
    sel = cq.selectors.BoxSelector((-P.CAP_PIN_DX - 3, yf - 0.01, zr - 3), (-P.CAP_PIN_DX + 3, yf + 0.01, zr + 3))
    return b.edges(sel).fillet(P.CAP_PIN_ROOT_R)


# ---------------------------------------------------------------- cuerpo
def build_body():
    h = P.CAP_BODY_H
    b = rrect_prism(-P.CAP_W / 2, 0, P.CAP_W / 2, P.CAP_D, 0, h, P.CAP_R)
    b = gota(b, "<Z", 0.0)
    b = b.cut(_cavity(P.CAP_FLOOR, h + 1))
    # ventanas del frente, centradas en los huecos de cable de las borneras
    for xc in (P.INA_XC, P.GND_XC):
        win = (cq.Workplane("XZ").workplane(offset=1.0).center(xc, P.CAP_HOLE_ZC)   # normal -Y: plano en y = -1
               .rect(P.CAP_WIN_W, P.CAP_WIN_H).extrude(-(P.CAP_WALL + 2.0))
               .edges("|Y").fillet(P.CAP_WIN_R))
        b = b.cut(win)
    # postes del modulo con inserto M2.5
    z_top = P.INA_Z0
    for x, y in ina_holes():
        b = b.union(cyl_z(x, y, P.INA_POST_D, P.CAP_FLOOR - 0.5, z_top))
    # costilla bajo la bornera del modulo, con ranura para sus pines
    x0, x1 = P.INA_XC - P.INA_TB_L / 2, P.INA_XC + P.INA_TB_L / 2
    rib = box_between((x0, P.INA_Y0, P.CAP_FLOOR - 0.5), (x1, P.INA_Y0 + P.INA_TB_D, z_top))
    s0, s1 = P.INA_TB_PIN_SLOT
    rib = rib.cut(box_between((x0 - 1, P.INA_Y0 + s0, z_top - P.INA_TB_PIN - 0.5),
                              (x1 + 1, P.INA_Y0 + s1, z_top + 1)))
    b = b.union(rib)
    # apoyo bajo el lado del header
    ys = P.INA_Y0 + P.INA_MW - P.INA_SUP_Y
    b = b.union(box_between((P.INA_X0 + 3.0, ys - P.INA_SUP_W / 2, P.CAP_FLOOR - 0.5),
                            (P.INA_X0 + P.INA_ML - 3.0, ys + P.INA_SUP_W / 2, z_top)))
    # cuna de la bornera GND: U hueca hasta el piso (pines cortados, soldadura
    # del cable y puente), abierta a la derecha para que entre el cable GND
    gx0, gx1 = P.GND_XC - P.BORNE2_L / 2 - 0.5, P.GND_XC + P.BORNE2_L / 2 + 0.5
    gy1 = P.GND_Y0 + P.BORNE2_D
    cuna = box_between((gx0, P.GND_Y0, P.CAP_FLOOR - 0.5), (gx1, gy1, P.GND_Z0))
    w = P.CAP_CUNA_WALL
    cuna = cuna.cut(box_between((gx0 + w, P.GND_Y0 + w, P.CAP_FLOOR),
                                (gx1 + 1, gy1 - w, P.GND_Z0 + 1)))
    b = b.union(cuna)
    b = connector_face(b)
    # barrenos de los insertos (despues de las uniones)
    for x, y in ina_holes():
        b = b.cut(cyl_z(x, y, P.INS_M25_HOLE_D, z_top - P.INA_INS_DEPTH, z_top + 1))
    for sx in (-1, 1):
        b = b.cut(cyl_z(sx * P.CAP_SCREW_X, P.CAP_SCREW_Y, P.INS_M3_HOLE_D,
                        h - P.CAP_INS_M3_DEPTH, h + 1))
    return b


# ---------------------------------------------------------------- tapa
def gnd_collar():
    """Bloque casi solido de la tapa que fija la bornera GND: la rodea a la
    izq., atras y der. (a la derecha llega hasta el labio; al frente la detiene
    la pared de las ventanas) y la toca arriba a CAP_G_PRESS_CL. Solo le queda
    la ranura del desarmador. La cuna la sostiene por abajo."""
    z0 = P.CAP_BODY_H
    ztop = P.GND_Z0 + P.BORNE2_H
    cl, t = P.CAP_G_COLLAR_CL, P.CAP_G_COLLAR_T
    x0, x1 = P.GND_XC - P.BORNE2_L / 2 - cl, P.GND_XC + P.BORNE2_L / 2 + cl
    y0, y1 = P.CAP_WALL + P.CAP_LIP_CL, P.GND_Y0 + P.BORNE2_D + cl
    xr = P.CAP_W / 2 - P.CAP_WALL - P.CAP_LIP_CL
    c = box_between((x0 - t, y0, ztop - P.CAP_G_COLLAR_H), (xr, y1 + t, z0))
    c = c.intersect(_cavity(ztop - P.CAP_G_COLLAR_H - 1, z0, P.CAP_LIP_CL))
    return c.cut(box_between((x0, y0 - 1, ztop - P.CAP_G_COLLAR_H - 1), (x1, y1, ztop + P.CAP_G_PRESS_CL)))


def build_lid():
    z0, z1 = P.CAP_BODY_H, P.CAP_H
    lid = rrect_prism(-P.CAP_W / 2, 0, P.CAP_W / 2, P.CAP_D, z0, z1, P.CAP_R)
    # r3.5 = grueso de la tapa: OCC no redondea toda la cara; 3.45 deja 0.05 recto
    lid = gota(lid, ">Z", z1, min(P.CAP_GOTA_R, P.CAP_LID_T - 0.05))
    # labio: anillo dentro de la cavidad, entrada a 45 grados, sin tramo al frente
    ring = _cavity(z0 - P.CAP_LIP_H, z0, P.CAP_LIP_CL)
    ring = ring.faces("<Z").edges().chamfer(P.CAP_LIP_C)
    ring = ring.cut(_cavity(z0 - P.CAP_LIP_H - 1, z0 + 1, P.CAP_LIP_CL + P.CAP_LIP_W))
    ring = ring.cut(box_between((-P.CAP_W, -1, z0 - P.CAP_LIP_H - 1),
                                (P.CAP_W, P.CAP_WALL + P.CAP_LIP_CL + P.CAP_LIP_W + 0.01, z0 + 1)))
    lid = lid.union(ring)
    # lenguetas del frente, pegadas a la pared y libres de las 2 borneras
    xt = P.CAP_W / 2 - P.CAP_WALL - P.CAP_CL - P.CAP_TAB_W / 2 - 0.3
    y0 = P.CAP_WALL + P.CAP_CL
    keep = _cavity(z0 - P.CAP_TAB_H - 1, z0, P.CAP_CL)
    for sx in (-1, 1):
        tab = box_between((sx * xt - P.CAP_TAB_W / 2, y0, z0 - P.CAP_TAB_H),
                          (sx * xt + P.CAP_TAB_W / 2, y0 + P.CAP_TAB_T, z0))
        lid = lid.union(tab.intersect(keep))
    lid = lid.union(gnd_collar())
    # ranuras ovaladas sobre los tornillos de las borneras
    for x, y in tb_screws():
        lid = lid.cut(cq.Workplane("XY").workplane(offset=z0 - 1).center(x, y)
                      .slot2D(P.CAP_SLOT_L, P.CAP_SLOT_W).extrude(P.CAP_LID_T + 2))
    # M3 avellanados (cabeza conica, 90 grados) hacia arriba
    d = P.M3_CSK_D + 2 * P.M3_CSK_CLEAR
    for sx in (-1, 1):
        x, y = sx * P.CAP_SCREW_X, P.CAP_SCREW_Y
        lid = lid.cut(cyl_z(x, y, P.M3_CLEAR_D, z0 - 1, z1 + 1))
        hc = (d - P.M3_CLEAR_D) / 2
        lid = lid.cut(cq.Workplane(obj=cq.Solid.makeCone(
            P.M3_CLEAR_D / 2, d / 2 + 1.0, hc + 1.0, cq.Vector(x, y, z1 - hc), cq.Vector(0, 0, 1))))
    return lid


def build_lid_print():
    """Tapa boca abajo: la cara de arriba sobre la cama (Z = 0)."""
    return build_lid().rotate((0, 0, 0), (0, 1, 0), 180).translate((0, 0, P.CAP_H))


# ---------------------------------------------------------------- envolventes
def module_envelope():
    pcb = box_between((P.INA_X0, P.INA_Y0, P.INA_Z0),
                      (P.INA_X0 + P.INA_ML, P.INA_Y0 + P.INA_MW, P.INA_Z0 + P.INA_PCB_T))
    zt = P.INA_Z0 + P.INA_PCB_T
    tb = box_between((P.INA_XC - P.INA_TB_L / 2, P.INA_Y0, zt),
                     (P.INA_XC + P.INA_TB_L / 2, P.INA_Y0 + P.INA_TB_D, zt + P.INA_TB_H))
    return pcb, tb


def gnd_envelope():
    return box_between((P.GND_XC - P.BORNE2_L / 2, P.GND_Y0, P.GND_Z0),
                       (P.GND_XC + P.BORNE2_L / 2, P.GND_Y0 + P.BORNE2_D, P.GND_Z0 + P.BORNE2_H))


def dupont_envelope():
    """Los 4 machos: carcasas al ras de la cara y pines metalicos afuera."""
    w = 4 * 2.54 / 2
    zr, h = P.CAP_ROW_ZC, P.DUP_W / 2
    housing = box_between((-w, P.CAP_D - P.DUP_M_L, zr - h), (w, P.CAP_D, zr + h))
    pins = box_between((-w + 0.8, P.CAP_D, zr - 0.32), (w - 0.8, P.CAP_D + P.DUP_M_PIN, zr + 0.32))
    return housing, pins


def build_assembly():
    grey, orange = cq.Color(0.75, 0.75, 0.75), cq.Color(1.0, 0.55, 0.1)
    a = cq.Assembly(name="capsula")
    a.add(build_body(), name="cuerpo", color=grey)
    a.add(build_lid(), name="tapa", color=cq.Color(0.6, 0.75, 0.9))
    pcb, tb = module_envelope()
    a.add(pcb, name="gy219_placa", color=orange)
    a.add(tb, name="gy219_bornera", color=orange)
    a.add(gnd_envelope(), name="bornera_gnd", color=orange)
    housing, pins = dupont_envelope()
    a.add(housing, name="dupont_machos", color=orange)
    a.add(pins, name="dupont_pines", color=orange)
    return a


if __name__ == "__main__":
    print(export_versioned(build_body(), "capsula_cuerpo", OUTPUT))
    print(export_versioned(build_lid_print(), "capsula_tapa", OUTPUT))
    print(export_assembly_versioned(build_assembly(), "capsula_ensamble", OUTPUT))
