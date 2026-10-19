# Fase 1 — Base CAD + conector HSW + pieza de prueba de la tapa trasera — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** dejar lista la base de código CadQuery del proyecto (utilidades, parámetros, lectura de STL de referencia) y generar la **pieza de prueba de la tapa trasera** con los 2 conectores HSW integrados, para que Carlos la imprima y la pruebe en su pared real antes de modelar la carcasa.

**Architecture:** `cad/parameters.py` es la única fuente de verdad. `cad/hsw_connector.py` clona de forma paramétrica el conector de resorte `externalfiles/hexagonconector3dprint.stl`, validado contra ese STL (volumen y superficie). `cad/tapa_trasera_prueba.py` une una placa y 2 conectores a 40.88 mm y exporta STL + STEP numerados en `output/`.

**Tech Stack:** Python 3.11, CadQuery 2.8.0 (OCP), numpy, pytest 9. Se ejecuta con `python3` desde `cad/`.

**Spec:** `docs/superpowers/specs/2026-09-25-carcasa-monitor-design.md`

## Global Constraints

- Responder y comentar en **español**. Al entregar cambios de código, entregar el **archivo completo**.
- Exportar **STL (`tolerance=0.05`) y STEP**; cada export lleva **numeral consecutivo** (`_1`, `_2`…) calculado con `cq_utils`, nunca a mano.
- **Sin números mágicos**: toda cota en `cad/parameters.py`.
- **Nunca loft/BSPLINE**: solo primitivas (box, extrude, extrude con taper).
- **Búsquedas de archivos solo dentro de `c:\medidorTHR`** (Prioridad 1 de `CLAUDE.md`).
- **Todo archivo generado pasa por revisión de Carlos en Onshape** antes de imprimir.
- No narrar las verificaciones internas en el chat; reportar solo la conclusión.
- Sistema de coordenadas global: **X** = ancho, **Y** = profundidad (+Y se aleja de la pared), **Z** = vertical. La tapa trasera se imprime de pie: su Z = Z de la impresora.
- HSW: celdas de la misma fila a **40.88 mm**; hexágonos con cara plana arriba y abajo.

## Estructura de archivos

| Archivo | Responsabilidad |
|---|---|
| `.gitignore` | Ignorar cachés y `output/` (se regenera) |
| `cad/cq_utils.py` | `check_valid`, `next_version_number`, `versioned`, `export_versioned` |
| `cad/stl_ref.py` | Leer STL binarios de `externalfiles/` con numpy; volumen; vértices únicos |
| `cad/parameters.py` | Parámetros HSW, del conector, de la tapa trasera y de la pieza de prueba |
| `cad/hsw_connector.py` | `connector_local()`, `connector_placed(x_center, z_bottom)` |
| `cad/tapa_trasera_prueba.py` | `build()` + export de la pieza de prueba |
| `cad/test_cq_utils.py`, `cad/test_hsw_connector.py`, `cad/test_tapa_trasera_prueba.py` | Tests |

Las pruebas se corren desde `cad/` (los módulos se importan como módulos sueltos, igual que en `c:\marco-rompecabezas\cad`).

---

### Task 1: Repositorio git + utilidades de export + lector de STL

**Files:**
- Create: `.gitignore`
- Create: `cad/cq_utils.py`
- Create: `cad/stl_ref.py`
- Test: `cad/test_cq_utils.py`

**Interfaces:**
- Produces:
  - `cq_utils.check_valid(solid, name) -> solid` (lanza `RuntimeError` si no es válido)
  - `cq_utils.next_version_number(sample_path) -> int`
  - `cq_utils.versioned(path, version) -> str`
  - `cq_utils.export_versioned(solid, name: str, out_dir) -> (str, str)`: rutas STL y STEP con el mismo numeral
  - `stl_ref.EXTERNAL: Path` (= `<repo>/externalfiles`)
  - `stl_ref.load_stl_triangles(path) -> np.ndarray (n,3,3)`
  - `stl_ref.stl_volume(tris) -> float`
  - `stl_ref.unique_vertices(tris, decimals=3) -> np.ndarray (m,3)`

- [ ] **Step 1: Inicializar git y `.gitignore`**

```bash
cd /c/medidorTHR && git init
```

`.gitignore`:
```
__pycache__/
.pytest_cache/
output/
```

- [ ] **Step 2: Escribir el test que falla** — `cad/test_cq_utils.py`

```python
import cadquery as cq
import pytest

from cq_utils import check_valid, export_versioned, next_version_number, versioned


def test_next_version_number_empty_dir(tmp_path):
    assert next_version_number(tmp_path / "foo.stl") == 1


def test_next_version_number_skips_to_max(tmp_path):
    (tmp_path / "foo_1.stl").write_text("x")
    (tmp_path / "foo_3.stl").write_text("x")
    (tmp_path / "foobar_9.stl").write_text("x")   # otro nombre base: no cuenta
    assert next_version_number(tmp_path / "foo.stl") == 4


def test_versioned_inserts_suffix():
    assert versioned("out/foo.stl", 3).replace("\\", "/") == "out/foo_3.stl"


def test_check_valid_raises_on_invalid():
    class Fake:
        def val(self):
            class V:
                def isValid(self):
                    return False
            return V()
    with pytest.raises(RuntimeError):
        check_valid(Fake(), "fake")


def test_export_versioned_writes_stl_and_step_same_number(tmp_path):
    box = cq.Workplane("XY").box(10, 10, 10)
    stl, step = export_versioned(box, "cubo", tmp_path)
    assert stl.endswith("cubo_1.stl") and step.endswith("cubo_1.step")
    (tmp_path / "cubo_1.stl").unlink()          # aunque falte el STL, el STEP _1 existe
    stl2, step2 = export_versioned(box, "cubo", tmp_path)
    assert stl2.endswith("cubo_2.stl") and step2.endswith("cubo_2.step")
```

- [ ] **Step 3: Correr y verificar que falla**

Run: `cd /c/medidorTHR/cad && python3 -m pytest test_cq_utils.py -v`
Expected: FAIL / ERROR con `ModuleNotFoundError: No module named 'cq_utils'`

- [ ] **Step 4: Implementar `cad/cq_utils.py`**

```python
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
```

- [ ] **Step 5: Implementar `cad/stl_ref.py`** (lo usa el test de la Task 2; no lleva test propio porque ahí se ejercita contra un STL real)

```python
"""Lectura minima de STL binarios de referencia (externalfiles/) con numpy.

No hay trimesh instalado; esto alcanza para medir y comparar."""
from pathlib import Path

import numpy as np

EXTERNAL = Path(__file__).resolve().parent.parent / "externalfiles"


def load_stl_triangles(path):
    """Regresa un array (n, 3, 3) con los vertices de cada triangulo."""
    data = Path(path).read_bytes()
    n = int(np.frombuffer(data[80:84], "<u4")[0])
    if 84 + n * 50 != len(data):
        raise ValueError(f"No es un STL binario valido: {path}")
    rec = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    return np.frombuffer(data[84:84 + n * 50], rec)["v"].astype(float)


def stl_volume(tris):
    """Volumen encerrado (teorema de la divergencia)."""
    return float(abs(np.einsum("ij,ij->i", tris[:, 0],
                               np.cross(tris[:, 1], tris[:, 2])).sum()) / 6)


def unique_vertices(tris, decimals=3):
    return np.unique(np.round(tris.reshape(-1, 3), decimals), axis=0)
```

- [ ] **Step 6: Correr y verificar que pasa**

Run: `cd /c/medidorTHR/cad && python3 -m pytest test_cq_utils.py -v`
Expected: 5 passed

- [ ] **Step 7: Commit**

```bash
cd /c/medidorTHR && git add .gitignore cad/cq_utils.py cad/stl_ref.py cad/test_cq_utils.py
git commit -m "feat(cad): utilidades de export versionado y lector de STL de referencia"
```

(En el primer commit, agregar también los archivos de proyecto ya existentes: `CLAUDE.md`, `docs/`, `externalfiles/`, `.claude/settings.local.json`.)

---

### Task 2: Parámetros + conector HSW paramétrico validado contra el STL

**Files:**
- Create: `cad/parameters.py`
- Create: `cad/hsw_connector.py`
- Test: `cad/test_hsw_connector.py`

**Interfaces:**
- Consumes: `stl_ref.EXTERNAL`, `stl_ref.load_stl_triangles`, `stl_ref.stl_volume`, `stl_ref.unique_vertices` (Task 1)
- Produces:
  - `parameters`: `HSW_*`, `CONN_*` (incluye `CONN_STANDOFF = 6.4`, `CONN_SPACING = 40.88`), `TAPA_T`, `TAPA_W`, `TAPA_PRUEBA_H`
  - `hsw_connector.connector_local() -> cq.Workplane`: ejes locales, punta en X=-9.8, base en X=+5.8, Z ∈ [-9.9, 9.9]
  - `hsw_connector.connector_placed(x_center: float, z_bottom: float = 0.0) -> cq.Workplane`: base en el plano Y=0, punta en Y=-15.6, centrado en X=x_center, Z ∈ [z_bottom, z_bottom+19.8]

- [ ] **Step 1: Escribir el test que falla** — `cad/test_hsw_connector.py`

```python
import numpy as np
import pytest
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Pnt

import parameters as P
from hsw_connector import connector_local, connector_placed
from stl_ref import EXTERNAL, load_stl_triangles, stl_volume, unique_vertices

REF_STL = EXTERNAL / "hexagonconector3dprint.stl"


@pytest.fixture(scope="module")
def local():
    return connector_local()


def _dist(shape, p):
    v = BRepBuilderAPI_MakeVertex(gp_Pnt(*map(float, p))).Vertex()
    return BRepExtrema_DistShapeShape(v, shape.wrapped).Value()


def test_local_is_single_valid_solid(local):
    assert local.val().isValid()
    assert len(local.solids().vals()) == 1


def test_local_bounding_box(local):
    bb = local.val().BoundingBox()
    assert bb.xmin == pytest.approx(P.CONN_X_TIP, abs=0.01)
    assert bb.xmax == pytest.approx(P.CONN_X_BASE, abs=0.01)
    assert bb.ymax == pytest.approx(P.CONN_B_YTRUNC, abs=0.01)
    assert bb.zmax == pytest.approx(P.CONN_HALF_H, abs=0.01)


def test_volume_matches_reference_stl(local):
    ref = stl_volume(load_stl_triangles(REF_STL))
    assert ref == pytest.approx(P.CONN_REF_VOLUME, rel=0.001)
    assert local.val().Volume() == pytest.approx(ref, rel=0.03)


def test_surface_matches_reference_stl(local):
    """>= 92% de los vertices del STL original a <= 0.3 mm del modelo.
    El resto son las pestanas de adherencia de 0.5 mm que no se clonan."""
    pts = unique_vertices(load_stl_triangles(REF_STL))
    shape = local.val()
    close = sum(_dist(shape, p) <= 0.3 for p in pts)
    assert close / len(pts) >= 0.92


def test_standoff_is_6_4():
    assert P.CONN_STANDOFF == pytest.approx(6.4)


def test_placed_connector_frame():
    bb = connector_placed(20.0, z_bottom=0.0).val().BoundingBox()
    assert bb.ymax == pytest.approx(0.0, abs=0.01)                            # base en Y=0
    assert bb.ymin == pytest.approx(-(P.CONN_X_BASE - P.CONN_X_TIP), abs=0.01)  # punta -15.6
    assert bb.zmin == pytest.approx(0.0, abs=0.01)                            # a ras de la cama
    assert bb.zmax == pytest.approx(2 * P.CONN_HALF_H, abs=0.01)
    assert (bb.xmin + bb.xmax) / 2 == pytest.approx(20.0, abs=0.01)           # centrado en X
    assert bb.xmax - bb.xmin == pytest.approx(2 * P.CONN_B_YTRUNC, abs=0.01)  # puntas en X
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `cd /c/medidorTHR/cad && python3 -m pytest test_hsw_connector.py -v`
Expected: ERROR con `ModuleNotFoundError: No module named 'parameters'`

- [ ] **Step 3: Implementar `cad/parameters.py`**

```python
"""Fuente unica de verdad de parametros (mm).

Spec: docs/superpowers/specs/2026-09-25-carcasa-monitor-design.md

Sistema de coordenadas global de la carcasa (montada en la pared):
  X = horizontal (ancho), Y = profundidad (+Y se aleja de la pared, hacia
  el frente), Z = vertical (arriba). La tapa trasera (pieza 1) se imprime de
  pie, asi que su Z global = Z de la impresora.
"""

# --- Pared HSW (medido de externalfiles/HSl bakc wall assebly.stl) ---------
HSW_MOUTH_F2F = 22.0      # boca frontal, entre caras planas
HSW_MOUTH_DEPTH = 2.0     # profundidad de la boca de 22
HSW_CELL_F2F = 20.0       # hexagono interior
HSW_PANEL_T = 8.0         # grosor del panel
HSW_CELL_PITCH = 23.6     # centro a centro, celdas vecinas
HSW_ROW_PITCH = 40.88     # centro a centro, misma fila horizontal
HSW_BACK_GAP = 17.0       # hueco libre detras del panel

# --- Conector HSW: clon parametrico de externalfiles/hexagonconector3dprint.stl
# Ejes LOCALES del conector: X = insercion (punta en -X, base en +X),
# Y = direccion de las puntas del hexagono, Z = entre caras planas.
CONN_HALF_H = 9.9         # medio alto (caras planas en Z = +-9.9)
CONN_X_TIP = -9.8         # punta (entra primero a la pared)
CONN_X_BASE = 5.8         # cara de la base (se une a la pieza)
CONN_ARM_IN = 3.8         # cara interior de cada brazo (|Y|)
CONN_ARM_OUT = 5.8        # cara exterior de cada brazo (|Y|)
CONN_BRIDGE_T = 1.0       # espesor del puente de la base (U cerrada)
# Placa A (punta; se engancha detras del panel). Tramos (x, radio
# circunscrito del hexagono): chaflan de entrada, meseta, rampa de retencion.
CONN_A_PROFILE = ((-9.8, 11.547), (-8.8, 12.702), (-8.27, 12.702), (-7.3, 11.46))
CONN_A_YTRUNC = 12.413    # truncado de las puntas de la placa A (|Y|)
# Placa B (asienta en la boca de 22 del panel)
CONN_B_X0 = -2.2
CONN_B_X1 = -0.6
CONN_B_R = 12.99          # radio circunscrito (lados a 60 grados ~ hex de 22.5)
CONN_B_YTRUNC = 12.673
CONN_REF_VOLUME = 2040.5  # mm3, volumen del STL original (referencia de test)
# Separacion entre la cara trasera de la pieza y la cara del panel HSW:
CONN_STANDOFF = CONN_X_BASE - CONN_B_X1   # 6.4

# --- Tapa trasera (pieza 1) -------------------------------------------------
TAPA_T = 4.0              # espesor de la tapa trasera
TAPA_W = 90.0             # ancho provisional (~ancho de la caja; se fija en la fase 3)
CONN_SPACING = HSW_ROW_PITCH   # 2 conectores en la misma fila horizontal

# --- Pieza de prueba de la tapa trasera (fase 1) ---------------------------
TAPA_PRUEBA_H = 30.0      # alto de la placa de prueba
```

- [ ] **Step 4: Implementar `cad/hsw_connector.py`**

```python
"""Conector HSW de resorte: clon parametrico de
externalfiles/hexagonconector3dprint.stl (conector probado por Carlos).

Geometria (ejes locales, ver parameters.py):
  - 2 brazos (|Y| entre CONN_ARM_IN y CONN_ARM_OUT) de la punta a la base,
    unidos solo en la base por un puente -> las mitades flexionan (resorte).
  - Placa B: asienta en la boca de 22 del panel.
  - Placa A (punta): pasa el hexagono de 20 flexionando los brazos y se
    engancha detras del panel con su rampa trasera.
  - La cara de la base queda a CONN_STANDOFF (6.4 mm) de la cara del panel.
Se imprime de pie (Z local = Z impresora), con la cara Z = -CONN_HALF_H
sobre la cama. No se clonan las pestanas de adherencia de 0.5 mm del STL.
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
    return arms.union(bridge).union(plate_a).union(plate_b)


def connector_placed(x_center, z_bottom=0.0):
    """Conector en coordenadas globales de la carcasa: base en el plano
    Y = 0 (cara trasera de la pieza), punta hacia -Y (la pared), centro en
    X = x_center, cara inferior en Z = z_bottom (a ras de la cama).
    Rotacion de +90 grados en Z: X local -> +Y global, Y local -> -X global."""
    return (connector_local()
            .rotate((0, 0, 0), (0, 0, 1), 90)
            .translate((x_center, -P.CONN_X_BASE, z_bottom + P.CONN_HALF_H)))
```

- [ ] **Step 5: Correr y verificar que pasa**

Run: `cd /c/medidorTHR/cad && python3 -m pytest test_hsw_connector.py -v`
Expected: 6 passed (en la corrida de prueba del plan, el volumen del clon dio 2013.4 contra 2040.5 del STL: −1.3%)

- [ ] **Step 6: Commit**

```bash
cd /c/medidorTHR && git add cad/parameters.py cad/hsw_connector.py cad/test_hsw_connector.py
git commit -m "feat(cad): conector HSW parametrico validado contra el STL de referencia"
```

---

### Task 3: Pieza de prueba de la tapa trasera + export

**Files:**
- Create: `cad/tapa_trasera_prueba.py`
- Test: `cad/test_tapa_trasera_prueba.py`

**Interfaces:**
- Consumes: `parameters.TAPA_W`, `TAPA_T`, `TAPA_PRUEBA_H`, `CONN_SPACING`, `CONN_ARM_IN`, `CONN_ARM_OUT`, `CONN_HALF_H` (Task 2); `hsw_connector.connector_placed` (Task 2); `cq_utils.export_versioned` (Task 1)
- Produces: `tapa_trasera_prueba.build() -> cq.Workplane`: placa X ∈ [-45, 45], Y ∈ [0, 4], Z ∈ [0, 30], más conectores en X = ±20.44 con la punta hacia -Y. Al correrlo como script genera `output/tapa_trasera_prueba_N.stl` y `.step`.

- [ ] **Step 1: Escribir el test que falla** — `cad/test_tapa_trasera_prueba.py`

```python
import cadquery as cq
import pytest

import parameters as P
from tapa_trasera_prueba import build


@pytest.fixture(scope="module")
def tapa():
    return build()


def _inside(solid, p):
    return solid.val().isInside(cq.Vector(*p))


def test_single_valid_solid(tapa):
    assert tapa.val().isValid()
    assert len(tapa.solids().vals()) == 1


def test_sits_flat_on_bed(tapa):
    assert tapa.val().BoundingBox().zmin == pytest.approx(0.0, abs=0.01)


def test_connectors_spaced_on_hsw_row_pitch(tapa):
    """Brazos presentes a +-4.8 mm del centro de cada conector y ranura vacia
    en el centro, a Y=-10 (zona de brazos), justo encima de la cama."""
    arm_mid = (P.CONN_ARM_IN + P.CONN_ARM_OUT) / 2
    for xc in (-P.CONN_SPACING / 2, P.CONN_SPACING / 2):
        for z in (0.1, P.CONN_HALF_H):
            assert _inside(tapa, (xc - arm_mid, -10.0, z))
            assert _inside(tapa, (xc + arm_mid, -10.0, z))
            assert not _inside(tapa, (xc, -10.0, z))
    assert P.CONN_SPACING == pytest.approx(40.88)


def test_plate_back_face_at_y0(tapa):
    assert _inside(tapa, (0.0, 0.1, 10.0))                # placa entre conectores
    assert not _inside(tapa, (0.0, -0.1, 10.0))           # nada detras entre conectores
    assert _inside(tapa, (0.0, P.TAPA_T - 0.1, 10.0))
    assert not _inside(tapa, (0.0, P.TAPA_T + 0.1, 10.0))
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `cd /c/medidorTHR/cad && python3 -m pytest test_tapa_trasera_prueba.py -v`
Expected: ERROR con `ModuleNotFoundError: No module named 'tapa_trasera_prueba'`

- [ ] **Step 3: Implementar `cad/tapa_trasera_prueba.py`**

```python
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
             .box(P.TAPA_W, P.TAPA_T, P.TAPA_PRUEBA_H, centered=(True, False, False)))
    for xc in (-P.CONN_SPACING / 2, P.CONN_SPACING / 2):
        plate = plate.union(connector_placed(xc, z_bottom=0.0))
    return plate


if __name__ == "__main__":
    stl, step = export_versioned(build(), "tapa_trasera_prueba", OUTPUT)
    print("Exportado:", stl, step)
```

- [ ] **Step 4: Correr toda la suite y verificar que pasa**

Run: `cd /c/medidorTHR/cad && python3 -m pytest -v`
Expected: 15 passed

- [ ] **Step 5: Exportar**

Run: `cd /c/medidorTHR/cad && python3 tapa_trasera_prueba.py`
Expected: `Exportado: ...output/tapa_trasera_prueba_1.stl ...output/tapa_trasera_prueba_1.step`

- [ ] **Step 6: Commit**

```bash
cd /c/medidorTHR && git add cad/tapa_trasera_prueba.py cad/test_tapa_trasera_prueba.py
git commit -m "feat(cad): pieza de prueba de la tapa trasera con 2 conectores HSW"
```

---

### Task 4: Checkpoint físico con Carlos + registro

**Files:**
- Modify: `docs/bitacora.md` (entrada nueva al final de la sección 3)
- Modify: `CLAUDE.md` ("Estado actual y próximos pasos")
- Modify (según el resultado): `cad/parameters.py`

- [ ] **Step 1: Entregar a Carlos** `output/tapa_trasera_prueba_N.step` (revisión en Onshape) y `.stl` (laminado). Indicaciones:
  - Imprimir **de pie, con el borde de los conectores sobre la cama**, sin soportes, en el mismo material con el que ya usó este conector.
- [ ] **Step 2: Carlos evalúa en su pared y reporta:**
  1. ¿Los 2 conectores entran a la vez en 2 celdas de la misma fila (40.88 mm) sin forzar?
  2. Retención: ¿quedan firmes? ¿Salen con facilidad cuando se quiere?
  3. ¿La placa queda paralela a la pared (6.4 mm de separación uniforme) o se inclina?
  4. **Orientación:** probar la placa con los conectores **en el borde superior** y luego **en el inferior**, empujando la placa como si se presionara el botón. ¿En cuál se mueve menos?
- [ ] **Step 3: Registrar el resultado** en `docs/bitacora.md` (entrada con fecha) y en `CLAUDE.md`. Si hay que ajustar algo (holgura, separación), cambiar solo `cad/parameters.py`, volver a correr `python3 -m pytest -v` (todo en verde), reexportar (el numeral sube solo) y repetir desde el Step 1.
- [ ] **Step 4: Commit**

```bash
cd /c/medidorTHR && git add docs/bitacora.md CLAUDE.md cad/parameters.py
git commit -m "docs: resultado de la prueba fisica de la tapa trasera en la pared HSW"
```

---

## Hoja de ruta (fases siguientes: cada una con su propio plan)

Estas fases **no se ejecutan con este plan**. Dependen de las mediciones de la §6 de la especificación, y cada una se detalla en su propio plan cuando lleguen los datos (flujo iterativo con checkpoints, preferencia de Carlos).

| Fase | Entregable | Bloqueada por |
|---|---|---|
| 2 | **Armado eléctrico en banco** (tira de bus, cables largos sin recortar, prueba con ESPHome), hecho por Carlos, y después parámetros de componentes **medidos sobre el conjunto armado** + modelos de envolvente (LCD+PCF, Wemos, BME, botón, placa de bus) | Armado eléctrico; mediciones de la §6 y §6.1 de la especificación |
| 3 | Caja (pieza 2) + tapa de pantalla (pieza 3) + tapa trasera final (pieza 1) con los 4 tornillos pasantes; piezas de prueba: poste con inserto + ventana del LCD, barreno del botón | Fase 2 + resultado de la Task 4 (orientación de los conectores) |
| 4 | Detalles: rejillas, compartimento del BME, alivios de tensión de USB y CAT6 | Fase 3 |
| 5 | Cápsula del sensor remoto | Medida de la bornera, Ø del CAT6, tornillos para MDF |
