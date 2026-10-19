"""Conector HSW de resorte: reinterpretacion parametrica de
externalfiles/hexagonconector3dprint.stl (conector probado por Carlos).

Autoria: el conector original es de autor desconocido (la pieza trae unas
letras, al parecer "XYZ", en la cara trasera). Este modulo solo lo
reinterpreta en CadQuery; todos los derechos del diseno original son de su
autor. El STL original no se incluye en el repositorio publico.

Geometria (ejes locales, ver parameters.py):
  - 2 brazos (|Y| entre CONN_ARM_IN y CONN_ARM_OUT) de la punta a la base,
    unidos solo en la base por un puente -> las mitades flexionan (resorte).
  - Placa B: asienta en la boca de 22 del panel.
  - Placa A (punta): pasa el hexagono de 20 flexionando los brazos y se
    engancha detras del panel con su rampa trasera.
  - La cara de la base queda a CONN_STANDOFF (6.4 mm) de la cara del panel.
  - Pestana de primera capa (0.5 mm) por dentro de cada brazo: da
    adherencia a los brazos altos y delgados sin necesidad de brim.
Se imprime de pie (Z local = Z impresora), con la cara Z = -CONN_HALF_H
sobre la cama.
"""
import math

import cadquery as cq

import parameters as P

SQ3 = math.sqrt(3)


def _hex_frustum(x0, x1, r0, r1):
    """Tronco hexagonal a lo largo de +X, de radio circunscrito r0 (en x0) a
    r1 (en x1), con las puntas sobre +-Y. Solo primitivas (extrude con
    taper), nada de loft (CLAUDE.md, convenciones)."""
    length = x1 - x0
    offset = (r0 - r1) * SQ3 / 2          # desplazamiento normal de las caras
    taper = math.degrees(math.atan2(offset, length))
    return (cq.Workplane("YZ", origin=(x0, 0, 0))
            .polygon(6, 2 * r0)
            .extrude(length, taper=taper))


def _clip(solid, ytrunc, ymin):
    """Recorta a |Y| <= ytrunc y |Z| <= CONN_HALF_H, y quita la ranura
    central |Y| < ymin (separa las dos mitades)."""
    keep = cq.Workplane("XY").box(40, 2 * ytrunc, 2 * P.CONN_HALF_H)
    slot = cq.Workplane("XY").box(40, 2 * ymin, 4 * P.CONN_HALF_H)
    return solid.intersect(keep).cut(slot)


def connector_local():
    """Conector en sus ejes locales (punta en -X, base en +X)."""
    h2 = 2 * P.CONN_HALF_H
    arm = (cq.Workplane("XY")
           .center((P.CONN_X_TIP + P.CONN_X_BASE) / 2,
                   (P.CONN_ARM_IN + P.CONN_ARM_OUT) / 2)
           .box(P.CONN_X_BASE - P.CONN_X_TIP, P.CONN_ARM_OUT - P.CONN_ARM_IN, h2))
    arms = arm.union(arm.mirror("XZ"))
    bridge = (cq.Workplane("XY")
              .center(P.CONN_X_BASE - P.CONN_BRIDGE_T / 2, 0)
              .box(P.CONN_BRIDGE_T, 2 * P.CONN_ARM_OUT, h2))

    prof = P.CONN_A_PROFILE
    plate_a = _hex_frustum(prof[0][0], prof[1][0], prof[0][1], prof[1][1])
    for (xa, ra), (xb, rb) in zip(prof[1:-1], prof[2:]):
        plate_a = plate_a.union(_hex_frustum(xa, xb, ra, rb))
    plate_a = _clip(plate_a, P.CONN_A_YTRUNC, P.CONN_ARM_IN)

    plate_b = _clip(_hex_frustum(P.CONN_B_X0, P.CONN_B_X1, P.CONN_B_R, P.CONN_B_R),
                    P.CONN_B_YTRUNC, P.CONN_ARM_OUT)
    return (arms.union(bridge).union(plate_a).union(plate_b)
            .union(_first_layer_foot()))


def _first_layer_foot():
    """Pestanas de 0.5 mm en la primera capa, por dentro de ambos brazos,
    con redondeo concavo hacia la cara interior del brazo."""
    z0 = -P.CONN_HALF_H
    z_top = z0 + P.CONN_FOOT_H
    r = P.CONN_FOOT_FILLET_R
    foot = (cq.Workplane("XY", origin=(0, 0, z0))
            .polyline(P.CONN_FOOT_PROFILE).close()
            .extrude(P.CONN_FOOT_H))
    # Redondeo: bloque r x r en la esquina, menos un cilindro a lo largo de X,
    # recortado al contorno de la pestana (se desvanece con la rampa final).
    x0, x1 = P.CONN_X_TIP, P.CONN_B_X1
    corner = (cq.Workplane("XY")
              .box(x1 - x0, r, r, centered=False)
              .translate((x0, P.CONN_ARM_IN - r, z_top)))
    arc = (cq.Workplane("YZ", origin=(x0, P.CONN_ARM_IN - r, z_top + r))
           .circle(r).extrude(x1 - x0))
    outline = (cq.Workplane("XY", origin=(0, 0, z0))
               .polyline(P.CONN_FOOT_PROFILE).close()
               .extrude(P.CONN_FOOT_H + r))
    fillet = corner.cut(arc).intersect(outline)
    half = foot.union(fillet)
    return half.union(half.mirror("XZ"))


def connector_placed(x_center, z_bottom=0.0):
    """Conector en coordenadas globales de la carcasa: punta hacia -Y (la
    pared), centro en X = x_center, cara inferior en Z = z_bottom (a ras de
    la cama). El puente de la base queda embebido CONN_EMBED dentro de la
    pieza: la cara de la base cae en Y = +CONN_EMBED y la cara trasera de la
    pieza (Y = 0) queda a TAPA_STANDOFF del panel.
    Rotacion de +90 grados en Z: X local -> +Y global, Y local -> -X global."""
    return (connector_local()
            .rotate((0, 0, 0), (0, 0, 1), 90)
            .translate((x_center, P.CONN_EMBED - P.CONN_X_BASE,
                        z_bottom + P.CONN_HALF_H)))
