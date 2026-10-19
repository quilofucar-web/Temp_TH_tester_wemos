"""Alojamiento del boton tactil 12 x 12 en la cara interior del frente, con
3 formas de sujetarlo (parametro BTN_MOUNT; la prueba fisica de 2026-10-14
eligio "clip": en "presion" y "ambos" el boton no entro):

  - "clip":    pared perimetral + 2 brazos flexibles (lados +-X) con una ceja
               de rampa a 45 grados que abraza la base del cuerpo: tope real
               contra el empuje.
  - "presion": 4 aletas delgadas sin pared detras, PRESS_INTERF mas adentro
               que el cuerpo: lo sujetan por friccion al flexionar.
  - "ambos":   aletas en +-Z y brazos con ceja en +-X.

Ejes LOCALES: la cara interior del frente es y = 0 (el frente crece hacia +y),
el cuerpo del boton ocupa y en [-BTN_BODY_H, 0], centrado en x = z = 0.
Las patas del boton van hacia +-Z (lados sin brazos); la pared y las aletas
terminan BTN_LEG_FREE antes de la base para no tapar su salida.
"""
import cadquery as cq

import parameters as P
from geom import box_between

VARIANTS = ("clip", "presion", "ambos")


def _ring():
    pin = P.BTN_BODY / 2 + P.BTN_CLEAR
    pout = pin + P.BTN_POCKET_WALL
    y0 = -(P.BTN_BODY_H - P.BTN_LEG_FREE)
    return (box_between((-pout, y0, -pout), (pout, 0.0, pout))
            .cut(box_between((-pin, y0 - 1.0, -pin), (pin, 1.0, pin))))


def _clip_arms(ring=None, lip=P.CLIP_LIP, t=P.CLIP_T):
    """2 brazos con ceja en +-X; si hay pared, le abre una ranura a cada brazo.
    La ceja es un triangulo: cara plana que retiene (mira al frente) y rampa a
    45 grados hacia atras para que el cuerpo entre empujando. lip = cuanto
    entra la ceja sobre el cuerpo; t = espesor del brazo."""
    pin = P.BTN_BODY / 2 + P.BTN_CLEAR
    pout = pin + P.BTN_POCKET_WALL
    xi = P.BTN_BODY / 2 - lip                      # cara interior de la ceja
    y_lip = -(P.BTN_BODY_H + P.CLIP_GAP)
    y_end = y_lip - (pin - xi)                      # rampa a 45 grados
    hw = P.CLIP_W / 2
    out = ring
    for sx in (-1, 1):
        if out is not None:
            gap = hw + P.CLIP_SLOT
            out = out.cut(box_between((sx * (pin - 0.01), -P.BTN_BODY_H - 1.0, -gap),
                                      (sx * (pout + 0.01), 1.0, gap)))
        arm = box_between((sx * pin, y_end, -hw), (sx * (pin + t), 0.0, hw))
        lip = (cq.Workplane("XY", origin=(0, 0, -hw))
               .polyline([(sx * pin, y_lip), (sx * xi, y_lip), (sx * pin, y_end)])
               .close().extrude(2 * hw))
        arm = arm.union(lip)
        out = arm if out is None else out.union(arm)
    return out


def _press_fins(sides=("x", "z")):
    """Aletas a presion: cara interior PRESS_INTERF adentro del cuerpo."""
    a = P.BTN_BODY / 2 - P.PRESS_INTERF
    b = a + P.PRESS_FIN_T
    hl = P.PRESS_FIN_L / 2
    y0 = -(P.BTN_BODY_H - P.BTN_LEG_FREE)
    out = None
    for side in sides:
        for s in (-1, 1):
            if side == "x":
                fin = box_between((s * a, y0, -hl), (s * b, 0.0, hl))
            else:
                fin = box_between((-hl, y0, s * a), (hl, 0.0, s * b))
            out = fin if out is None else out.union(fin)
    return out


def mount(variant, lip=P.CLIP_LIP, t=P.CLIP_T):
    """(solido a sumar, solido a restar) del alojamiento, en ejes locales.
    Lo que se resta es la ventana de la tapa verde a traves del frente.
    lip y t ajustan la ceja y el brazo del clip (prueba_boton)."""
    if variant == "clip":
        add = _clip_arms(_ring(), lip, t)
    elif variant == "presion":
        add = _press_fins(("x", "z"))
    elif variant == "ambos":
        add = _clip_arms(_press_fins(("z",)))
    else:
        raise ValueError(f"BTN_MOUNT desconocido: {variant}")
    cw = P.BTN_CAP / 2 + P.BTN_CAP_CLEAR
    cut = box_between((-cw, -1.0, -cw), (cw, P.FRONT_T + 1.0, cw))
    return add, cut
