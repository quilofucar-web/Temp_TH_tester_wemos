"""Ensamble de revision para Onshape: las 3 piezas en su posicion de uso
(coordenadas globales) mas las envolventes de los componentes. Solo STEP;
no se imprime.

Uso:  cd cad && python3 ensamble.py
"""
from pathlib import Path

import cadquery as cq

import caja_delantera
import caja_trasera
import tapa_trasera
from components import all_envelopes
from cq_utils import export_assembly_versioned

OUTPUT = Path(__file__).resolve().parent.parent / "output"

PIECE_COLOR = cq.Color(0.80, 0.80, 0.80, 1.0)
ENVELOPE_COLOR = cq.Color(0.95, 0.45, 0.10, 1.0)


def pieces():
    """{nombre: Workplane} de las 3 piezas en coordenadas globales."""
    return {
        "tapa_trasera": tapa_trasera.build_global(),
        "caja_trasera": caja_trasera.build_global(),
        "caja_delantera": caja_delantera.build_global(),
    }


def build_assembly():
    assy = cq.Assembly(name="medidor_thr")
    for name, solid in pieces().items():
        assy.add(solid, name=name, color=PIECE_COLOR)
    for name, solid in all_envelopes().items():
        assy.add(solid, name=f"env_{name}", color=ENVELOPE_COLOR)
    return assy


if __name__ == "__main__":
    print("Exportado:", export_assembly_versioned(build_assembly(), "ensamble", OUTPUT))
