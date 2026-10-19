"""Utilidades compartidas entre los scripts de CadQuery del proyecto.

Patron tomado de c:\\marco-rompecabezas\\cad\\cq_utils.py.
"""
import re
from pathlib import Path

import cadquery as cq


def check_valid(solid, name):
    """Verifica isValid() antes de exportar: un chaflan o fillet mal
    dimensionado puede generar un solido invalido que igual exporta a STL
    sin error."""
    if not solid.val().isValid():
        raise RuntimeError(f"Solido invalido: {name} (revisar antes de exportar)")
    return solid


def next_version_number(sample_path):
    """Siguiente numero consecutivo para el sufijo de export, revisando los
    archivos existentes con el mismo nombre base en el mismo directorio
    (CLAUDE.md, "Convenciones de codigo")."""
    p = Path(sample_path)
    pattern = re.compile(rf"^{re.escape(p.stem)}_(\d+){re.escape(p.suffix)}$")
    existing = [
        int(m.group(1))
        for f in p.parent.glob(f"{p.stem}_*{p.suffix}")
        if (m := pattern.match(f.name))
    ]
    return max(existing, default=0) + 1


def versioned(path, version):
    """'../output/foo.stl' -> '../output/foo_3.stl'."""
    p = Path(path)
    return str(p.with_name(f"{p.stem}_{version}{p.suffix}"))


def export_versioned(solid, name, out_dir):
    """Exporta STL (tolerance=0.05) + STEP con el mismo numeral consecutivo.
    El numeral sale del mayor existente entre ambos formatos, para que STL y
    STEP de una misma tanda compartan numero. Regresa (ruta_stl, ruta_step)."""
    check_valid(solid, name)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v = max(next_version_number(out / f"{name}.stl"),
            next_version_number(out / f"{name}.step"))
    stl = versioned(out / f"{name}.stl", v)
    step = versioned(out / f"{name}.step", v)
    cq.exporters.export(solid, stl, tolerance=0.05)
    cq.exporters.export(solid, step)
    return stl, step


def export_assembly_versioned(assy, name, out_dir):
    """Exporta un cq.Assembly a STEP con numeral consecutivo (solo STEP: el
    ensamble es para revisar en Onshape, no se imprime). Regresa la ruta."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    step = versioned(out / f"{name}.step", next_version_number(out / f"{name}.step"))
    assy.export(step)
    return step
