# CLAUDE.md — Carcasa para monitor de temperatura/humedad (pared HSW)

Punto de entrada para Claude Code. Aquí vive solo el **estado vigente** del proyecto. El brief de diseño original (generado en Claude Web) está en `externalfiles/README-carcasa-monitor.md`; el historial completo (día por día, decisiones, alternativas descartadas, lecciones) está en `docs/bitacora.md` — consultarla solo cuando haga falta el detalle de una decisión pasada.

## Prioridad 1 (regla crítica, por encima de todo lo demás)

**Nunca correr una búsqueda de filesystem sin acotar a la carpeta de este proyecto (`c:\medidorTHR`).** Nada de `find`/`grep -r`/búsquedas recursivas de shell con punto de partida `/`, `C:/`, el home del usuario, u otra carpeta fuera de este proyecto. Toda búsqueda (Glob, Grep, `find`, etc.) se acota a una ruta dentro de `c:\medidorTHR`. Si una búsqueda amplia es realmente inevitable, confirmar con Carlos antes de correrla. Excepción conocida y explícita: leer `c:\marco-rompecabezas` como referencia de estructura/código cuando Carlos lo indique.

## Qué es el proyecto

Diseñar en CadQuery e imprimir en FDM una **carcasa para un monitor ambiental** (ESP8266 Wemos D1 mini + ESPHome) montada en una **pared HSW (honeycomb storage wall)**, más una **cápsula aparte para el sensor remoto**. El frente muestra un LCD 16×2 (+ botón de backlight) con temperatura y humedad de dos puntos: **ambiente** (BME280 en la carcasa, aislado del calor de la electrónica) y **caja de filamentos** (BME280 remoto por cable CAT6). El circuito ya está validado en protoboard; este proyecto es sobre todo el diseño mecánico.

**Estado (2026-10-19):** **carcasa terminada**: las 3 piezas impresas en PETG rojo (`caja_delantera_6`, `caja_trasera_4`, `tapa_trasera_3`), armadas y **colgadas en la pared HSW**. 96 × 60 (cabe en el lugar de Carlos, máx. 100 de ancho). Lleva 3 días funcionando: humedad igual que otros medidores, temperatura ~1 °C distinta, sin offset (D-35). Firmware v2 instalado. Sensor remoto en pausa (D-34). Ver "Estado actual y próximos pasos".

## Entorno y restricciones duras

- **Impresora:** Bambu Lab **P1S**, laminador **Bambu Studio**. Material de la carcasa: **PETG rojo**.
- **CAD:** CadQuery (Python, paramétrico). Salida **STEP** (revisión/edición en Onshape) + **STL** (laminado).
- **Restricciones FDM** (brief, sección 6): pared ≥ 2.4 mm; holgura 0.2 mm en ajustes deslizantes, 0.3–0.4 mm en pasacables; evitar voladizos > 45°; torres/bosses con fillet en la base; orientar para que ventanas y rejillas no exijan soporte feo. Aristas sobre la cama con **chaflán de 45°** (no redondeo) contra el pie de elefante.
- **Brazos flexibles impresos verticales** (se abren entre capas): en PETG aguantaron ~4.4 % de flexión y se rompieron desde ~4.8 % (D-28).
- **Cierre:** tornillos M3 con **insertos térmicos** (Carlos tiene equipo), preferidos sobre autorroscante.
- **Cotas de componentes = medidas por Carlos** (especificación §6.2 y bitácora). Lo que siga nominal se marca "POR MEDIR" en `cad/parameters.py`.

## Preferencias de trabajo de Carlos (respétalas)

- Responde en **español**.
- Flujo **iterativo, con checkpoints de confirmación**: primero cuerpo y posiciones, luego detalles. No entregar el diseño completo de un jalón.
- Cuando entregues cambios de código, **entrega el archivo completo**, no parches línea por línea.
- **Todo archivo generado pasa por revisión de Carlos en Onshape** antes de imprimir, aunque los chequeos numéricos hayan salido bien.
- **No narrar en el chat las pruebas/verificaciones internas** (tests, chequeos numéricos, debugging). Correrlas normalmente y reportar solo la conclusión validada — salvo que Carlos lo pida o algo falle.
- **Regla de uniones (de `~/.claude/extras.md`):** toda unión necesita ≥ 2 puntos de fijación para bloquear rotación; aplicarla desde el diseño.
- Carlos pide que se cuestionen sus ideas con datos para llegar al mejor acuerdo.
- Archivos que Carlos copia y pega (p. ej. YAML): completos, versionados en el nombre (`_N`) y con la versión anotada en un comentario dentro del archivo.
- **Preguntas siempre numeradas** (1, 2, 3…) para que Carlos conteste por número (regla fija, también en `~/.claude/CLAUDE.md`).
- **Salida mínima en el chat**, la mía y la de los subagentes: estos responden en 2–3 líneas y el detalle va a archivos.
- Al pedir medidas, explicarlas con un dibujo (vista y puntos de referencia exactos). Para desfases, pedir las 2 distancias (p. ej. arriba y abajo) y cruzarlas con el total.
- Para decisiones estéticas del frente, mostrar un PNG 2D de la vista frontal (como `output/frente_hexagonos_3.png`).

## Arquitectura vigente

Detalle y razones en `docs/superpowers/specs/2026-09-25-carcasa-monitor-design.md` (D-01 a D-32; D-03, D-04, D-11 y D-22 superadas).

- **Montaje:** pared **HSW**. 2 conectores `hexagonconector3dprint` integrados a **40.88 mm** (misma fila), a ras del borde **superior** de la tapa trasera (va sobre la cama al imprimirla de pie). Puente de 1 mm embebido: **la tapa queda a 5.4 mm del panel**. Pestaña de 0.5 mm de primera capa (sin brim) con redondeo r = 1.0.
- **3 piezas (D-18):** (1) **tapa trasera** de pie; (2) **caja trasera** acostada sobre la pared divisoria (su fondo), con la placa y el Wemos; (3) **caja delantera** boca abajo, con LCD, botón y BME. El Wemos y el BME nunca comparten compartimento.
- **Unión (D-19, D-26):** 2 juegos de 4 M3×8 con insertos M3×4×4.2. Juego A: caja delantera ↔ trasera, desde dentro de la trasera, a **columnas cortas medio embebidas en las paredes laterales**, en las esquinas, con cara a 45° hacia el frente. Juego B: tapa ↔ caja trasera, desde atrás (cabezas cónicas en barrenos **avellanados** de la tapa, D-33, del lado del hueco de 5.4 mm), a columnas pegadas a las paredes a **±15** del centro. Se arma sobre la mesa y después se encaja en la rejilla.
- **Placa (D-17):** **50 × 50 × 1**, 4 barrenos Ø2.95 a 45.17, en postes con inserto M2.5. Componentes hacia la pared, USB hacia abajo. Lo más alto: cabezal del BME con su cable, 12.5 mm.
- **LCD (D-20, D-24, D-27):** el marco atraviesa el frente y queda a ras; ventana = marco + 0.3 por lado. Marco a **6.60 del borde de arriba y 5.40 del de abajo**. 4 **postes en cono (Ø11 → Ø8)** recortados contra el marco, con inserto M2.5 y M2.5×6. **Pines del I2C doblados hacia atrás**: el Dupont pasa a la caja trasera por una ventana en la divisoria, ubicada con lo medido en la caja con el LCD montado (2026-10-16).
- **Fila del botón (D-25):** botón al centro y BME a la izquierda, en la misma fila bajo el LCD.
- **BME de ambiente (D-21, D-29):** cable propio desde el cabezal hembra de 8 pines de la placa; montado sobre **2 escalones de 2 mm con pin de Ø2.5** (sobresale 3), fijado con una gota de silicón sobre los pines, sin remachar, chip hacia la rejilla. Trae 0x76 por defecto con 4 hilos.
- **Botón (D-28):** táctil 12 × 12 momentáneo; **clip con ceja de 0.70 y brazo de 0.6**, sin pegamento.
- **Rejillas (D-23, D-30):** hexagonales de 3.5. Frente: zona bajo la ventana con 3 mm de margen + columna en zigzag de 5 por lado + 5 arriba de la pantalla + 3 arriba del botón (47 en total; simétrica). Caja delantera también en sus paredes inferior y superior; caja trasera en sus paredes inferior y superior (chimenea).
- **Paso de cables de la divisoria** (botón y BME): 8 × 14, a la izquierda de la placa, abajo (1.5 del piso; D-32).
- **Sensor remoto (D-01, D-31):** I2C directo por CAT6 (1–1.5 m), SDA y SCL en pares distintos. Sale por una **muesca en la pared superior de la caja trasera**, al centro, abierta hacia la tapa; alivio con un cincho por dentro. En la placa: conector de 90° delgado sobre 6 pines al centro de la orilla opuesta al USB. Cápsula aparte atornillada al MDF; **la bornera de 4 polos va solo en la cápsula**.
- **Electrónica:** sensores SDA D1 / SCL D2 (así quedó soldada la placa; la guía de fase 2 dice al revés), LCD D6/D5 (bus aparte, 0x27), botón D7 a GND. **0x76 = ambiente**, **0x77 = filamentos**. Backlight: se enciende con el botón o al arrancar y se apaga sola a los 30 s.

## Especificaciones y parámetros

Fuente única de verdad: `cad/parameters.py`. Valores vigentes:

- HSW: `HSW_ROW_PITCH=40.88`, boca 22.0 / hexágono interior 20.0 entre caras planas, panel 8.0 mm
- Conector: clon de `hexagonconector3dprint.stl` (−0.6% de volumen), `CONN_STANDOFF=6.4`, `CONN_EMBED=1.0`, `CONN_FOOT_H=0.5`
- Carcasa: exterior **96.0 × 60.04 × 49.49** mm (+ 14.6 de conectores); `WALL_T=FRONT_T=DIV_T=2.4`; `TAPA_T=4.0`; pila en Y: tapa 0–4, caja trasera 4–27.9 (divisoria 25.5–27.9), caja delantera 27.9–49.49; `LCD_SIDE_GAP=5.6`, `TOP_MARGIN=BOTTOM_MARGIN=2.0`
- LCD: `LCD_BEZEL_TOP=6.72` (alto 24.0 centrado entre 6.60/5.40); `LCD_POST_D=8.0`, `LCD_POST_BASE_D=11.0`, `LCD_POST_BEZEL_CLEAR=0.3`; `LCD_CONN_TOP0=8.75`, `LCD_CONN_TOP1=25.0`, `LCD_CONN_SIDE=14.0`, `LCD_CONN_W=10.0`, `LCD_CONN_BACK=20.0`, `LCD_BACK_EDGE_FREE=2.0`, `DIV_LCD_WIN_CLEAR=1.0`
- Tornillería: M3×8 de cabeza cónica + `INS_M3_HOLE_D=4.0`; avellanado de la tapa `M3_CSK_D=6.0`, `M3_CSK_CLEAR=0.2` (boca Ø6.4, validado); M2.5×6 + `INS_M25_HOLE_D=3.3`; columnas M3 Ø8 a `BOSS_X=42.6` (`BOSS_SIDE_INSET=3.0`); `A_BOSS_Z=(6.4, 53.64)`, `A_COL_CAP=1.0`; `B_BOSS_DZ=15.0`
- Botón: `BTN_MOUNT="clip"`, `CLIP_LIP=0.70`, `CLIP_T=0.6`, `CLIP_GAP=0.2`, `BTN_LEG_FREE=1.0`
- BME: `BME_L=15.2`, `BME_W=11.5`, `BME_PCB_T=1.5`, `BME_HOLE_D=2.8`, `BME_HOLE_PITCH=10.15`, `BME_STANDOFF_D=4.6`, `BME_PIN_CLEAR=0.15`, `BME_PIN_OUT=3.0`
- CAT6: `CAT6_D=5.5`, `CAT6_CLEAR=0.4`; paso de cables `DIV_SLOT_W=8.0`, `DIV_SLOT_H=14.0`, `DIV_SLOT_FLOOR=1.5`
- Rejillas: `HEX_F2F=3.5`, `HEX_RIB=1.2`; frente `FRONT_VENT_MARGIN=3.0`, `SIDE_VENT_N=9`, `TOP_VENT_N=5`, `BTN_VENT_N=3`
- Impresión: `BED_CHAMFER=0.4` (no se aplica al conector)

## Decisiones vigentes clave

| Decisión | Razón (1 línea) | Ref. |
|---|---|---|
| CadQuery + STEP/STL, parámetros centralizados | Requisito del brief; flujo probado en `c:\marco-rompecabezas` | Brief §2 |
| I2C directo por CAT6 (≤ 1.5 m) | ~85 pF, muy por debajo del límite de 400 pF | D-01 |
| Conector `3dprint` ×2 a 40.88 mm, arriba | Probado por Carlos; 2 puntos bloquean el giro | D-10 |
| Orden: tapa → eléctrica + mediciones → distribución | Modelar la caja con medidas reales, no nominales | D-13 |
| 0x76 ambiente / 0x77 filamentos, corregido en el YAML | Corregir el software no cuesta nada | D-14 |
| Placa de 50 × 50 con el Wemos, CAT6 soldado | Era la placa que Carlos tenía a la mano | D-17 |
| Dos cajas separadas por profundidad | Wemos y BME en compartimentos distintos | D-18 |
| Dos juegos de 4 M3×8 | El M3 más largo del inventario es de 25 mm | D-19 |
| Marco del LCD a ras del frente | Mejor visión, −2.4 mm de fondo | D-20 |
| BME con cable propio de pines doblados | Conserva la desconexión sin crecer la caja | D-21 |
| Rejillas hexagonales, chimenea en la caja trasera | Aire limpio abajo para el BME; el calor sale arriba | D-23 |
| Ancho de 96 con pines del I2C del LCD doblados | El lugar mide 100; ventana centrada | D-24 |
| Botón y BME en la misma fila | Alto de 86 a 60 sin perder nada | D-25 |
| Columnas del juego A cortas y embebidas en las paredes | Liberan alto y el frente para la rejilla | D-26 |
| Postes del LCD en cono Ø11 → Ø8 | Con Ø5.6 el poste se torcía al meter el inserto | D-27 |
| Clip del botón 0.70 / 0.6, sin pegamento | Más ceja rompía el brazo; así sostiene | D-28 |
| BME con escalones y pines de 3 mm | Sin tornillería; se fija con silicón, sin remachar | D-29 |
| Rejilla del frente con columnas laterales y filas extra | Estética (Carlos) | D-30 |
| CAT6 por muesca superior abierta a la tapa | Se arma sin cortar ni recrimpar el cable | D-31 |
| Paso de cables del botón y BME abajo | A la altura de los 2; a la derecha está la placa | D-32 |
| Avellanado de 90° en los barrenos del juego B de la tapa | Los M3×8 son de cabeza cónica | D-33 |
| Sensor remoto y cápsula en pausa; solo ambiente | Decisión de Carlos | D-34 |
| Sin offset de temperatura (~1 °C de diferencia) | Humedad coincide; parece error propio del BME (±1 °C) | D-35 |
| Firmware v2: hora de HA en la 2a fila sin remoto; versión en HA | El remoto está en pausa; saber qué versión corre | D-36 |
| Sin labio entre cajas ni nuevas versiones de la carcasa | Ya funciona; queda como lección | D-37 |

## Estructura de carpeta y archivos clave

- `cad/parameters.py` — fuente única de verdad (HSW, conector, componentes medidos, carcasa, botón, BME, rejillas)
- `cad/geom.py` — primitivas (`box_between`, `cyl_y`, `cone_y`, `overlap_volume`, rejilla hexagonal)
- `cad/components.py` — envolventes de componentes en coordenadas globales (placa por partes, cable USB, LCD y su cable, botón, BME)
- `cad/hsw_connector.py` — clon paramétrico del conector HSW
- `cad/tapa_trasera.py`, `cad/caja_trasera.py`, `cad/caja_delantera.py` — las 3 piezas (`build_global()` / `build_print()`)
- `cad/boton.py` — alojamiento del botón (variantes de sujeción; vigente: clip)
- `cad/ensamble.py` — ensamble STEP de revisión (piezas en gris, envolventes en naranja)
- `cad/prueba_frente.py`, `cad/prueba_boton.py`, `cad/tapa_trasera_prueba.py` — piezas de prueba
- `cad/cq_utils.py` (export versionado STL+STEP y de ensambles), `cad/stl_ref.py` (lector de STL con numpy)
- `cad/test_*.py` — 66 tests; correr con `cd cad && python3 -m pytest -q`
- `output/` — exportaciones STL/STEP versionadas (`_1`, `_2`...); vigentes: `caja_delantera_6`, `caja_trasera_4`, `tapa_trasera_3`, `ensamble_16` (este sí va en git), `prueba_boton_4`, `frente_hexagonos_3.png`, `insertos_caja_trasera_1.png` / `insertos_caja_delantera_1.png` (mapa de insertos y tornillos).
- `esphome/bmetesting_2.yaml` — firmware ESPHome vigente (versión 2: hora en la 2a fila; `bmetesting_1.yaml` queda como histórico)
- `README.md` — presentación del repo: estado, carcasa, electrónica, BOM, resumen y lecciones
- `docs/bitacora.md` — **registro histórico del proyecto**
- `docs/fase2-armado-electrico.md` — guía de banco (pines, CAT6, prueba, cambios al YAML)
- `docs/img/tira_bus_3.png` — referencia del conexionado (la tira quedó superada por D-17)
- `docs/superpowers/specs/2026-09-25-carcasa-monitor-design.md` — **especificación de diseño** (al día hasta D-32)
- `docs/superpowers/plans/` — planes de la fase 1 (`2026-09-25-…`) y de la fase 2 (`2026-10-14-fase2-distribucion-carcasa.md`)
- `docs/portafolio/` — portafolio de evidencias (skill `/portafolio-evidencias`)
- `externalfiles/` — insumos externos (los `*.stl` de terceros solo existen en local: están en `.gitignore` y no se publican):
  - `README-carcasa-monitor.md` — brief original; desactualizado en el montaje (manda la especificación).
  - `wemosd1mini.stl` (trae tiras de pines hembra arriba que el Wemos de Carlos no tiene), `GY-BME280 module.stl`, `LCD1602.stl`, `PCF8574.stl` — referencia de terceros.
  - `HSl bakc wall assebly.stl` — pared HSW de Carlos (el eje Y del archivo es el vertical real); `HSW single back screw.stl` — solo referencia.
  - `grid1.step` — fragmento de la rejilla HSW para simular el ajuste en Onshape.
  - `hexagonconector3dprint.stl` — conector de resorte probado por Carlos. **Es el que se usa.**
  - `3mfs/` — proyectos y laminados de Bambu Studio; el laminado trae tiempo y gramos en `Metadata/slice_info.config`. `carcasa_completa_1.3mf` = cama con las 3 piezas vigentes (así se reimprime).
- Git: rama `main`, con remoto privado `origin` = github.com/quilofucar-web/Temp_TH_tester_wemos (desde 2026-10-16). No se versiona `output/` (salvo `output/ensamble_16.step`, el ensamble final), `externalfiles/grid1.step`, `.claude/settings.local.json` ni `.superpowers/sdd/`.
- `.claude/settings.local.json` — permisos del proyecto (`git *` permitido; `push --force`, `reset --hard` y `clean` piden confirmación)
- Python: `python3` tiene cadquery 2.8.0, numpy, matplotlib, pytest y PyYAML (no hay trimesh ni ESPHome).

## Convenciones de código

- Exportar STL (`tolerance=0.05`) **y** STEP con `cq_utils.export_versioned()` (mismo numeral en ambos); ensambles solo STEP con `export_assembly_versioned()`.
- **Cada archivo exportado lleva un numeral consecutivo al final del nombre** (`_1`, `_2`...), incluso si se regenera sin cambios. Nunca numerar a mano.
- Sin números mágicos: toda cota relevante como variable en `cad/parameters.py`.
- **Nunca usar loft/BSPLINE** — solo primitivas (box, extrude, extrude con taper, cilindros, conos, polígonos extruidos).
- Coordenadas globales: X ancho (0 al centro, +X a la derecha visto de frente), Y profundidad (0 en la cara trasera de la tapa, +Y al frente), Z vertical (0 abajo).
- Verificar posiciones/interferencias contra el sólido 3D real (`isInside`, volumen de intersección), no contra previews 2D.
- Antes de proponer un soporte o detalle, revisar en qué cara de impresión nace (sin soportes) y que no quede sobre huecos de rejilla.
- Al clonar una pieza probada, no omitir detalles "menores" sin preguntar (bitácora, lección 2).

## Estado actual y próximos pasos

- **Carcasa terminada y montada en la pared** (2026-10-19). No se imprimen más versiones (D-37).
- **Pendientes:**
  1. Foto del medidor montado en la pared (Carlos la pasa): agregarla al README y al proyecto.
  2. Ver en la pantalla la fecha y la hora de la v2 (el apagado de la luz a los 30 s ya se probó desde HA).
  3. Opcional: quitar o tapar el LED rojo de encendido del PCF8574 (no se apaga por software).
- Después: sensor remoto y cápsula (D-34).

## Historial

El registro completo del proyecto está en `docs/bitacora.md` — consultarla solo cuando se necesite el detalle de una decisión pasada.
