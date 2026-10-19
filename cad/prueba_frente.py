"""Pieza de prueba del frente: recorte de la caja delantera con la ventana
del LCD, sus 4 postes con inserto M2.5, el alojamiento del boton y los
pines del BME. Sirve para
probar en fisico el LCD, los insertos y el boton antes de imprimir la caja
completa (especificacion, seccion 7).

Se imprime boca abajo, igual que la caja delantera.

Uso:  cd cad && python3 prueba_frente.py
"""
from pathlib import Path

import caja_delantera
import parameters as P
from cq_utils import export_versioned
from geom import box_between

OUTPUT = Path(__file__).resolve().parent.parent / "output"


def build_global():
    z0 = (P.BTN_ZC - P.BTN_BODY / 2 - P.BTN_CLEAR - P.BTN_POCKET_WALL
          - P.PRUEBA_FRENTE_MARGIN)
    if z0 < P.WALL_T:
        z0 = -1.0                         # la fila del boton llega al piso: pared completa
    y0 = P.LCD_Y_PCB_FRONT - P.PRUEBA_FRENTE_BACK
    slab = box_between((-P.OUT_W / 2 - 1.0, y0, z0),
                       (P.OUT_W / 2 + 1.0, P.Y_FRONT + 1.0, P.OUT_H + 1.0))
    return caja_delantera.build_global().intersect(slab)


def build_print():
    return caja_delantera.to_print(build_global())


if __name__ == "__main__":
    stl, step = export_versioned(build_print(), "prueba_frente", OUTPUT)
    print("Exportado:", stl, step)
