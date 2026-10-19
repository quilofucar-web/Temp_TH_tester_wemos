# Fase 2 — Distribución de la carcasa con medidas reales — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** pasar las medidas reales de los componentes (2026-10-14) a parámetros y modelar el **cuerpo y las posiciones** de las 3 piezas de la carcasa: tapa trasera final, caja trasera (Wemos) y caja delantera (LCD, botón, BME). Se entregan un ensamble STEP para revisar en Onshape y una pieza de prueba del frente para imprimir.

**Architecture:** `cad/parameters.py` suma las medidas y la distribución, con derivados calculados (nada a mano). `cad/geom.py` reúne las primitivas compartidas. `cad/components.py` modela las envolventes conservadoras de los componentes en coordenadas globales. Cada pieza tiene su módulo con `build_global()` (posición de uso) y `build_print()` (orientación de impresión). `cad/ensamble.py` junta las piezas y las envolventes en un STEP. Los tests prueban las interferencias contra los sólidos 3D reales.

**Tech Stack:** Python 3.11, CadQuery 2.8.0 (OCP), pytest. Se corre con `python3` desde `cad/`.

**Spec:** `docs/superpowers/specs/2026-09-25-carcasa-monitor-design.md` (la Task 1 le agrega D-18, D-19 y las mediciones).

## Global Constraints

- Responder y comentar en **español**. Al entregar cambios de código a Carlos, entregar el **archivo completo**.
- Exportar **STL (`tolerance=0.05`) y STEP** con `cq_utils.export_versioned()`: **numeral consecutivo** (`_1`, `_2`…), nunca a mano. El ensamble se exporta **solo en STEP** con `export_assembly_versioned()`.
- **Sin números mágicos**: toda cota en `cad/parameters.py`.
- **Nunca loft/BSPLINE**: solo primitivas (box, cilindros, extrude).
- Verificar posiciones e interferencias contra el sólido 3D (`isInside`, volumen de intersección), no contra vistas 2D.
- **Búsquedas de archivos solo dentro de `c:\medidorTHR`** (Prioridad 1 de `CLAUDE.md`).
- **Todo archivo generado pasa por la revisión de Carlos en Onshape** antes de imprimir.
- No narrar en el chat las verificaciones internas; reportar solo la conclusión.
- Sistema de coordenadas global: **X** = ancho (0 al centro), **Y** = profundidad (Y = 0 en la cara trasera de la tapa trasera; +Y hacia el frente), **Z** = vertical (Z = 0 en la base exterior de la carcasa).
- Restricciones FDM: pared ≥ 2.4 mm; holgura de 0.2 mm en los ajustes; sin voladizos > 45°; chaflán de 45° (`BED_CHAMFER`) en las aristas exteriores que tocan la cama.
- Regla de uniones: toda unión lleva ≥ 2 puntos de fijación (aquí son 4 en cada una).

## Alcance

Entra: **cuerpo y posiciones**: cascarones, pared divisoria, columnas y postes con inserto, ventanas del LCD, del botón y del USB, y paso de cables en la divisoria.

Queda para el plan de detalles (fase 3): rejillas y ventilación de las 2 cajas, soporte del BME, retenedor trasero del botón, alivio de tensión del USB y del CAT6, salida del CAT6, sellado del paso de cables y, si hicieran falta, topes inferiores de la tapa trasera.

## Distribución (resumen para el implementador)

```
 Vista lateral (Y →)                                   Vista frontal (X, Z)
 pared│5.4│tapa│ caja trasera   ║ caja delantera │     ┌──────────────────────────┐
      │   │ 4  │ placa 50×50 +  ║ LCD (marco     │     │ ●     paso de cables ▭  ●│ ← columnas A en
      │   │    │ Wemos, comp.   ║ contra frente) │     │   ┌──────────────────┐   │   las esquinas
      │   │    │ hacia la pared ║ botón          │     │   │ ventana del LCD  │   │
      │   │    │ USB hacia abajo║ BME abajo      │     │   └──────────────────┘   │
  Y:  0   4         27.2  29.6        53.59            │          [botón]         │
                    divisoria                          │ ●       BME (zona)      ● │
                                                       └──────────────────────────┘
 Exterior: 98.8 (X) × 86.04 (Z) × 53.59 (Y) + conectores HSW (14.6 hacia la pared)
```

- **Juego A** (caja delantera ↔ caja trasera): 4 M3×8 desde dentro de la caja trasera, pasando la divisoria, a insertos en las 4 columnas de esquina de la caja delantera.
- **Juego B** (tapa trasera ↔ caja trasera): 4 M3×8 desde atrás (las cabezas quedan en el hueco de 5.4 mm), a insertos en 4 columnas laterales de la caja trasera, a ±20 mm del centro vertical.
- Placa y LCD: M2.5×6 a insertos M2.5×4 en sus postes.
- Placa con los **componentes hacia la pared** y el **USB hacia abajo**. Gracias al patrón cuadrado de barrenos, cualquier giro de 90° usa los mismos postes; se revisa en el checkpoint.

## Estructura de archivos

| Archivo | Responsabilidad |
|---|---|
| `cad/parameters.py` | + medidas de componentes, tornillería, distribución y derivados |
| `cad/geom.py` (nuevo) | `box_between`, `cyl_y`, `overlap_volume` |
| `cad/components.py` (nuevo) | envolventes de la placa, el cable USB, el LCD, el botón y el BME; `pcb_point`, `pcb_holes_xz`, `usb_center`, `lcd_holes_xz`, `all_envelopes` |
| `cad/cq_utils.py` | + `export_assembly_versioned` |
| `cad/tapa_trasera.py` (nuevo) | tapa final: conectores arriba + barrenos del juego B |
| `cad/caja_trasera.py` (nuevo) | pieza 2 |
| `cad/caja_delantera.py` (nuevo) | pieza 3 |
| `cad/ensamble.py` (nuevo) | ensamble STEP de revisión |
| `cad/prueba_frente.py` (nuevo) | recorte de la caja delantera para la prueba física |
| `cad/test_components.py`, `test_tapa_trasera.py`, `test_caja_trasera.py`, `test_caja_delantera.py`, `test_ensamble.py` (nuevos); `test_cq_utils.py` (modificado) | tests |

`cad/tapa_trasera_prueba.py` y su test no cambian: `TAPA_W = 90` queda como medida de la pieza de prueba, y la tapa final usa `OUT_W`.

---

### Task 1: Registrar mediciones y decisiones en la especificación

**Files:**
- Modify: `docs/superpowers/specs/2026-09-25-carcasa-monitor-design.md`

**Interfaces:**
- Produces: D-18 y D-19 citables desde el código y los docstrings.

- [ ] **Step 1: Tabla de decisiones (§2).** Al inicio de la celda de decisión de las filas **D-03** y **D-04**, anteponer `**(Superada por D-18)**`; en la fila **D-11**, `**(Superada por D-19)**`. Agregar al final de la tabla:

```markdown
| D-18 | **Dos cajas separadas por profundidad** (2026-10-14): **caja trasera** (contra la pared) con la placa de 50 × 50 y el Wemos; **caja delantera** con el LCD, el botón y el BME de ambiente abajo. La pared divisoria es el fondo de la caja trasera. El BME sale de su cabezal con 4 cables Dupont (VCC, GND, SCL, SDA): el módulo trae por defecto la dirección 0x76 con CSB y SDO sin conectar | Idea de Carlos. El Wemos y el BME no comparten compartimento. En la caja delantera solo calienta la luz del LCD, que se apaga a los 30 s, y el BME va abajo con la entrada de aire abajo. D-04 ya no servía: el BME sobresale 5.9 mm de la placa y su chip queda a ~1.7 mm del lado caliente | Compartimento inferior en la misma caja con ranura (D-03/D-04) |
| D-19 | **Dos juegos de 4 M3×8** en lugar de 4 pasantes. Juego A: caja delantera ↔ caja trasera, desde dentro de la caja trasera. Juego B: tapa trasera ↔ caja trasera, desde atrás | Con ~54 mm de fondo, los pasantes medirían ~50 mm y el M3 más largo del inventario es de 25 mm. Se conservan el frente limpio, los 4 puntos por unión y el armado antes de colgar | Comprar M3×50 |
```

- [ ] **Step 2: Tabla de piezas (§3).** Reemplazar las filas 2 y 3 por:

```markdown
| 2 | **Caja trasera** | Acostada sobre la pared divisoria (su fondo) | Placa de 50 × 50 en 4 postes con inserto M2.5 (componentes hacia la pared, USB hacia abajo); 4 columnas laterales con inserto M3 (juego B); 4 barrenos del juego A en la divisoria; paso de cables arriba en la divisoria; ventana del micro-USB en la pared inferior; ventilación (fase 3) |
| 3 | **Caja delantera** | Boca abajo (cara frontal en la cama) | Ventana del área visible del LCD; 4 postes con inserto M2.5 (frente intacto); ventana de la tapa del botón y alojamiento del cuerpo; zona del BME abajo; 4 columnas de esquina con inserto M3 (juego A); rejillas (fase 3) |
```

Y en la fila 1, cambiar "4 barrenos para los tornillos pasantes" por "4 barrenos del juego B (D-19); conectores a ras del borde **superior** (prueba de la fase 1)".

- [ ] **Step 3: Vista lateral (§3).** Reemplazar el bloque de la vista lateral y su título por:

````markdown
Vista lateral de referencia (D-18; fondo de la carcasa **53.6 mm**, más 5.4 mm de aire contra el panel):

```
  PARED HSW  5.4 aire | 1 tapa (4) | 2 caja trasera (25.6)      ║ 3 caja delantera (24.0)
  ◄═╣ conector  ═╪ M3 juego B ═▓ col. │ placa 50×50 + Wemos  ╪ A ▓│ LCD + botón
                                      │ (componentes → pared) ║   │ BME abajo ≋ rejilla
                                                    pared divisoria
```
````

- [ ] **Step 4: Mediciones (§6).** Marcar como hechas `[x]` las casillas del LCD, el PCF8574 y el Wemos. Agregar al final de §6:

```markdown
### 6.2 Mediciones reales (2026-10-14, calibrador de Carlos)

| Pieza | Medida |
|---|---|
| Placa | 50 × 50 × 1.0; componentes hasta 14.2 sobre la placa; pines del Wemos 4.5 por abajo; 4 barrenos Ø2.95 a 45.17 entre centros |
| Wemos / USB | El USB sobresale 2.2 del borde, con su centro a 17.6 del borde vecino; cara inferior del Wemos a ~3.1 sobre la placa |
| BME local | En cabezal hembra; sobresale 5.9 del borde; cara superior a 14.22 |
| LCD | Placa 80 × 36.24 × 1.6; barrenos Ø3 a 75.0 × 31.15 entre centros; marco 71 × 24 a 4.92 (izq.) / 5.33 (arriba), sobresale 7.18; área visible 64.53 × 14.12 a 2.70 / 4.24 del marco; módulo I2C hasta 9.81 detrás; conector derecho: ~5 fuera del borde, centro a 11.6 del borde inferior, hasta 9.55 detrás; los Dupont hacen una curva suave de ~20 |
| Botón | Táctil 12 × 12, momentáneo; cuerpo 3.18; total con tapa 8.82; tapa 10 × 10; recorrido ~0.4 |
| Pendientes | Altura del centro del USB sobre la placa (se usa 5.4 estimado); sobremolde del cable micro-USB (se usa 12 × 8); BME con calibrador; posición del cabezal de 16 pines del LCD |
```

- [ ] **Step 5: Commit**

```bash
cd /c/medidorTHR && git add docs/superpowers/specs/2026-09-25-carcasa-monitor-design.md
git commit -m "docs(spec): D-18 dos cajas por profundidad, D-19 dos juegos de M3x8 y mediciones reales"
```

---

### Task 2: Parámetros medidos + primitivas + envolventes de componentes

**Files:**
- Modify: `cad/parameters.py` (agregar al final)
- Create: `cad/geom.py`, `cad/components.py`
- Modify: `cad/cq_utils.py` (agregar al final)
- Test: `cad/test_components.py` (nuevo), `cad/test_cq_utils.py` (modificar)

**Interfaces:**
- Produces:
  - `geom.box_between(p0, p1) -> Workplane`, `geom.cyl_y(x, z, d, y0, y1) -> Workplane`, `geom.overlap_volume(a, b) -> float`
  - `components.pcb_point(u, v, w) -> (x, y, z)`, `components.pcb_box(u0, u1, v0, v1, w0, w1)`, `components.pcb_holes_xz() -> [(x, z)]×4`, `components.usb_center() -> (x, y, z)`, `components.lcd_holes_xz() -> [(x, z)]×4`
  - `components.board_envelope()`, `usb_plug_envelope()`, `lcd_envelope()`, `button_envelope()`, `bme_envelope()`, `all_envelopes() -> {"placa", "cable_usb", "lcd", "boton", "bme"}`
  - `cq_utils.export_assembly_versioned(assy, name, out_dir) -> str` (ruta del STEP)
  - Parámetros: todos los del bloque de abajo (`OUT_W`, `OUT_H`, `Y_DIV0`, `Y_DIV1`, `Y_FRONT_IN`, `Y_FRONT`, `BOSS_X`, `A_BOSS_Z`, `B_BOSS_Z`, `PCB_Y_SOLDER`, `LCD_Y_PCB_FRONT`, `VIEW_XC`, `VIEW_ZC`, `BTN_XC`, `BTN_ZC`, etc.)

- [ ] **Step 1: Escribir el test que falla:** `cad/test_components.py`

```python
import pytest

import components as C
import parameters as P
from geom import overlap_volume


def test_measured_hole_pitches_center_to_center():
    assert P.PCB_HOLE_PITCH == pytest.approx(45.17)
    assert P.LCD_HOLE_PITCH_X == pytest.approx(75.0)
    assert P.LCD_HOLE_PITCH_Z == pytest.approx(31.15)


def test_case_size_and_depth_stack():
    assert P.OUT_W == pytest.approx(98.8)
    assert P.OUT_H == pytest.approx(86.04)
    assert P.Y_DIV0 == pytest.approx(27.2)
    assert P.Y_DIV1 == pytest.approx(29.6)
    assert P.Y_FRONT == pytest.approx(53.59)


def test_view_window_centered_in_case():
    assert abs(P.VIEW_XC) < 0.2


def test_pcb_mapping_usb_down_components_toward_wall():
    _, y, z = C.usb_center()
    assert z == pytest.approx(P.Z_IN0 + P.USB_EDGE_GAP)     # boca del USB abajo
    assert y < P.PCB_Y_COMP                                  # lado de componentes
    assert C.pcb_point(0, 0, 1)[1] < C.pcb_point(0, 0, 0)[1]  # w -> -Y (pared)


def test_board_envelope_fits_rear_cavity():
    bb = C.board_envelope().val().BoundingBox()
    assert bb.ymin == pytest.approx(P.Y_REAR0 + P.REAR_BACK_GAP)
    assert bb.ymax <= P.Y_DIV0 + 1e-6
    assert bb.zmin >= P.Z_IN0 - 1e-6 and bb.zmax <= P.Z_IN1
    assert -P.IN_W / 2 <= bb.xmin and bb.xmax <= P.IN_W / 2


def test_lcd_envelope_touches_front_and_clears_divider_and_bosses():
    bb = C.lcd_envelope().val().BoundingBox()
    assert bb.ymax == pytest.approx(P.Y_FRONT_IN)              # marco contra el frente
    assert bb.ymin == pytest.approx(P.Y_DIV1 + P.FRONT_BACK_GAP)
    assert bb.xmax <= P.IN_W / 2                               # conector derecho cabe
    assert bb.zmax <= P.A_BOSS_Z[1] - P.BOSS_D / 2             # libra las columnas


def test_button_cap_protrudes_from_front():
    bb = C.button_envelope().val().BoundingBox()
    assert bb.ymax - P.Y_FRONT == pytest.approx(P.BTN_TOTAL_H - P.BTN_BODY_H - P.FRONT_T)


def test_envelopes_do_not_overlap_each_other():
    env = C.all_envelopes()
    names = list(env)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            assert overlap_volume(env[a], env[b]) < 1e-3, (a, b)
```

Y en `cad/test_cq_utils.py`, cambiar el import a:

```python
from cq_utils import (check_valid, export_assembly_versioned, export_versioned,
                      next_version_number, versioned)
```

y agregar al final:

```python
def test_export_assembly_versioned_numbers_step(tmp_path):
    assy = cq.Assembly(cq.Workplane("XY").box(5, 5, 5), name="a")
    p1 = export_assembly_versioned(assy, "ens", tmp_path)
    p2 = export_assembly_versioned(assy, "ens", tmp_path)
    assert p1.endswith("ens_1.step") and p2.endswith("ens_2.step")
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `cd /c/medidorTHR/cad && python3 -m pytest test_components.py test_cq_utils.py -v`
Expected: ERROR con `ModuleNotFoundError: No module named 'components'` e `ImportError` de `export_assembly_versioned`.

- [ ] **Step 3: Agregar al final de `cad/parameters.py`**

```python

# =============================================================================
# Fase 2: componentes medidos y distribucion de la carcasa (D-18, D-19)
# =============================================================================

# --- Placa principal (medida 2026-10-14) ------------------------------------
# Ejes LOCALES (u, v, w), como en la foto con la cara de componentes hacia el
# observador: u = derecha, v = arriba, w = normal de la cara de componentes;
# origen en la esquina inferior izquierda. El micro-USB sale por el borde u = 0.
PCB_W = 50.0              # placa cuadrada de 50 x 50
PCB_T = 1.0
PCB_TOP_H = 14.2          # lo mas alto sobre la cara de componentes
PCB_BOTTOM_H = 4.5        # pines del Wemos por la cara de soldadura
PCB_HOLE_D = 2.95
PCB_HOLE_PITCH = 42.22 + PCB_HOLE_D            # 45.17 (se midio orilla a orilla)
PCB_HOLE_INSET = (PCB_W - PCB_HOLE_PITCH) / 2  # 2.415
USB_PROTRUDE = 2.2        # el micro-USB sobresale del borde u = 0
USB_V = 17.6              # centro del USB, desde el borde v = 0
USB_W = 5.4               # centro del USB sobre la cara de componentes (ESTIMADO 3.13 + 1.0 + 1.3; por medir)
USB_RECEPT_W = 8.0        # receptaculo micro-USB (nominal)
USB_RECEPT_H = 3.0
USB_PLUG_W = 12.0         # sobremolde del cable micro-USB (POR MEDIR)
USB_PLUG_H = 8.0
USB_PLUG_INSET = 0.2      # el sobremolde entra hasta 0.2 mm antes de la cara interior

# --- LCD 16x2 (medido 2026-10-14), visto de frente ---------------------------
LCD_W = 80.0
LCD_H = 36.24
LCD_PCB_T = 1.6
LCD_HOLE_D = 3.0
LCD_HOLE_PITCH_X = 72.0 + LCD_HOLE_D     # 75.0 (medido orilla a orilla)
LCD_HOLE_PITCH_Z = 28.15 + LCD_HOLE_D    # 31.15
LCD_BEZEL_W = 71.0
LCD_BEZEL_H = 24.0
LCD_BEZEL_LEFT = 4.92     # borde izquierdo de la placa -> marco
LCD_BEZEL_TOP = 5.33      # borde superior de la placa -> marco
LCD_BEZEL_D = 7.18        # el marco sobresale de la cara frontal de la placa
LCD_VIEW_W = 64.53
LCD_VIEW_H = 14.12
LCD_VIEW_LEFT = LCD_BEZEL_LEFT + 2.70    # 7.62 desde el borde izquierdo de la placa
LCD_VIEW_TOP = LCD_BEZEL_TOP + 4.24      # 9.57 desde el borde superior de la placa
LCD_BACK_D = 9.81         # modulo I2C (potenciometro) detras de la placa
LCD_CONN_OUT = 5.0        # conector de 4 pines + Dupont, fuera del borde derecho
LCD_CONN_H = 4 * 2.54     # 4 pines a 2.54
LCD_CONN_ZC = 11.6        # centro del conector, desde el borde inferior
LCD_CONN_D = 9.55         # hasta donde llega hacia atras, desde la cara trasera

# --- Boton tactil 12 x 12, momentaneo (medido 2026-10-14) --------------------
BTN_BODY = 12.0
BTN_BODY_H = 3.18         # cuerpo negro sin vastago
BTN_CAP = 10.0
BTN_TOTAL_H = 8.82        # base del cuerpo -> cara de la tapa verde
BTN_TRAVEL = 0.4

# --- BME280 de ambiente (del STL; POR MEDIR con calibrador) -----------------
BME_W = 11.5
BME_L = 15.3
BME_ENV_D = 16.0          # modulo + cabezal + carcasas Dupont, hacia atras
BME_FRONT_GAP = 2.0       # cara interior del frente -> modulo

# --- Tornilleria (inventario 2026-10-14) -------------------------------------
INS_M3_HOLE_D = 4.0       # INS-M3x4x4.2 (diametro exterior 4.2, largo 4)
M3_CLEAR_D = 3.4
M3_HEAD_D = 5.5
M3_SCREW_L = 8.0          # TOR-M3x8 en las 2 uniones (D-19)
INS_M25_HOLE_D = 3.3      # INS-M2.5x4x3.5 (diametro exterior 3.5, largo 4)
M25_SCREW_L = 6.0         # TOR-M2.5x6: placa y LCD

# --- Carcasa: 3 piezas (D-18, D-19) -----------------------------------------
WALL_T = 2.4
FRONT_T = 2.4             # cara frontal de la caja delantera
DIV_T = 2.4               # pared divisoria = fondo de la caja trasera
LCD_SIDE_GAP = 7.0        # a cada lado del LCD (conector derecho 5 + 2); centra la ventana
TOP_MARGIN = 9.0          # pared superior -> LCD (libra las columnas de esquina)
GAP_LCD_BTN = 3.0
GAP_BTN_BME = 3.0
BME_ZONE_H = 18.0
FRONT_BACK_GAP = 3.0      # modulo I2C -> pared divisoria (paso de cables)
REAR_POST_GAP = 1.5       # pines del Wemos -> pared divisoria
REAR_BACK_GAP = 2.0       # componentes de la placa -> tapa trasera
USB_EDGE_GAP = 0.3        # cara del micro-USB -> cara interior de la pared inferior
USB_WIN_CLEAR = 0.3       # holgura del sobremolde en su ventana, por lado
BOSS_D = 8.0              # columnas de tornillo M3
BOSS_INSET = 4.5          # centro de la columna -> caras interiores de las paredes
B_BOSS_DZ = 20.0          # columnas tapa-caja trasera: centro vertical +- 20
A_INSERT_DEPTH = 7.0      # caja delantera: M3x8 - divisoria 2.4 = 5.6, + holgura
B_INSERT_DEPTH = 6.0      # caja trasera: M3x8 - tapa 4.0 = 4.0, + holgura
PCB_POST_D = 6.0
LCD_POST_D = 5.6          # libra el marco del LCD (3.2 mm del centro a su esquina)
M25_INSERT_DEPTH = 6.0    # M2.5x6: punta a 5.0 (placa) o 4.4 (LCD) de la boca
BTN_CLEAR = 0.2           # cuerpo del boton en su alojamiento, por lado
BTN_CAP_CLEAR = 0.3       # tapa verde en su ventana, por lado
BTN_POCKET_WALL = 1.6
LCD_VIEW_MARGIN = 0.5     # ventana del frente: area visible + margen por lado
DIV_SLOT_W = 16.0         # paso de cables en la divisoria (Dupont del LCD, boton, BME)
DIV_SLOT_H = 8.0
DIV_SLOT_X = 25.0         # centro, del lado del conector del LCD
DIV_SLOT_TOP_GAP = 1.0

# --- Pieza de prueba del frente (ventana + postes del LCD + boton) ----------
PRUEBA_FRENTE_MARGIN = 3.0    # bajo el alojamiento del boton
PRUEBA_FRENTE_BACK = 1.0      # detras de la cara frontal de la placa del LCD

# --- Derivados (no editar: salen de lo anterior) -----------------------------
IN_W = LCD_W + 2 * LCD_SIDE_GAP                                      # 94.0
IN_H = (TOP_MARGIN + LCD_H + GAP_LCD_BTN + BTN_BODY
        + GAP_BTN_BME + BME_ZONE_H)                                  # 81.24
OUT_W = IN_W + 2 * WALL_T                                            # 98.8
OUT_H = IN_H + 2 * WALL_T                                            # 86.04
Z_IN0 = WALL_T                                                       # piso interior
Z_IN1 = WALL_T + IN_H                                                # techo interior
# Profundidad: Y = 0 es la cara trasera de la tapa trasera (hacia la pared)
Y_REAR0 = TAPA_T                                                     # 4.0
PCB_POST_H = PCB_BOTTOM_H + REAR_POST_GAP                            # 6.0
REAR_IN_D = PCB_POST_H + PCB_T + PCB_TOP_H + REAR_BACK_GAP           # 23.2
Y_DIV0 = Y_REAR0 + REAR_IN_D                                         # 27.2
Y_DIV1 = Y_DIV0 + DIV_T                                              # 29.6
FRONT_IN_D = FRONT_BACK_GAP + LCD_BACK_D + LCD_PCB_T + LCD_BEZEL_D   # 21.59
Y_FRONT_IN = Y_DIV1 + FRONT_IN_D                                     # 51.19
Y_FRONT = Y_FRONT_IN + FRONT_T                                       # 53.59
# Vista frontal (X, Z)
LCD_X0 = -LCD_W / 2
LCD_Z1 = Z_IN1 - TOP_MARGIN                                          # borde superior del LCD
LCD_Z0 = LCD_Z1 - LCD_H
LCD_Y_PCB_FRONT = Y_FRONT_IN - LCD_BEZEL_D                           # el marco toca el frente
VIEW_XC = LCD_X0 + LCD_VIEW_LEFT + LCD_VIEW_W / 2
VIEW_ZC = LCD_Z1 - LCD_VIEW_TOP - LCD_VIEW_H / 2
BTN_XC = VIEW_XC
BTN_ZC = LCD_Z0 - GAP_LCD_BTN - BTN_BODY / 2
BME_ZC = Z_IN0 + BME_ZONE_H / 2
# Placa con el USB hacia abajo (u -> +Z, v -> -X, w -> -Y), centrada en X
PCB_Z0 = Z_IN0 + USB_EDGE_GAP + USB_PROTRUDE
PCB_X0 = PCB_W / 2                                                   # v = 0 cae en X = +25
PCB_Y_SOLDER = Y_DIV0 - PCB_POST_H                                   # cara de soldadura
PCB_Y_COMP = PCB_Y_SOLDER - PCB_T                                    # cara de componentes
# Columnas de tornillo
BOSS_X = IN_W / 2 - BOSS_INSET                                       # 42.5
A_BOSS_Z = (Z_IN0 + BOSS_INSET, Z_IN1 - BOSS_INSET)                  # esquinas
B_BOSS_Z = ((Z_IN0 + Z_IN1) / 2 - B_BOSS_DZ, (Z_IN0 + Z_IN1) / 2 + B_BOSS_DZ)
```

- [ ] **Step 4: Crear `cad/geom.py`**

```python
"""Primitivas geometricas compartidas (cajas entre 2 esquinas, cilindros
paralelos a Y) y medicion de traslapes. Solo primitivas, sin loft
(CLAUDE.md, convenciones)."""
import cadquery as cq


def box_between(p0, p1):
    """Caja alineada a los ejes entre dos esquinas opuestas (en cualquier orden)."""
    lo = [min(a, b) for a, b in zip(p0, p1)]
    hi = [max(a, b) for a, b in zip(p0, p1)]
    size = [h - l for l, h in zip(lo, hi)]
    return cq.Workplane("XY").box(*size, centered=False).translate(tuple(lo))


def cyl_y(x, z, d, y0, y1):
    """Cilindro de diametro d con eje paralelo a Y, de y0 a y1 (en cualquier orden)."""
    lo, hi = min(y0, y1), max(y0, y1)
    return cq.Workplane(obj=cq.Solid.makeCylinder(
        d / 2, hi - lo, cq.Vector(x, lo, z), cq.Vector(0, 1, 0)))


def overlap_volume(a, b):
    """Volumen comun entre dos Workplane (0 si solo se tocan)."""
    return a.val().intersect(b.val()).Volume()
```

- [ ] **Step 5: Crear `cad/components.py`**

```python
"""Envolventes de los componentes medidos, en coordenadas globales de la
carcasa (X ancho, Y profundidad hacia el frente, Z vertical; ver
parameters.py). Son cajas conservadoras para revisar la distribucion en
Onshape y probar interferencias; no se imprimen.
"""
import parameters as P
from geom import box_between, cyl_y


# --- Placa principal ---------------------------------------------------------
def pcb_point(u, v, w):
    """Ejes locales de la placa -> globales. USB hacia abajo: u -> +Z,
    v -> -X, w (normal de la cara de componentes) -> -Y."""
    return (P.PCB_X0 - v, P.PCB_Y_COMP - w, P.PCB_Z0 + u)


def pcb_box(u0, u1, v0, v1, w0, w1):
    return box_between(pcb_point(u0, v0, w0), pcb_point(u1, v1, w1))


def pcb_holes_xz():
    """Centros (X, Z) de los 4 barrenos de la placa."""
    a, b = P.PCB_HOLE_INSET, P.PCB_W - P.PCB_HOLE_INSET
    pts = []
    for u in (a, b):
        for v in (a, b):
            x, _, z = pcb_point(u, v, 0)
            pts.append((x, z))
    return pts


def usb_center():
    """Centro (X, Y, Z) de la boca del micro-USB."""
    return pcb_point(-P.USB_PROTRUDE, P.USB_V, P.USB_W)


def board_envelope():
    """Placa + componentes (cara trasera) + pines (cara de soldadura, sin la
    zona de los postes) + receptaculo del micro-USB fuera del borde."""
    w = P.PCB_W
    env = (pcb_box(0, w, 0, w, -P.PCB_T, 0)
           .union(pcb_box(0, w, 0, w, 0, P.PCB_TOP_H)))
    pins = pcb_box(0, w, 0, w, -P.PCB_T - P.PCB_BOTTOM_H, -P.PCB_T)
    for x, z in pcb_holes_xz():
        pins = pins.cut(cyl_y(x, z, P.PCB_POST_D + 0.4, 0, P.Y_DIV0))
    env = env.union(pins)
    hw, hh = P.USB_RECEPT_W / 2, P.USB_RECEPT_H / 2
    recept = pcb_box(-P.USB_PROTRUDE, 0, P.USB_V - hw, P.USB_V + hw,
                     P.USB_W - hh, P.USB_W + hh)
    return env.union(recept)


def usb_plug_envelope():
    """Sobremolde del cable micro-USB: entra por la pared inferior hasta
    USB_PLUG_INSET antes de la cara interior, y sigue 15 mm hacia afuera."""
    x, y, _ = usb_center()
    hw, hh = P.USB_PLUG_W / 2, P.USB_PLUG_H / 2
    return box_between((x - hw, y - hh, -15.0),
                       (x + hw, y + hh, P.Z_IN0 - P.USB_PLUG_INSET))


# --- LCD ----------------------------------------------------------------------
def lcd_holes_xz():
    xc, zc = P.LCD_X0 + P.LCD_W / 2, P.LCD_Z0 + P.LCD_H / 2
    dx, dz = P.LCD_HOLE_PITCH_X / 2, P.LCD_HOLE_PITCH_Z / 2
    return [(xc + sx * dx, zc + sz * dz) for sx in (-1, 1) for sz in (-1, 1)]


def lcd_envelope():
    """Placa verde + marco (toca la cara interior del frente) + modulo I2C
    (toda el area de la placa, conservador) + conector derecho con Dupont."""
    x0, x1 = P.LCD_X0, P.LCD_X0 + P.LCD_W
    z0, z1 = P.LCD_Z0, P.LCD_Z1
    y_front = P.LCD_Y_PCB_FRONT
    y_back = y_front - P.LCD_PCB_T
    pcb = box_between((x0, y_back, z0), (x1, y_front, z1))
    bx0 = x0 + P.LCD_BEZEL_LEFT
    bz1 = z1 - P.LCD_BEZEL_TOP
    bezel = box_between((bx0, y_front, bz1 - P.LCD_BEZEL_H),
                        (bx0 + P.LCD_BEZEL_W, P.Y_FRONT_IN, bz1))
    back = box_between((x0, y_back - P.LCD_BACK_D, z0), (x1, y_back, z1))
    cz = z0 + P.LCD_CONN_ZC
    conn = box_between((x1, y_back - P.LCD_CONN_D, cz - P.LCD_CONN_H / 2),
                       (x1 + P.LCD_CONN_OUT, y_back, cz + P.LCD_CONN_H / 2))
    return pcb.union(bezel).union(back).union(conn)


# --- Boton y BME --------------------------------------------------------------
def button_envelope():
    """Cuerpo apoyado en la cara interior del frente + tapa verde."""
    b, c = P.BTN_BODY / 2, P.BTN_CAP / 2
    y_base = P.Y_FRONT_IN - P.BTN_BODY_H
    body = box_between((P.BTN_XC - b, y_base, P.BTN_ZC - b),
                       (P.BTN_XC + b, P.Y_FRONT_IN, P.BTN_ZC + b))
    cap = box_between((P.BTN_XC - c, P.Y_FRONT_IN, P.BTN_ZC - c),
                      (P.BTN_XC + c, y_base + P.BTN_TOTAL_H, P.BTN_ZC + c))
    return body.union(cap)


def bme_envelope():
    """BME de ambiente en la zona baja de la caja delantera, paralelo al
    frente, con sus cables Dupont hacia atras (D-18). El soporte se disena
    en la fase de detalles."""
    y1 = P.Y_FRONT_IN - P.BME_FRONT_GAP
    return box_between((-P.BME_L / 2, y1 - P.BME_ENV_D, P.BME_ZC - P.BME_W / 2),
                       (P.BME_L / 2, y1, P.BME_ZC + P.BME_W / 2))


def all_envelopes():
    """{nombre: Workplane} para el ensamble y las pruebas."""
    return {
        "placa": board_envelope(),
        "cable_usb": usb_plug_envelope(),
        "lcd": lcd_envelope(),
        "boton": button_envelope(),
        "bme": bme_envelope(),
    }
```

- [ ] **Step 6: Agregar al final de `cad/cq_utils.py`**

```python


def export_assembly_versioned(assy, name, out_dir):
    """Exporta un cq.Assembly a STEP con numeral consecutivo (solo STEP: el
    ensamble es para revisar en Onshape, no se imprime). Regresa la ruta."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    step = versioned(out / f"{name}.step", next_version_number(out / f"{name}.step"))
    assy.export(step)
    return step
```

- [ ] **Step 7: Correr y verificar que pasa**

Run: `cd /c/medidorTHR/cad && python3 -m pytest -v`
Expected: todo en verde (19 tests previos + 8 de componentes + 1 de cq_utils).

- [ ] **Step 8: Commit**

```bash
cd /c/medidorTHR && git add cad/parameters.py cad/geom.py cad/components.py cad/cq_utils.py cad/test_components.py cad/test_cq_utils.py
git commit -m "feat(cad): medidas reales de componentes, distribucion y envolventes (D-18, D-19)"
```

---

### Task 3: Tapa trasera final

**Files:**
- Create: `cad/tapa_trasera.py`
- Test: `cad/test_tapa_trasera.py`

**Interfaces:**
- Consumes: `hsw_connector.connector_placed(x_center, z_bottom)`, `geom.cyl_y`, `cq_utils.export_versioned`, parámetros de la Task 2.
- Produces: `tapa_trasera.build_print()`, `tapa_trasera.to_global(solid)`, `tapa_trasera.build_global()`.

- [ ] **Step 1: Escribir el test que falla:** `cad/test_tapa_trasera.py`

```python
import cadquery as cq
import pytest

import parameters as P
from tapa_trasera import build_global, build_print


@pytest.fixture(scope="module")
def tapa():
    return build_global()


def _inside(solid, p):
    return solid.val().isInside(cq.Vector(*p))


def test_print_orientation_single_valid_solid_on_bed():
    t = build_print()
    assert t.val().isValid()
    assert len(t.solids().vals()) == 1
    assert t.val().BoundingBox().zmin == pytest.approx(0.0, abs=0.01)


def test_plate_size(tapa):
    bb = tapa.val().BoundingBox()
    assert bb.xmin == pytest.approx(-P.OUT_W / 2)
    assert bb.xmax == pytest.approx(P.OUT_W / 2)
    assert bb.zmin == pytest.approx(0.0, abs=0.01)
    assert bb.zmax == pytest.approx(P.OUT_H)
    assert bb.ymax == pytest.approx(P.TAPA_T)


def test_connectors_flush_with_top_edge(tapa):
    """Brazos de los 2 conectores presentes justo bajo el borde superior y
    terminando a 2 * CONN_HALF_H de el (resultado de la prueba: arriba)."""
    arm_mid = (P.CONN_ARM_IN + P.CONN_ARM_OUT) / 2
    z_low = P.OUT_H - 2 * P.CONN_HALF_H
    for xc in (-P.CONN_SPACING / 2, P.CONN_SPACING / 2):
        assert _inside(tapa, (xc - arm_mid, -10.0, P.OUT_H - 0.1))
        assert _inside(tapa, (xc - arm_mid, -10.0, z_low + 0.1))
        assert not _inside(tapa, (xc - arm_mid, -10.0, z_low - 0.5))


def test_b_screw_holes(tapa):
    for sx in (-1, 1):
        for z in P.B_BOSS_Z:
            x = sx * P.BOSS_X
            assert not _inside(tapa, (x, P.TAPA_T / 2, z))
            assert _inside(tapa, (x + P.M3_CLEAR_D / 2 + 0.5, P.TAPA_T / 2, z))
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `cd /c/medidorTHR/cad && python3 -m pytest test_tapa_trasera.py -v`
Expected: ERROR con `ModuleNotFoundError: No module named 'tapa_trasera'`

- [ ] **Step 3: Implementar `cad/tapa_trasera.py`**

```python
"""Tapa trasera (pieza 1), version final: placa de OUT_W x OUT_H con los 2
conectores HSW a ras del borde SUPERIOR (resultado de la prueba de la fase 1)
y 4 barrenos para los tornillos M3x8 que la unen a la caja trasera (juego B,
D-19; las cabezas quedan en el hueco de 5.4 mm contra el panel).

Se imprime DE PIE con el borde superior (el de los conectores) sobre la cama:
build_print() la deja asi; build_global() la coloca en el ensamble.

Uso:  cd cad && python3 tapa_trasera.py
"""
from pathlib import Path

import cadquery as cq

import parameters as P
from cq_utils import export_versioned
from geom import cyl_y
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
            plate = plate.cut(cyl_y(sx * P.BOSS_X, P.OUT_H - z, P.M3_CLEAR_D,
                                    -1.0, P.TAPA_T + 1.0))
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
```

- [ ] **Step 4: Correr y verificar que pasa**

Run: `cd /c/medidorTHR/cad && python3 -m pytest test_tapa_trasera.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
cd /c/medidorTHR && git add cad/tapa_trasera.py cad/test_tapa_trasera.py
git commit -m "feat(cad): tapa trasera final con conectores arriba y barrenos del juego B"
```

---

### Task 4: Caja trasera (pieza 2)

**Files:**
- Create: `cad/caja_trasera.py`
- Test: `cad/test_caja_trasera.py`

**Interfaces:**
- Consumes: `components.pcb_holes_xz()`, `components.usb_center()`, `components.usb_plug_envelope()`, `geom.box_between`, `geom.cyl_y`, `geom.overlap_volume`.
- Produces: `caja_trasera.build_global()`, `caja_trasera.to_print(solid)`, `caja_trasera.build_print()`.

- [ ] **Step 1: Escribir el test que falla:** `cad/test_caja_trasera.py`

```python
import cadquery as cq
import pytest

import parameters as P
from caja_trasera import build_global, build_print
from components import pcb_holes_xz, usb_center, usb_plug_envelope
from geom import overlap_volume

Y_DIV_MID = (P.Y_DIV0 + P.Y_DIV1) / 2


@pytest.fixture(scope="module")
def caja():
    return build_global()


def _inside(solid, p):
    return solid.val().isInside(cq.Vector(*p))


def test_print_orientation_single_valid_solid_on_bed():
    c = build_print()
    assert c.val().isValid()
    assert len(c.solids().vals()) == 1
    assert c.val().BoundingBox().zmin == pytest.approx(0.0, abs=0.01)


def test_divider_solid_and_cavity_open_to_back(caja):
    assert _inside(caja, (0.0, Y_DIV_MID, 40.0))
    assert not _inside(caja, (0.0, P.Y_REAR0 + 1.0, 40.0))
    assert not _inside(caja, (0.0, P.Y_DIV0 - 1.0, 40.0))


def test_pcb_posts_with_insert_holes(caja):
    for x, z in pcb_holes_xz():
        assert not _inside(caja, (x, P.PCB_Y_SOLDER + 1.0, z))
        assert _inside(caja, (x + P.INS_M25_HOLE_D / 2 + 0.6, P.PCB_Y_SOLDER + 1.0, z))


def test_b_columns_with_insert_holes(caja):
    for sx in (-1, 1):
        for z in P.B_BOSS_Z:
            x = sx * P.BOSS_X
            assert not _inside(caja, (x, P.Y_REAR0 + 1.0, z))
            assert _inside(caja, (x, P.Y_REAR0 + P.B_INSERT_DEPTH + 1.0, z))


def test_a_holes_through_divider(caja):
    for sx in (-1, 1):
        for z in P.A_BOSS_Z:
            assert not _inside(caja, (sx * P.BOSS_X, Y_DIV_MID, z))
            assert _inside(caja, (sx * P.BOSS_X + P.M3_CLEAR_D / 2 + 0.5, Y_DIV_MID, z))


def test_cable_slot_in_divider(caja):
    z = P.Z_IN1 - P.DIV_SLOT_TOP_GAP - P.DIV_SLOT_H / 2
    assert not _inside(caja, (P.DIV_SLOT_X, Y_DIV_MID, z))


def test_usb_window_and_plug_clearance(caja):
    x, y, _ = usb_center()
    assert not _inside(caja, (x, y, P.WALL_T / 2))
    assert _inside(caja, (x - P.USB_PLUG_W / 2 - P.USB_WIN_CLEAR - 1.0, y, P.WALL_T / 2))
    assert overlap_volume(usb_plug_envelope(), caja) < 1e-3
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `cd /c/medidorTHR/cad && python3 -m pytest test_caja_trasera.py -v`
Expected: ERROR con `ModuleNotFoundError: No module named 'caja_trasera'`

- [ ] **Step 3: Implementar `cad/caja_trasera.py`**

```python
"""Caja trasera (pieza 2, D-18): aloja la placa de 50 x 50 con el Wemos. Su
fondo es la pared divisoria que la separa de la caja delantera (el calor del
Wemos no llega al BME). Abierta hacia la tapa trasera.

Contenido (solo cuerpo y posiciones; rejillas y alivios de tension van en la
fase de detalles):
  - 4 postes con inserto M2.5 para la placa (cara de soldadura hacia la divisoria).
  - 4 columnas laterales con inserto M3 para la tapa trasera (juego B, D-19).
  - 4 barrenos en la divisoria para los M3x8 que sujetan la caja delantera
    (juego A, D-19; se atornillan desde aqui, con la caja abierta).
  - Paso de cables en la divisoria, arriba, del lado del conector del LCD.
  - Ventana del cable micro-USB en la pared inferior.

Se imprime acostada sobre la divisoria (cara Y = Y_DIV1 sobre la cama).

Uso:  cd cad && python3 caja_trasera.py
"""
from pathlib import Path

import parameters as P
from components import pcb_holes_xz, usb_center
from cq_utils import export_versioned
from geom import box_between, cyl_y

OUTPUT = Path(__file__).resolve().parent.parent / "output"


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
    sx0, sz1 = P.DIV_SLOT_X - P.DIV_SLOT_W / 2, P.Z_IN1 - P.DIV_SLOT_TOP_GAP
    body = body.cut(box_between((sx0, P.Y_DIV0 - 1.0, sz1 - P.DIV_SLOT_H),
                                (sx0 + P.DIV_SLOT_W, P.Y_DIV1 + 1.0, sz1)))
    # Ventana del cable micro-USB en la pared inferior
    x, y, _ = usb_center()
    ww = P.USB_PLUG_W / 2 + P.USB_WIN_CLEAR
    wh = P.USB_PLUG_H / 2 + P.USB_WIN_CLEAR
    body = body.cut(box_between((x - ww, y - wh, -1.0), (x + ww, y + wh, P.Z_IN0 + 1.0)))
    return body


def to_print(solid):
    """Ensamble -> impresion: la divisoria (cara Y = Y_DIV1) sobre la cama."""
    return solid.rotate((0, 0, 0), (1, 0, 0), -90).translate((0, 0, P.Y_DIV1))


def build_print():
    return to_print(build_global())


if __name__ == "__main__":
    stl, step = export_versioned(build_print(), "caja_trasera", OUTPUT)
    print("Exportado:", stl, step)
```

- [ ] **Step 4: Correr y verificar que pasa**

Run: `cd /c/medidorTHR/cad && python3 -m pytest test_caja_trasera.py -v`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
cd /c/medidorTHR && git add cad/caja_trasera.py cad/test_caja_trasera.py
git commit -m "feat(cad): caja trasera con divisoria, postes de la placa y columnas del juego B"
```

---

### Task 5: Caja delantera (pieza 3)

**Files:**
- Create: `cad/caja_delantera.py`
- Test: `cad/test_caja_delantera.py`

**Interfaces:**
- Consumes: `components.lcd_holes_xz()`, `geom.box_between`, `geom.cyl_y`.
- Produces: `caja_delantera.build_global()`, `caja_delantera.to_print(solid)`, `caja_delantera.build_print()`.

- [ ] **Step 1: Escribir el test que falla:** `cad/test_caja_delantera.py`

```python
import cadquery as cq
import pytest

import parameters as P
from caja_delantera import build_global, build_print
from components import lcd_holes_xz

Y_PLATE_MID = P.Y_FRONT - P.FRONT_T / 2


@pytest.fixture(scope="module")
def caja():
    return build_global()


def _inside(solid, p):
    return solid.val().isInside(cq.Vector(*p))


def test_print_orientation_single_valid_solid_on_bed():
    c = build_print()
    assert c.val().isValid()
    assert len(c.solids().vals()) == 1
    assert c.val().BoundingBox().zmin == pytest.approx(0.0, abs=0.01)


def test_lcd_view_window_open_and_framed(caja):
    hx, hz = P.LCD_VIEW_W / 2 - 0.2, P.LCD_VIEW_H / 2 - 0.2
    for dx in (-hx, 0.0, hx):
        for dz in (-hz, 0.0, hz):
            assert not _inside(caja, (P.VIEW_XC + dx, Y_PLATE_MID, P.VIEW_ZC + dz))
    edge = P.LCD_VIEW_H / 2 + P.LCD_VIEW_MARGIN
    assert _inside(caja, (P.VIEW_XC, Y_PLATE_MID, P.VIEW_ZC + edge + 1.0))
    assert _inside(caja, (P.VIEW_XC, Y_PLATE_MID, P.VIEW_ZC - edge - 1.0))


def test_lcd_posts_with_insert_holes_and_intact_front(caja):
    for x, z in lcd_holes_xz():
        assert not _inside(caja, (x, P.LCD_Y_PCB_FRONT + 1.0, z))
        assert _inside(caja, (x + P.INS_M25_HOLE_D / 2 + 0.6, P.LCD_Y_PCB_FRONT + 1.0, z))
        assert _inside(caja, (x, Y_PLATE_MID, z))


def test_button_window_and_pocket(caja):
    assert not _inside(caja, (P.BTN_XC, Y_PLATE_MID, P.BTN_ZC))                 # tapa verde
    assert not _inside(caja, (P.BTN_XC + P.BTN_BODY / 2, P.Y_FRONT_IN - 1.0, P.BTN_ZC))
    wall_x = P.BTN_XC + P.BTN_BODY / 2 + P.BTN_CLEAR + P.BTN_POCKET_WALL / 2
    assert _inside(caja, (wall_x, P.Y_FRONT_IN - 1.0, P.BTN_ZC))
    assert _inside(caja, (P.BTN_XC + P.BTN_CAP / 2 + P.BTN_CAP_CLEAR + 0.5,
                          Y_PLATE_MID, P.BTN_ZC))


def test_a_columns_with_insert_holes(caja):
    for sx in (-1, 1):
        for z in P.A_BOSS_Z:
            x = sx * P.BOSS_X
            assert not _inside(caja, (x, P.Y_DIV1 + 1.0, z))
            assert _inside(caja, (x, P.Y_DIV1 + P.A_INSERT_DEPTH + 1.0, z))
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `cd /c/medidorTHR/cad && python3 -m pytest test_caja_delantera.py -v`
Expected: ERROR con `ModuleNotFoundError: No module named 'caja_delantera'`

- [ ] **Step 3: Implementar `cad/caja_delantera.py`**

```python
"""Caja delantera (pieza 3, D-18): frente + paredes. Aloja el LCD, el boton y
el BME de ambiente (zona baja, lejos del calor del Wemos, que queda tras la
pared divisoria). Abierta hacia la caja trasera.

Contenido (solo cuerpo y posiciones; rejillas, soporte del BME y retenedor
del boton van en la fase de detalles):
  - Ventana del area visible del LCD y 4 postes con inserto M2.5 (el marco
    del LCD apoya en la cara interior del frente; frente intacto de FRONT_T).
  - Ventana de la tapa verde del boton y alojamiento de su cuerpo.
  - 4 columnas de esquina con inserto M3 (juego A, D-19).

Se imprime boca abajo (cara frontal Y = Y_FRONT sobre la cama).

Uso:  cd cad && python3 caja_delantera.py
"""
from pathlib import Path

import parameters as P
from components import lcd_holes_xz
from cq_utils import export_versioned
from geom import box_between, cyl_y

OUTPUT = Path(__file__).resolve().parent.parent / "output"


def build_global():
    hw, ihw = P.OUT_W / 2, P.IN_W / 2
    body = (box_between((-hw, P.Y_DIV1, 0.0), (hw, P.Y_FRONT, P.OUT_H))
            .faces(">Y").edges().chamfer(P.BED_CHAMFER))     # aristas sobre la cama
    body = body.cut(box_between((-ihw, P.Y_DIV1 - 1.0, P.Z_IN0),
                                (ihw, P.Y_FRONT_IN, P.Z_IN1)))
    # Columnas de esquina del juego A, pegadas a las 2 paredes de la esquina
    for sx in (-1, 1):
        for z, wall_z in zip(P.A_BOSS_Z, (P.Z_IN0, P.Z_IN1)):
            x = sx * P.BOSS_X
            col = (cyl_y(x, z, P.BOSS_D, P.Y_DIV1, P.Y_FRONT_IN)
                   .union(box_between((x, P.Y_DIV1, z - P.BOSS_D / 2),
                                      (sx * ihw, P.Y_FRONT_IN, z + P.BOSS_D / 2)))
                   .union(box_between((x - P.BOSS_D / 2, P.Y_DIV1, z),
                                      (x + P.BOSS_D / 2, P.Y_FRONT_IN, wall_z))))
            body = body.union(col).cut(
                cyl_y(x, z, P.INS_M3_HOLE_D, P.Y_DIV1 - 1.0, P.Y_DIV1 + P.A_INSERT_DEPTH))
    # Postes del LCD
    for x, z in lcd_holes_xz():
        body = body.union(cyl_y(x, z, P.LCD_POST_D, P.LCD_Y_PCB_FRONT, P.Y_FRONT_IN)).cut(
            cyl_y(x, z, P.INS_M25_HOLE_D, P.LCD_Y_PCB_FRONT - 1.0,
                  P.LCD_Y_PCB_FRONT + P.M25_INSERT_DEPTH))
    # Ventana del LCD
    vw = P.LCD_VIEW_W / 2 + P.LCD_VIEW_MARGIN
    vh = P.LCD_VIEW_H / 2 + P.LCD_VIEW_MARGIN
    body = body.cut(box_between((P.VIEW_XC - vw, P.Y_FRONT_IN - 1.0, P.VIEW_ZC - vh),
                                (P.VIEW_XC + vw, P.Y_FRONT + 1.0, P.VIEW_ZC + vh)))
    # Boton: alojamiento del cuerpo + ventana de la tapa verde
    pin = P.BTN_BODY / 2 + P.BTN_CLEAR
    pout = pin + P.BTN_POCKET_WALL
    y_pocket = P.Y_FRONT_IN - P.BTN_BODY_H
    body = body.union(box_between((P.BTN_XC - pout, y_pocket, P.BTN_ZC - pout),
                                  (P.BTN_XC + pout, P.Y_FRONT_IN, P.BTN_ZC + pout)))
    body = body.cut(box_between((P.BTN_XC - pin, y_pocket - 1.0, P.BTN_ZC - pin),
                                (P.BTN_XC + pin, P.Y_FRONT_IN, P.BTN_ZC + pin)))
    cw = P.BTN_CAP / 2 + P.BTN_CAP_CLEAR
    body = body.cut(box_between((P.BTN_XC - cw, P.Y_FRONT_IN - 1.0, P.BTN_ZC - cw),
                                (P.BTN_XC + cw, P.Y_FRONT + 1.0, P.BTN_ZC + cw)))
    return body


def to_print(solid):
    """Ensamble -> impresion: la cara frontal (Y = Y_FRONT) sobre la cama."""
    return solid.rotate((0, 0, 0), (1, 0, 0), -90).translate((0, 0, P.Y_FRONT))


def build_print():
    return to_print(build_global())


if __name__ == "__main__":
    stl, step = export_versioned(build_print(), "caja_delantera", OUTPUT)
    print("Exportado:", stl, step)
```

- [ ] **Step 4: Correr y verificar que pasa**

Run: `cd /c/medidorTHR/cad && python3 -m pytest test_caja_delantera.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
cd /c/medidorTHR && git add cad/caja_delantera.py cad/test_caja_delantera.py
git commit -m "feat(cad): caja delantera con ventana y postes del LCD, boton y columnas del juego A"
```

---

### Task 6: Ensamble, pieza de prueba del frente y exportación

**Files:**
- Create: `cad/ensamble.py`, `cad/prueba_frente.py`
- Test: `cad/test_ensamble.py`

**Interfaces:**
- Consumes: `build_global()` de las 3 piezas, `caja_delantera.to_print`, `components.all_envelopes()`, `cq_utils.export_assembly_versioned`.
- Produces: `ensamble.pieces() -> {"tapa_trasera", "caja_trasera", "caja_delantera"}`, `ensamble.build_assembly() -> cq.Assembly`, `prueba_frente.build_global()`, `prueba_frente.build_print()`.

- [ ] **Step 1: Escribir el test que falla:** `cad/test_ensamble.py`

```python
import cadquery as cq
import pytest

import parameters as P
from components import all_envelopes
from ensamble import build_assembly, pieces
from geom import overlap_volume
from prueba_frente import build_print as prueba_frente_print

INS_M3_L = 4.0    # largo de INS-M3x4x4.2
INS_M25_L = 4.0   # largo de INS-M2.5x4x3.5


@pytest.fixture(scope="module")
def ps():
    return pieces()


def _inside(solid, p):
    return solid.val().isInside(cq.Vector(*p))


def test_pieces_do_not_overlap(ps):
    names = list(ps)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            assert overlap_volume(ps[a], ps[b]) < 1e-3, (a, b)


def test_envelopes_clear_all_pieces(ps):
    for en, env in all_envelopes().items():
        for pn, piece in ps.items():
            assert overlap_volume(env, piece) < 1e-3, (en, pn)


def test_screw_set_a_coaxial_and_length_fits(ps):
    """M3x8 desde la cara trasera de la divisoria hasta el inserto de la caja
    delantera: agujero libre en ambas piezas, rosca >= largo del inserto y
    punta antes del fondo del agujero."""
    for sx in (-1, 1):
        for z in P.A_BOSS_Z:
            x = sx * P.BOSS_X
            assert not _inside(ps["caja_trasera"], (x, (P.Y_DIV0 + P.Y_DIV1) / 2, z))
            assert not _inside(ps["caja_delantera"], (x, P.Y_DIV1 + 1.0, z))
    tip = P.Y_DIV0 + P.M3_SCREW_L
    assert tip - P.Y_DIV1 >= INS_M3_L
    assert tip <= P.Y_DIV1 + P.A_INSERT_DEPTH - 0.5


def test_screw_set_b_coaxial_and_length_fits(ps):
    for sx in (-1, 1):
        for z in P.B_BOSS_Z:
            x = sx * P.BOSS_X
            assert not _inside(ps["tapa_trasera"], (x, P.TAPA_T / 2, z))
            assert not _inside(ps["caja_trasera"], (x, P.Y_REAR0 + 1.0, z))
    tip = P.M3_SCREW_L                       # desde la cara trasera de la tapa (Y = 0)
    assert tip - P.Y_REAR0 >= INS_M3_L
    assert tip <= P.Y_REAR0 + P.B_INSERT_DEPTH - 0.5


def test_m25_screws_fit_board_and_lcd():
    board_tip = P.M25_SCREW_L - P.PCB_T          # desde la boca del inserto
    lcd_tip = P.M25_SCREW_L - P.LCD_PCB_T
    for tip in (board_tip, lcd_tip):
        assert INS_M25_L <= tip <= P.M25_INSERT_DEPTH - 0.5


def test_set_a_heads_clear_rear_box(ps):
    """Las cabezas del juego A quedan dentro de la caja trasera, sobre la
    divisoria: no deben chocar con las columnas B ni con las paredes."""
    for sx in (-1, 1):
        for z in P.A_BOSS_Z:
            x = sx * P.BOSS_X
            for dx, dz in ((P.M3_HEAD_D / 2, 0), (-P.M3_HEAD_D / 2, 0),
                           (0, P.M3_HEAD_D / 2), (0, -P.M3_HEAD_D / 2)):
                assert not _inside(ps["caja_trasera"], (x + dx * 0.95, P.Y_DIV0 - 1.0,
                                                        z + dz * 0.95))


def test_assembly_builds():
    assy = build_assembly()
    assert len(assy.children) == 3 + len(all_envelopes())


def test_prueba_frente_single_solid_on_bed():
    p = prueba_frente_print()
    assert p.val().isValid()
    assert len(p.solids().vals()) == 1
    bb = p.val().BoundingBox()
    assert bb.zmin == pytest.approx(0.0, abs=0.01)
    assert bb.zmax == pytest.approx(P.Y_FRONT - P.LCD_Y_PCB_FRONT + P.PRUEBA_FRENTE_BACK)
```

- [ ] **Step 2: Correr y verificar que falla**

Run: `cd /c/medidorTHR/cad && python3 -m pytest test_ensamble.py -v`
Expected: ERROR con `ModuleNotFoundError: No module named 'ensamble'`

- [ ] **Step 3: Crear `cad/ensamble.py`**

```python
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
```

- [ ] **Step 4: Crear `cad/prueba_frente.py`**

```python
"""Pieza de prueba del frente: recorte de la caja delantera con la ventana
del LCD, sus 4 postes con inserto M2.5 y el alojamiento del boton. Sirve para
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
    y0 = P.LCD_Y_PCB_FRONT - P.PRUEBA_FRENTE_BACK
    slab = box_between((-P.OUT_W / 2 - 1.0, y0, z0),
                       (P.OUT_W / 2 + 1.0, P.Y_FRONT + 1.0, P.OUT_H + 1.0))
    return caja_delantera.build_global().intersect(slab)


def build_print():
    return caja_delantera.to_print(build_global())


if __name__ == "__main__":
    stl, step = export_versioned(build_print(), "prueba_frente", OUTPUT)
    print("Exportado:", stl, step)
```

- [ ] **Step 5: Correr toda la suite**

Run: `cd /c/medidorTHR/cad && python3 -m pytest -v`
Expected: todo en verde (los 28 de las Tasks previas, 16 de las piezas y 8 del ensamble).

- [ ] **Step 6: Exportar**

```bash
cd /c/medidorTHR/cad && python3 ensamble.py && python3 prueba_frente.py && python3 tapa_trasera.py && python3 caja_trasera.py && python3 caja_delantera.py
```

Expected: `output/ensamble_1.step`, `prueba_frente_1.{stl,step}`, `tapa_trasera_1.{stl,step}`, `caja_trasera_1.{stl,step}`, `caja_delantera_1.{stl,step}` (el numeral sube solo si ya existían).

- [ ] **Step 7: Commit**

```bash
cd /c/medidorTHR && git add cad/ensamble.py cad/prueba_frente.py cad/test_ensamble.py
git commit -m "feat(cad): ensamble de revision y pieza de prueba del frente"
```

---

### Task 7: Checkpoint con Carlos (Onshape + pieza de prueba) y registro

**Files:**
- Modify (según el resultado): `cad/parameters.py`
- Modify: `docs/bitacora.md`, `CLAUDE.md` (en el `/cierre-dia`)

- [ ] **Step 1: Entregar a Carlos `output/ensamble_N.step`** para revisar en Onshape. En naranja van las envolventes (placa, cable USB, LCD, botón, BME); en gris, las piezas. Preguntas concretas:
  1. **Medidas exteriores** de 98.8 × 86 × 53.6 mm (más los conectores): ¿te parecen bien?
  2. **Placa:** componentes hacia la pared y **USB hacia abajo**, con el cable bajando por la pared. ¿O prefieres el USB a un costado? Se cambia girando la placa 90°, con los mismos postes.
  3. **Barreno de la esquina junto al Wemos:** el borde del Wemos queda a ~3.5 mm del borde de la placa, encima del barreno. ¿Entra el desarmador y cabe la cabeza del M2.5 bajo el Wemos? Si no, esa esquina va sin tornillo y la placa queda con 3.
  4. Medir, si se puede: altura del **centro del USB** sobre la placa (se usó 5.4 estimado) y el **sobremolde del cable micro-USB** (se usó 12 × 8).
- [ ] **Step 2: Entregar `output/prueba_frente_N.stl`** para imprimir boca abajo en PETG (~10.6 mm de alto). Qué revisar en físico:
  1. Insertos M2.5 en los 4 postes del LCD: ¿entran bien con el cautín (barreno de Ø3.3)?
  2. LCD con M2.5×6: ¿el marco apoya parejo en el frente y la ventana queda centrada sobre el área visible?
  3. ¿El cabezal de 16 pines del LCD choca con algún poste?
  4. Botón: ¿el cuerpo entra en su alojamiento? ¿La tapa verde asoma ~3.2 mm y se mueve sin rozar?
- [ ] **Step 3: Aplicar los ajustes.** Si hay que cambiar algo, cambiar **solo `cad/parameters.py`**, volver a correr `python3 -m pytest -v` (todo en verde), reexportar (el numeral sube solo) y repetir desde el Step 1.
- [ ] **Step 4: Registrar** el resultado en `docs/bitacora.md` y `CLAUDE.md` (con `/cierre-dia`) y hacer commit de `cad/parameters.py` si cambió.

---

## Siguiente plan (fase 3: detalles), no se ejecuta con este

Rejillas y ventilación (caja trasera: salida arriba y entrada abajo; caja delantera: entrada abajo junto al BME y salida arriba). Soporte del BME con clip. Retenedor trasero del botón con 2 tornillos (regla de 2 puntos). Alivio de tensión del USB. Salida del CAT6 con alivio. Sellado del paso de cables. Chaflán de las ventanas sobre la cama. Topes inferiores de la tapa trasera, si la caja colgada se mueve al presionar el botón. Después: impresión de las 3 piezas y la cápsula remota (fase 4).
