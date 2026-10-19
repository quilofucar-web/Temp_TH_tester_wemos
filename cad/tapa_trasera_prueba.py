"""Pieza de prueba de la tapa trasera (pieza 1): placa con los 2 conectores
HSW a CONN_SPACING, para probar ajuste y retencion en la pared real antes de
modelar la carcasa.

Se imprime DE PIE: la cara Z = 0 (donde los conectores quedan a ras) va sobre
la cama; sin soportes.

Uso:  cd cad && python3 tapa_trasera_prueba.py
"""
from pathlib import Path

import cadquery as cq

import parameters as P
from cq_utils import export_versioned
from hsw_connector import connector_placed

OUTPUT = Path(__file__).resolve().parent.parent / "output"


def build():
    plate = (cq.Workplane("XY")
             .box(P.TAPA_W, P.TAPA_T, P.TAPA_PRUEBA_H, centered=(True, False, False))
             .faces("<Z").edges().chamfer(P.BED_CHAMFER))   # aristas sobre la cama
    for xc in (-P.CONN_SPACING / 2, P.CONN_SPACING / 2):
        plate = plate.union(connector_placed(xc, z_bottom=0.0))
    return plate


if __name__ == "__main__":
    stl, step = export_versioned(build(), "tapa_trasera_prueba", OUTPUT)
    print("Exportado:", stl, step)
