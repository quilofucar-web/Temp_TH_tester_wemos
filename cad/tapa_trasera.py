"""Tapa trasera (pieza 1), version final: placa de OUT_W x OUT_H con los 2
conectores HSW a ras del borde SUPERIOR (resultado de la prueba de la fase 1)
y 4 barrenos avellanados para los tornillos M3x8 de cabeza conica que la unen a la caja trasera (juego B,
D-19; las cabezas quedan en el hueco de 5.4 mm contra el panel).

Se imprime DE PIE con el borde superior (el de los conectores) sobre la cama:
build_print() la deja asi; build_global() la coloca en el ensamble.

Uso:  cd cad && python3 tapa_trasera.py
"""
from pathlib import Path

import cadquery as cq

import parameters as P
from cq_utils import export_versioned
from geom import cone_y, cyl_y
from hsw_connector import connector_placed

OUTPUT = Path(__file__).resolve().parent.parent / "output"


def build_print():
    """Orientacion de impresion: Z = 0 es el borde superior de la carcasa."""
    plate = (cq.Workplane("XY")
             .box(P.OUT_W, P.TAPA_T, P.OUT_H, centered=(True, False, False))
             .faces("<Z").edges().chamfer(P.BED_CHAMFER))   # aristas sobre la cama
    for xc in (-P.CONN_SPACING / 2, P.CONN_SPACING / 2):
        plate = plate.union(connector_placed(xc, z_bottom=0.0))
    for sx in (-1, 1):
        for z in P.B_BOSS_Z:
            x, zp = sx * P.BOSS_X, P.OUT_H - z
            plate = plate.cut(cyl_y(x, zp, P.M3_CLEAR_D, -1.0, P.TAPA_T + 1.0))
            # avellanado a 90 grados en la cara Y = 0 (hacia el panel), para
            # que la cabeza conica quede bajo la cara
            d = P.M3_CSK_D + 2 * P.M3_CSK_CLEAR
            plate = plate.cut(cone_y(x, zp, d + 2.0, -1.0, P.M3_CLEAR_D,
                                     (d - P.M3_CLEAR_D) / 2))
    return plate


def to_global(solid):
    """Impresion -> ensamble: giro de 180 grados en Y; el borde de los
    conectores queda arriba (Z = OUT_H)."""
    return solid.rotate((0, 0, 0), (0, 1, 0), 180).translate((0, 0, P.OUT_H))


def build_global():
    return to_global(build_print())


if __name__ == "__main__":
    stl, step = export_versioned(build_print(), "tapa_trasera", OUTPUT)
    print("Exportado:", stl, step)
