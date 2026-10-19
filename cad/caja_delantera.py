"""Caja delantera (pieza 3, D-18): frente + paredes. Aloja el LCD, el boton y
el BME de ambiente (en la fila del boton, lejos del calor del Wemos, que queda
tras la pared divisoria). Abierta hacia la caja trasera.

Contenido:
  - Ventana del marco del LCD: el marco pasa por el frente y queda a ras de
    la cara frontal (opcion B, 2026-10-14). 4 postes en cono con inserto M2.5
    desde la cara interior del frente hasta la placa del LCD, recortados
    contra el marco.
  - Alojamiento del boton con la sujecion elegida (BTN_MOUNT, boton.py).
  - BME: 2 escalones con pin que entran en sus barrenos (sin tornillo; la
    punta del pin se remacha con el cautin si hace falta).
  - Rejilla hexagonal en la zona del frente bajo la ventana del LCD (el BME
    queda detras, a la izquierda del boton), con hexagonos extra a los lados,
    arriba de la pantalla y arriba del boton; tambien en la pared inferior
    (entrada de aire) y en la superior (salida del calor del LCD).
  - 4 columnas cortas de esquina con inserto M3 (juego A, D-19), medio
    embebidas en las paredes laterales.

Se imprime boca abajo (cara frontal Y = Y_FRONT sobre la cama).

Uso:  cd cad && python3 caja_delantera.py
"""
import math
from pathlib import Path

import cadquery as cq

import boton
import parameters as P
from components import bme_holes_xz, lcd_holes_xz
from cq_utils import export_versioned
from geom import box_between, cone_y, cyl_y, hex_grid_points, hex_prisms

OUTPUT = Path(__file__).resolve().parent.parent / "output"

VENT_X = P.BOSS_X - P.BOSS_D / 2 - P.VENT_EDGE      # rejillas: |X| <= VENT_X (libra columnas)


def front_vent_points():
    """(z, x) de los hexagonos del frente, simetricos en X:
      - zona baja, bajo la ventana del LCD; se saltan los que caerian bajo el
        alojamiento del boton, los escalones del BME o la base de los postes
        del LCD (se imprimirian en puente); los de esos 2 ultimos tambien en
        espejo;
      - una columna en zigzag a cada lado de la pantalla (misma reticula),
        entre los postes del LCD;
      - una fila centrada arriba de la pantalla y otra corta arriba del boton."""
    r_hex = P.HEX_F2F / math.sqrt(3)
    s = P.HEX_F2F + P.HEX_RIB
    da = s * math.sqrt(3) / 2
    edge = P.VENT_EDGE + r_hex
    btn_half = P.BTN_BODY / 2 + P.BTN_CLEAR + P.BTN_POCKET_WALL
    btn = btn_half + edge
    posts = [(abs(x), z, P.LCD_POST_BASE_D / 2) for x, z in lcd_holes_xz()]
    circles = [(abs(x), z, P.BME_STANDOFF_D / 2) for x, z in bme_holes_xz()] + posts

    def clear_of(z, x, circs):
        return all(math.hypot(x - cx, z - cz) > r + edge for cx, cz, r in circs)

    right = [(z, x) for z, x in hex_grid_points(P.FRONT_VENT_Z0, P.FRONT_VENT_Z1, 0.0,
                                                P.FRONT_VENT_X, P.HEX_F2F, P.HEX_RIB)
             if not (abs(x - P.BTN_XC) < btn and abs(z - P.BTN_ZC) < btn)
             and clear_of(z, x, circles)]
    # columna a los lados de la pantalla, arriba de la zona baja
    x_even = P.HEX_F2F / 2 + P.SIDE_VENT_N * s
    x_odd = x_even - s / 2
    k, z = 0, P.FRONT_VENT_Z0 + r_hex
    while z <= P.OUT_H - P.FRONT_VENT_MARGIN - r_hex + 1e-9:
        x = x_even if k % 2 == 0 else x_odd
        if z - r_hex > P.FRONT_VENT_Z1 - 0.5 and clear_of(z, x, posts):
            right.append((z, x))
        z += da
        k += 1
    # fila arriba de la pantalla, centrada en la franja libre
    win_top = P.BEZEL_ZC + P.LCD_BEZEL_H / 2 + P.LCD_WIN_CLEAR
    z_top = (win_top + P.OUT_H) / 2
    # fila corta justo arriba del alojamiento del boton
    z_btn = P.BTN_ZC + btn_half + edge
    centered = ([(z_top, (i - (P.TOP_VENT_N - 1) / 2) * s) for i in range(P.TOP_VENT_N)]
                + [(z_btn, P.BTN_XC + (i - (P.BTN_VENT_N - 1) / 2) * s)
                   for i in range(P.BTN_VENT_N)])
    return (right + [(z, -x) for z, x in right]
            + [(z, x) for z, x in centered if x >= 0]
            + [(z, -x) for z, x in centered if x > 0])


def _vents():
    """Prismas a restar: zona baja del frente + paredes inferior y superior.
    En las paredes las puntas de los hexagonos van a lo largo de Y, que es la
    vertical de impresion (sin voladizos)."""
    # plano XZ con eje a = +Z: la coordenada b = normal x a = Y x Z = +X
    front = hex_prisms((0.0, P.Y_FRONT - P.FRONT_T / 2, 0.0), (0, 0, 1), (0, 1, 0),
                       front_vent_points(), P.HEX_F2F, P.FRONT_T + 2.0)
    y0, y1 = P.Y_DIV1 + P.VENT_RIM, P.Y_FRONT_IN - P.VENT_EDGE
    pts = hex_grid_points(y0, y1, -VENT_X, VENT_X, P.HEX_F2F, P.HEX_RIB)
    walls = None
    for zc in (P.WALL_T / 2, P.OUT_H - P.WALL_T / 2):
        # plano XY: eje a = +Y, eje b = normal x a = Z x Y = -X (simetrico en X)
        w = hex_prisms((0.0, 0.0, zc), (0, 1, 0), (0, 0, 1), pts, P.HEX_F2F, P.WALL_T + 2.0)
        walls = w if walls is None else walls.union(w)
    return front.union(walls)


def _a_column(sx, z, wall_z):
    """Columna corta del juego A en una esquina, medio embebida en la pared
    lateral y tocando piso o techo. Solo mide lo que pide el inserto desde la
    divisoria; su cara hacia el frente baja a 45 grados hasta la pared lateral
    (se imprime boca abajo: sin voladizo y sin tocar la rejilla del frente)."""
    ihw = P.IN_W / 2
    x = sx * P.BOSS_X
    p = P.BOSS_SIDE_INSET + P.BOSS_D / 2           # lo que sobresale de la pared
    y_c = P.Y_DIV1 + P.A_INSERT_DEPTH + P.A_COL_CAP
    col = (cyl_y(x, z, P.BOSS_D, P.Y_DIV1, y_c + p)
           .union(box_between((x, P.Y_DIV1, z - P.BOSS_D / 2),
                              (sx * ihw, y_c + p, z + P.BOSS_D / 2)))
           .union(box_between((x - P.BOSS_D / 2, P.Y_DIV1, z),
                              (x + P.BOSS_D / 2, y_c + p, wall_z))))
    # cuna: Y <= y_c + (p - distancia a la pared lateral)
    wedge = (cq.Workplane("XY", origin=(0, 0, P.Z_IN0 - 1.0))
             .polyline([(sx * (ihw + 1.0), P.Y_DIV1 - 1.0),
                        (sx * (ihw - p - 1.0), P.Y_DIV1 - 1.0),
                        (sx * (ihw - p - 1.0), y_c - 1.0),
                        (sx * ihw, y_c + p),
                        (sx * (ihw + 1.0), y_c + p)])
             .close().extrude(P.IN_H + 2.0))
    return col.intersect(wedge)


def build_global():
    hw, ihw = P.OUT_W / 2, P.IN_W / 2
    body = (box_between((-hw, P.Y_DIV1, 0.0), (hw, P.Y_FRONT, P.OUT_H))
            .faces(">Y").edges().chamfer(P.BED_CHAMFER))     # aristas sobre la cama
    body = body.cut(box_between((-ihw, P.Y_DIV1 - 1.0, P.Z_IN0),
                                (ihw, P.Y_FRONT_IN, P.Z_IN1)))
    # Ventana del marco del LCD (antes de los postes: el corte no debe tocarlos)
    bw = P.LCD_BEZEL_W / 2 + P.LCD_WIN_CLEAR
    bh = P.LCD_BEZEL_H / 2 + P.LCD_WIN_CLEAR
    body = body.cut(box_between((P.BEZEL_XC - bw, P.Y_FRONT_IN - 0.01, P.BEZEL_ZC - bh),
                                (P.BEZEL_XC + bw, P.Y_FRONT + 1.0, P.BEZEL_ZC + bh)))
    body = body.cut(_vents())
    for sx in (-1, 1):
        for z, wall_z in zip(P.A_BOSS_Z, (P.Z_IN0, P.Z_IN1)):
            body = body.union(_a_column(sx, z, wall_z)).cut(
                cyl_y(sx * P.BOSS_X, z, P.INS_M3_HOLE_D,
                      P.Y_DIV1 - 1.0, P.Y_DIV1 + P.A_INSERT_DEPTH))
    # Postes del LCD: cono (mas material junto al frente) recortado contra el
    # marco del LCD, que solo estorba en la esquina hacia el centro
    pw = P.LCD_BEZEL_W / 2 + P.LCD_POST_BEZEL_CLEAR
    ph = P.LCD_BEZEL_H / 2 + P.LCD_POST_BEZEL_CLEAR
    bez = box_between((P.BEZEL_XC - pw, P.LCD_Y_PCB_FRONT - 1.0, P.BEZEL_ZC - ph),
                      (P.BEZEL_XC + pw, P.Y_FRONT, P.BEZEL_ZC + ph))
    for x, z in lcd_holes_xz():
        post = cone_y(x, z, P.LCD_POST_BASE_D, P.Y_FRONT_IN,
                      P.LCD_POST_D, P.LCD_Y_PCB_FRONT).cut(bez)
        body = body.union(post).cut(
            cyl_y(x, z, P.INS_M25_HOLE_D, P.LCD_Y_PCB_FRONT - 1.0,
                  P.LCD_Y_PCB_FRONT + P.LCD_INSERT_DEPTH))
    # BME: escalon (lo separa del frente) + pin que entra en cada barreno
    y_seat = P.Y_FRONT_IN - P.BME_FRONT_GAP
    for x, z in bme_holes_xz():
        body = body.union(cyl_y(x, z, P.BME_STANDOFF_D, y_seat, P.Y_FRONT_IN)).union(
            cyl_y(x, z, P.BME_HOLE_D - 2 * P.BME_PIN_CLEAR,
                  y_seat - P.BME_PCB_T - P.BME_PIN_OUT, y_seat))
    # Boton
    add, cut = boton.mount(P.BTN_MOUNT)
    at = (P.BTN_XC, P.Y_FRONT_IN, P.BTN_ZC)
    body = body.union(add.translate(at)).cut(cut.translate(at))
    return body


def to_print(solid):
    """Ensamble -> impresion: la cara frontal (Y = Y_FRONT) sobre la cama."""
    return solid.rotate((0, 0, 0), (1, 0, 0), -90).translate((0, 0, P.Y_FRONT))


def build_print():
    return to_print(build_global())


if __name__ == "__main__":
    stl, step = export_versioned(build_print(), "caja_delantera", OUTPUT)
    print("Exportado:", stl, step)
