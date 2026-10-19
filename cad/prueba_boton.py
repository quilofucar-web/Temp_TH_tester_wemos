"""Pieza de prueba del boton: un trozo de frente (FRONT_T) con 3 variantes
del clip lado a lado (PRUEBA_CLIP_VARIANTS: ceja y espesor del brazo). Cada
variante lleva grabados 1, 2 o 3 puntos en la cara interior (regla de marcas
de ~/.claude/extras.md). Con el resultado se fijan CLIP_LIP y CLIP_T.

Se imprime boca abajo, igual que la caja delantera.

Uso:  cd cad && python3 prueba_boton.py
"""
from pathlib import Path

import boton
import parameters as P
from cq_utils import export_versioned
from geom import box_between, cyl_y

OUTPUT = Path(__file__).resolve().parent.parent / "output"


def variant_x(i):
    """Centro en X de la variante i (0, 1, 2)."""
    return (i - (len(P.PRUEBA_CLIP_VARIANTS) - 1) / 2) * P.PRUEBA_BOTON_PITCH


def build_local():
    """Ejes locales de boton.py: cara interior del frente en y = 0."""
    hw = len(P.PRUEBA_CLIP_VARIANTS) * P.PRUEBA_BOTON_PITCH / 2
    hh = P.PRUEBA_BOTON_H / 2
    plate = (box_between((-hw, 0.0, -hh), (hw, P.FRONT_T, hh))
             .faces(">Y").edges().chamfer(P.BED_CHAMFER))   # aristas sobre la cama
    for i, (lip, t) in enumerate(P.PRUEBA_CLIP_VARIANTS):
        add, cut = boton.mount("clip", lip, t)
        at = (variant_x(i), 0.0, 0.0)
        plate = plate.union(add.translate(at)).cut(cut.translate(at))
        z_mark = -hh + P.MARK_PITCH + P.MARK_D / 2
        for k in range(i + 1):
            x = variant_x(i) + (k - i / 2) * P.MARK_PITCH
            plate = plate.cut(cyl_y(x, z_mark, P.MARK_D, -1.0, P.MARK_DEPTH))
    return plate


def build_print():
    """Cara frontal (y = FRONT_T) sobre la cama."""
    return (build_local().rotate((0, 0, 0), (1, 0, 0), -90)
            .translate((0, 0, P.FRONT_T)))


if __name__ == "__main__":
    stl, step = export_versioned(build_print(), "prueba_boton", OUTPUT)
    print("Exportado:", stl, step)
