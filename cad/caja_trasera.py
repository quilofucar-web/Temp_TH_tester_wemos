"""Caja trasera (pieza 2, D-18): aloja la placa de 50 x 50 con el Wemos. Su
fondo es la pared divisoria que la separa de la caja delantera (el calor del
Wemos no llega al BME). Abierta hacia la tapa trasera.

Contenido (el alivio de tension del USB y la salida del CAT6 van en la fase
de detalles):
  - 4 postes con inserto M2.5 para la placa (cara de soldadura hacia la divisoria).
  - 4 columnas laterales con inserto M3 para la tapa trasera (juego B, D-19).
  - 4 barrenos en la divisoria para los M3x8 que sujetan la caja delantera
    (juego A, D-19; se atornillan desde aqui, con la caja abierta).
  - Paso de cables en la divisoria (boton y BME), a la izquierda de la placa.
  - Ventana en la divisoria para el Dupont del LCD (pines doblados hacia atras).
  - Ventana del cable micro-USB en la pared inferior.
  - Muesca del CAT6 en la pared superior, al centro, abierta hacia la tapa
    trasera: el cable se acuesta en ella ya con su conector y la tapa la
    cierra. Alivio de tension: un cincho apretado al cable por dentro.
  - Rejilla hexagonal en las paredes inferior (entrada) y superior (salida):
    chimenea para el calor del Wemos.

Se imprime acostada sobre la divisoria (cara Y = Y_DIV1 sobre la cama).

Uso:  cd cad && python3 caja_trasera.py
"""
import math
from pathlib import Path

import cadquery as cq

import parameters as P
from components import lcd_cable_box, pcb_holes_xz, usb_center
from cq_utils import export_versioned
from geom import box_between, cyl_y, hex_grid_points, hex_prisms

OUTPUT = Path(__file__).resolve().parent.parent / "output"


VENT_X = P.BOSS_X - P.BOSS_D / 2 - P.VENT_EDGE      # rejillas: |X| <= VENT_X


def _vents():
    """Prismas a restar en las paredes inferior y superior. Las puntas de los
    hexagonos van a lo largo de Y, la vertical de impresion. En la pared
    inferior se saltan los hexagonos que tocarian la ventana del USB y en la
    superior los que tocarian la muesca del CAT6."""
    y0, y1 = P.Y_REAR0 + P.VENT_RIM, P.Y_DIV0 - P.VENT_EDGE
    pts = hex_grid_points(y0, y1, -VENT_X, VENT_X, P.HEX_F2F, P.HEX_RIB)
    x_usb, _, _ = usb_center()
    keep_out = P.USB_PLUG_W / 2 + P.USB_WIN_CLEAR + P.VENT_EDGE + P.HEX_F2F / math.sqrt(3)
    # en el plano XY con eje a = +Y, la coordenada b es -X
    bottom_pts = [(a, b) for a, b in pts if abs(-b - x_usb) > keep_out]
    bottom = hex_prisms((0.0, 0.0, P.WALL_T / 2), (0, 1, 0), (0, 0, 1),
                        bottom_pts, P.HEX_F2F, P.WALL_T + 2.0)
    keep_cat6 = P.CAT6_D / 2 + P.CAT6_CLEAR + P.VENT_EDGE + P.HEX_F2F / math.sqrt(3)
    top_pts = [(a, b) for a, b in pts if abs(-b - P.CAT6_X) > keep_cat6]
    top = hex_prisms((0.0, 0.0, P.OUT_H - P.WALL_T / 2), (0, 1, 0), (0, 0, 1),
                     top_pts, P.HEX_F2F, P.WALL_T + 2.0)
    return bottom.union(top)


def build_global():
    hw, ihw = P.OUT_W / 2, P.IN_W / 2
    body = (box_between((-hw, P.Y_REAR0, 0.0), (hw, P.Y_DIV1, P.OUT_H))
            .faces(">Y").edges().chamfer(P.BED_CHAMFER))     # aristas sobre la cama
    body = body.cut(box_between((-ihw, P.Y_REAR0 - 1.0, P.Z_IN0),
                                (ihw, P.Y_DIV0, P.Z_IN1)))
    # Columnas del juego B (tapa trasera -> caja trasera), pegadas a las paredes
    for sx in (-1, 1):
        for z in P.B_BOSS_Z:
            x = sx * P.BOSS_X
            col = (cyl_y(x, z, P.BOSS_D, P.Y_REAR0, P.Y_DIV0)
                   .union(box_between((x, P.Y_REAR0, z - P.BOSS_D / 2),
                                      (sx * ihw, P.Y_DIV0, z + P.BOSS_D / 2))))
            body = body.union(col).cut(
                cyl_y(x, z, P.INS_M3_HOLE_D, P.Y_REAR0 - 1.0, P.Y_REAR0 + P.B_INSERT_DEPTH))
    # Postes de la placa
    for x, z in pcb_holes_xz():
        body = body.union(cyl_y(x, z, P.PCB_POST_D, P.PCB_Y_SOLDER, P.Y_DIV0)).cut(
            cyl_y(x, z, P.INS_M25_HOLE_D, P.PCB_Y_SOLDER - 1.0,
                  P.PCB_Y_SOLDER + P.M25_INSERT_DEPTH))
    # Barrenos del juego A en la divisoria
    for sx in (-1, 1):
        for z in P.A_BOSS_Z:
            body = body.cut(cyl_y(sx * P.BOSS_X, z, P.M3_CLEAR_D,
                                  P.Y_DIV0 - 1.0, P.Y_DIV1 + 1.0))
    # Paso de cables
    sw, sh = P.DIV_SLOT_W / 2, P.DIV_SLOT_H / 2
    body = body.cut(box_between((P.DIV_SLOT_X - sw, P.Y_DIV0 - 1.0, P.DIV_SLOT_ZC - sh),
                                (P.DIV_SLOT_X + sw, P.Y_DIV1 + 1.0, P.DIV_SLOT_ZC + sh)))
    # Ventana del Dupont del LCD (pines doblados hacia atras)
    x0, x1, z0, z1 = lcd_cable_box()
    c = P.DIV_LCD_WIN_CLEAR
    body = body.cut(box_between((x0 - c, P.Y_DIV0 - 1.0, z0 - c),
                                (x1 + c, P.Y_DIV1 + 1.0, z1 + c)))
    # Ventana del cable micro-USB en la pared inferior
    x, y, _ = usb_center()
    ww = P.USB_PLUG_W / 2 + P.USB_WIN_CLEAR
    wh = P.USB_PLUG_H / 2 + P.USB_WIN_CLEAR
    body = body.cut(box_between((x - ww, y - wh, -1.0), (x + ww, y + wh, P.Z_IN0 + 1.0)))
    # Muesca del CAT6 (fondo redondo, abierta hacia la tapa trasera)
    r = P.CAT6_D / 2 + P.CAT6_CLEAR
    yc = P.Y_REAR0 + r
    body = body.cut(box_between((P.CAT6_X - r, P.Y_REAR0 - 1.0, P.Z_IN1 - 1.0),
                                (P.CAT6_X + r, yc, P.OUT_H + 1.0)))
    body = body.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
        r, P.OUT_H - P.Z_IN1 + 2.0, cq.Vector(P.CAT6_X, yc, P.Z_IN1 - 1.0))))
    return body.cut(_vents())


def to_print(solid):
    """Ensamble -> impresion: la divisoria (cara Y = Y_DIV1) sobre la cama."""
    return solid.rotate((0, 0, 0), (1, 0, 0), -90).translate((0, 0, P.Y_DIV1))


def build_print():
    return to_print(build_global())


if __name__ == "__main__":
    stl, step = export_versioned(build_print(), "caja_trasera", OUTPUT)
    print("Exportado:", stl, step)
