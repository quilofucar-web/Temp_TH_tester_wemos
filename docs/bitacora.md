# Bitácora del proyecto — Carcasa para monitor de temperatura/humedad (rack)

Registro histórico del proyecto: una entrada por día/sesión, con lo que se hizo, decisiones (y alternativas descartadas), problemas y su resolución, y pendientes. `CLAUDE.md` guarda solo el estado vigente; todo lo histórico vive aquí. Las entradas nuevas se agregan al final de la sección 3 (se puede usar `/cierre-dia`).

---

## 1. Ficha del proyecto

| Campo | Valor |
|---|---|
| Nombre | Carcasa impresa para monitor de temperatura/humedad (rack) |
| Objetivo | Diseñar en CadQuery e imprimir en FDM la carcasa de un monitor ESP8266 (Wemos D1 mini + ESPHome) con LCD 16×2, BME280 de ambiente aislado del calor y salida para un BME280 remoto por cable CAT6 |
| Inicio | Brief redactado en Claude Web (fecha no registrada); proyecto abierto en Claude Code el 2026-09-25 |
| Estado | Arranque |
| Herramientas | CadQuery (Python), Onshape (revisión), Bambu Studio + Bambu Lab P1S |
| Materiales | Por definir |

---

## 2. Resumen por fases

| Fase | Fechas | Resultado |
|---|---|---|
| 0. Brief inicial en Claude Web | antes de 2026-09-25 | `README-carcasa-monitor.md`: componentes, requisitos, restricciones FDM, checklist de medición, decisiones abiertas |
| 1. Arranque en Claude Code | 2026-09-25 | Estructura de carpetas, permisos, CLAUDE.md y bitácora |
| 2. Lluvia de ideas y arquitectura | 2026-09-25 | Montaje HSW con conector `3dprint`, 3 piezas, 4 tornillos pasantes, placa de bus, BME aislado. Especificación escrita |
| 3. Fase 1: tapa trasera de prueba | 2026-09-25 | Conector HSW paramétrico validado; `tapa_trasera_prueba_3` lista para imprimir |
| 4. Fase 2: preparación eléctrica | 2026-09-25 | Guía de banco, YAML v1, diagrama de la tira; armado pendiente (Carlos) |
| 5. Armado eléctrico e impresión de la tapa | 2026-10-13 | Placa de ~64 × 64 mm soldada (por medir); tapa de prueba v3 en impresión |
| 6. Fase 2: medición y distribución | 2026-10-14 | Prueba de la tapa OK; componentes medidos; 3 piezas modeladas con rejillas; pruebas de frente y botón listas |
| 7. Fase 2: pruebas y carcasa compacta | 2026-10-15 | Botón resuelto (clip 0.70/0.6); 96 × 60; caja_delantera_6 en impresión |

---

## 3. Registro cronológico

### 2026-09-25 — Apertura del proyecto en Claude Code

**Objetivo:** montar la base del proyecto a partir del brief de Claude Web, siguiendo la estructura de `c:\marco-rompecabezas`.

**Qué se hizo:**
- Revisado `externalfiles/README-carcasa-monitor.md` (brief generado en Claude Web). También en `externalfiles/`: `wemosd1mini.stl` y `GY-BME280 module.stl` (modelos de referencia de componentes).
- Creada la estructura: `cad/`, `output/`, `docs/`, `docs/portafolio/`, `.claude/`.
- Creado `.claude/settings.local.json` con permisos amplios **acotados al proyecto**: Read/Edit/Write/Glob/Grep sobre `c:\medidorTHR\**`, `ls`, `mkdir`, `python3` (scripts CadQuery y pytest), búsqueda web (firecrawl/perplexity). Reglas `deny` para búsquedas recursivas desde la raíz y `rm -rf`.
- Creados `CLAUDE.md` (estado vigente) y esta bitácora (historial).

**Decisiones:**
- **Decisión:** replicar la estructura y convenciones de `c:\marco-rompecabezas` (parámetros centralizados, exports versionados, CLAUDE.md vigente vs bitácora histórica). **Razón:** flujo ya probado por Carlos.
- **Decisión:** a diferencia del marco (que permite `Read(//c//**)`), la lectura queda acotada a la carpeta del proyecto. **Razón:** regla de Prioridad 1 (no buscar fuera del proyecto).
- **Decisión:** se incluye `Bash(python3 *)` como en el marco. **Razón:** necesario para correr CadQuery/pytest sin prompts; se asume el riesgo conocido de que un wildcard sobre intérprete permite ejecutar código arbitrario (ver `~/.claude/extras.md`, 2026-08-14).

**Pendientes:**
- Carlos sube archivos adicionales con ajustes al brief.
- Mediciones con calibrador (brief §7) y decisiones abiertas (brief §8).

### 2026-09-25 (tarde) — Lluvia de ideas y arquitectura general

**Objetivo:** con los insumos nuevos de Carlos (STLs del LCD1602, PCF8574, la pared HSW, el inserto HSW estándar y su conector `3dprint`), cuestionar las ideas iniciales y acordar la arquitectura.

**Qué se hizo:**
- Se midieron los STLs con un parser binario (numpy). LCD 80 × 36 × 18.7, PCF8574 46.6 × 18 × 13.2 y Wemos 25.7 × 34.25 × 11.5 coinciden con el brief; el BME280 mide 11.5 × 15.3 (más chico que el nominal).
- Pared HSW medida con cortes: boca de 22.0 mm entre caras planas (2 mm de profundidad), hexágono interior de 20.0 mm, panel de 8.0 mm, separación entre celdas de 23.6 mm, **40.88 mm en la misma fila**, ~17 mm de hueco detrás.
- Especificación escrita: `docs/superpowers/specs/2026-09-25-carcasa-monitor-design.md` (D-01…D-12).

**Decisiones (con lo que se cuestionó):**
- **Sensor remoto por I2C directo sobre CAT6.** Se cuestionó con datos: el límite del bus es 400 pF y el CAT6 tiene ~45–56 pF/m. Carlos confirmó 1–1.5 m (~85 pF), así que la conexión directa funciona. **Descartados:** extensor P82B715 y segundo ESP (solo se justifican desde ~2–3 m).
- **BME de ambiente en compartimento separado.** Se cuestionó la idea de dividir la caja como única solución: ~0.5 W internos sesgan la lectura. Queda en un compartimento inferior con pared divisoria y rejilla, y por fuera se ve una sola caja, que era el requisito de Carlos.
- **"Todo soldado al Wemos" → placa de bus de 4 tiras.** Se cuestionó: el Wemos tiene 1 solo pad de 3V3 y uno de GND, y serían 3–4 cables por pad. Carlos pidió el mínimo tamaño; la stripboard de ~25 × 12 mm cumple.
- **Montaje HSW:** se descartó el inserto atornillado (a Carlos no le convence) y se eligió el conector `3dprint` integrado (resorte, probado por él). Consecuencia: la pieza que lo lleva se imprime de pie.
- **Número de piezas:** propuse 2 (frente como cáscara + trasera plana). Carlos propuso 3 (tapa trasera de pie / caja / tapa de pantalla) y **corrigió un error mío**: yo había dicho que no se podía atornillar por detrás, pero sí se puede, porque se arma antes y después se encaja en la rejilla. Se adoptaron sus 3 piezas y 4 tornillos M3 pasantes (un solo juego).

**Pendientes:** revisión de la especificación por Carlos; mediciones (botón, LCD, PCF, conexiones, tornillería); plan de implementación.

### 2026-09-25 (noche) — Plan de la fase 1 y pieza de prueba de la tapa trasera

**Objetivo:** montar la base de código CAD y generar la primera pieza física: la tapa trasera de prueba con los 2 conectores HSW.

**Qué se hizo:**
- Plan: `docs/superpowers/plans/2026-09-25-fase1-tapa-trasera-hsw.md`. Ejecutado aquí mismo (Tasks 1–3), con git inicializado (rama `main`).
- `cad/cq_utils.py` (export STL+STEP con el mismo numeral), `cad/stl_ref.py` (lector de STL con numpy), `cad/parameters.py`, `cad/hsw_connector.py` (clon paramétrico del conector `3dprint`: extrusiones con taper, sin loft), `cad/tapa_trasera_prueba.py`. 15 tests en verde.
- Export: `output/tapa_trasera_prueba_1.stl` / `.step` (placa de 90 × 30 × 4 mm, conectores a ±20.44 mm, a ras de la cara de la cama).

**Hallazgo (corrige lo que se había dicho en la sesión anterior):** al medir el conector en detalle se vio que la **base es el extremo de la U cerrada**, no la placa de 2.7 mm. Esa placa es la punta (tiene chaflán de entrada) y se engancha detrás del panel. Consecuencias: la pieza queda **separada 6.4 mm** de la cara del panel; el conector va **a ras del borde que apoya en la cama**; las cabezas M3 caben en ese hueco sin avellanar (especificación, D-11 actualizada). El clon da −1.3% de volumen contra el STL; solo se omitieron las pestañas de adherencia de 0.5 mm.

**Pendientes:** Carlos revisa en Onshape, imprime de pie (borde de los conectores sobre la cama) y prueba en la pared: entrada simultánea en 2 celdas, retención, paralelismo con la pared, y orientación (conectores en el borde superior vs inferior).

---

### 2026-09-25 (noche, 2) — Revisión en Onshape de la tapa: v2

**Observaciones de Carlos sobre `tapa_trasera_prueba_1`:**
1. Al conector le faltaba la "base" inferior: la **pestaña de 0.5 mm de la primera capa**, por dentro de cada brazo (de la punta hasta la placa B, terminando en una rampa de 30°). Sirve para imprimir sin brim y limpio. Yo la había omitido a propósito, pensando que era irrelevante: fue un error de criterio, porque es funcional para la impresión.
2. El puente de 1 mm de la base del conector quedaba afuera; puede ir **embebido en la tapa**. Es más estético.
3. La separación entre conectores (40.88 mm) está perfecta.

**Qué se hizo:** se agregaron `CONN_FOOT_*`, `CONN_EMBED` y `TAPA_STANDOFF` a `parameters.py`; la pestaña va en `hsw_connector.py`; `connector_placed` ahora embebe el puente. El clon difiere del STL en −0.6% de volumen (antes −1.3%). 17 tests en verde. Export: `output/tapa_trasera_prueba_2.stl/.step`.

**Consecuencia:** la tapa queda separada **5.4 mm** del panel (antes 6.4). Las cabezas M3 DIN 912 (3 mm) siguen cabiendo.

**v3 (mismo día), pedido de Carlos para facilitar la impresión:**
- **Redondeo cóncavo r = 1.0 mm** entre la cara superior de la pestaña y la cara interior del brazo (`CONN_FOOT_FILLET_R`), recortado al contorno de la pestaña. Al principio entendí que el redondeo iba en la raíz del brazo contra la tapa, y le advertí que ahí endurecería el resorte (~15% con r = 0.5, ~35% con r = 1.0, porque la rigidez crece con el cubo del largo libre de 5.4 mm). Carlos aclaró que era la esquina pestaña-brazo, que no afecta al resorte.
- **Chaflán de 45° de 0.4 mm** (`BED_CHAMFER`) en las aristas de la placa que tocan la cama, contra el pie de elefante. Carlos pidió un redondeo y se acordó chaflán: un redondeo en la arista de la cama es casi horizontal en las primeras capas (voladizo), mientras que un chaflán de 45° se sostiene solo. **No se aplica al conector**: su pestaña y sus caras planas definen el apoyo y el ajuste. Complemento: "Elephant foot compensation" de Bambu Studio.
- 19 tests en verde. Export: `output/tapa_trasera_prueba_3.stl/.step`.

---

### 2026-09-25 (tarde-noche, 3) — Orden de etapas, guía eléctrica, YAML v1 y diagrama de la tira

**Objetivo:** mientras Carlos imprime la tapa de prueba, dejar lista la etapa 2 (armado eléctrico y mediciones) para hacerla esa misma noche.

**Qué se hizo:**
- Carlos propuso armar primero la parte eléctrica para modelar la caja con medidas reales. Se acordó el orden (D-13) y quedó en la especificación §8 (nueva §6.1 de mediciones del conjunto armado) y en la hoja de ruta del plan.
- Guía de banco `docs/fase2-armado-electrico.md`: mapa de pines, materiales, tira de bus, cableado del Wemos, CAT6, prueba funcional, mediciones y cambios al YAML.
- Revisión del YAML de la protoboard (pines confirmados: sensores D2/D1, LCD D6/D5, botón D7; ninguno es pin de arranque). Se generó `esphome/bmetesting_1.yaml` (versión 1, con encabezado de versión dentro del archivo), validado en sintaxis y estructura con PyYAML (ESPHome no está instalado en esta máquina).
- Diagrama `docs/img/tira_bus_3.png`, generado por `docs/img/tira_bus.py` (versionado con `cq_utils`). Conexiones marcadas con números y leyenda; solo los puentes A/B se dibujan como líneas. El borrador `_1` se borró porque los cables dibujados cruzaban otras tiras y parecían conexiones; la `_2` salió con los marcadores de la leyenda recortados por el límite de los ejes.
- Permisos del proyecto: `Bash(git *)` permitido; `git push --force/-f`, `git reset --hard` y `git clean` quedan en "ask" (Carlos estuvo de acuerdo).
- Skill global `cierre-dia` (fuera del proyecto, `~/.claude/skills/`): se agregó el commit local de cierre. Documentado en `~/.claude/extras.md`.
- `externalfiles/grid1.step` (fragmento de rejilla HSW que Carlos usa en Onshape como referencia de montaje; útil para simulación) agregado a `.gitignore`.

**Decisiones:**
- **D-13 — Orden: etapa 1 tapa → etapa 2 eléctrica + mediciones → distribución final.** Alternativa: modelar la caja con cotas nominales. Razón: la caja depende de medidas que hoy son estimaciones (tira, Wemos con cables, Dupont, USB); medir el conjunto real evita reimprimir. Los cables se sueldan con 10–15 cm de sobra y se recortan después de modelar la distribución.
- **D-14 — Direcciones: 0x76 = ambiente (SDO→GND en la tira), 0x77 = filamentos (SDO→3V3 en la cápsula); la inconsistencia se corrige en el YAML.** El YAML de la protoboard tenía las etiquetas invertidas respecto al brief. Alternativa: cambiar el hardware para ajustarlo al YAML. Razón: corregir el software no cuesta nada, y el hardware queda como dice la guía.
- **D-15 — Backlight: `restore_mode: ALWAYS_OFF`, se enciende al arrancar (`on_boot`, prioridad -100) y se apaga sola con un script `mode: restart` tras `backlight_timeout` (30 s).** Implementa D-08. Se mantuvo el nombre del dispositivo `bmetesting` para no romper el OTA ni Home Assistant; `api`/`ota` quedan sin clave, como estaban.
- **D-16 — Placa de bus de 6 tiras (no 4) y CAT6 soldado directo; la bornera solo va en la cápsula.** Alternativa: bornera en la tira. Razón: las borneras de paso 5.08 mm no caen en tiras vecinas de paso 2.54 mm. Alternativas válidas si hicieran falta: bornera de paso 2.54, o una perfboard con cada tira unida por un alambre desnudo (Carlos la considera si no tiene stripboard).

**Problemas y solución:**
- Un comando de shell quedó bloqueado esperando entrada (un `cat` sobrante): se detuvo y la edición se hizo con la herramienta de edición.
- En el diagrama, la leyenda se recortaba por el límite inferior de los ejes: se ajustó `ylim` a la altura real de la leyenda.

**Riesgo anotado (sin cambios):** el PCF8574 trae pull-ups a 5V en su bus, conectado a D6/D5 del ESP8266, que no está garantizado para 5V. En la protoboard funcionó; si el LCD falla de forma intermitente, empezar a revisar por ahí.

**Archivos:** `docs/fase2-armado-electrico.md`, `esphome/bmetesting_1.yaml`, `docs/img/tira_bus.py`, `docs/img/tira_bus_3.png` (nuevos); especificación (§6.1, §8, D-05), plan (hoja de ruta), `CLAUDE.md`, `.gitignore`.

**Pendientes:**
- Etapa 1: imprimir `tapa_trasera_prueba_3` y probarla en la pared (4 puntos).
- Etapa 2: armar la tira según el diagrama, soldar con cables largos, preparar el CAT6 y la cápsula, instalar `bmetesting_1.yaml`, hacer la prueba funcional y medir (guía §7).

---

### 2026-10-13 — Placa soldada por Carlos y tapa de prueba v3 mandada a imprimir

**Objetivo:** retomar el proyecto, ordenar los pendientes y mandar a imprimir la tapa de prueba.

**Qué se hizo:**
- Carlos soldó la electrónica en casa, sobre **una sola placa de ~64 × 64 mm** (medida de memoria, por confirmar) con todas las conexiones, en lugar de la tira de bus de 6 tiras. La placa queda atrás con el Wemos; al frente quedan la pantalla y un **botón grande** para encender y apagar. El conjunto se quedó en casa: no hay medidas ni fotos todavía.
- Posición recordada, sin confirmar: Wemos de un lado, debajo de la pantalla; BME de ambiente del lado opuesto, "debajo del botón".
- Lista de pendientes para WhatsApp (traer el conjunto, medir y fotografiar, prueba funcional, prueba de la tapa en la pared) más un bloque extra para el BME de ambiente.
- Revisión de `externalfiles/3mfs/tapa_trasera_prueba_3.3mf` y del laminado `tapa_trasera_prueba_3.gcode.3mf` (Bambu Studio 02.02.00.68): pieza de pie, 90 × 30 mm de alto, con el borde de los conectores y el chaflán sobre la cama. Carlos la mandó a imprimir.

**Decisiones:**
- **D-17 — La electrónica va en una sola placa de ~64 × 64 mm con el Wemos montado; sustituye a la tira de 6 tiras de D-05/D-16.** Decisión de Carlos al soldar. Alternativa: la tira de bus de 6 tiras de `docs/img/tira_bus_3.png`. Razón: disponibilidad, era la placa que Carlos tenía a la mano. Consecuencia: la placa pasa a ser la pieza que manda en el fondo y la distribución de la caja; el diagrama de la tira queda como referencia histórica del conexionado.

**Problemas y solución:**
- El 3MF tenía el brim en "Auto" (5 mm, separación 0.1 mm) y propuse pasarlo a "No brim" para no ensuciar los brazos del conector. Carlos laminó y vio que no se generaba; el G-code lo confirma (sin trazos de brim ni de soporte). No se cambió nada.
- El laminado trae la advertencia `bed_temperature_too_high_than_filament` (cama a 70 °C con el perfil "Generic PETG - Copy"). Se dejó como está.

**Parámetros de la impresión:** P1S, boquilla 0.4, perfil "0.20mm Strength @BBL X1C", capa 0.2 mm, 4 paredes, relleno 7 % en rejilla, PETG a 255 °C, cama texturizada a 70 °C, Elephant foot compensation 0.15 mm, sin soportes, filamento de la ranura 2. Laminado: 150 capas, 45 min 5 s, 16.25 g (5.32 m). Con capas de 0.2 mm, la pestaña de 0.5 mm del conector sale de 0.4 o 0.6 mm.

**Riesgo anotado:** el BME de ambiente quedó en la misma placa que el Wemos. D-03 pedía aislarlo del calor; falta confirmar qué lado queda arriba con la caja colgada y medir el sesgo real.

**Inventario:** no se registró el consumo de PETG (16.25 g + 10 %) porque el inventario no tiene carretes dados de alta; tampoco están los componentes soldados (Wemos, BME280, LCD, PCF8574, placa).

**Archivos:** `externalfiles/3mfs/tapa_trasera_prueba_3.3mf` y `tapa_trasera_prueba_3.gcode.3mf` (nuevos, de Carlos); `docs/bitacora.md` y `CLAUDE.md`.

**Pendientes:**
- Probar la tapa impresa en la pared (4 puntos: entrada en 2 celdas, retención y salida, paralelismo, conectores arriba vs abajo).
- Traer el conjunto soldado; medir y fotografiar: placa (largo, ancho, espesor), altura con el Wemos, posición del Wemos y salida del USB, LCD, backpack, botón (cuerpo, rosca, fondo), BME, salida del CAT6.
- BME de ambiente: qué lado va arriba, distancia al Wemos, si va soldado directo o en header, y prueba de sesgo (los 2 BME juntos, 30 min encendido, comparar temperaturas; criterio propuesto: hasta ~0.5 °C basta con pared divisoria y rejilla).
- Confirmar si el botón es momentáneo o con enclavamiento (el YAML v1 asume pulso y apagado a los 30 s).
- Prueba funcional con `esphome/bmetesting_1.yaml` (0x76/0x77/0x27, backlight, CAT6).

---

### 2026-10-14 — Prueba de la tapa OK, mediciones reales y distribución de la carcasa (fase 2)

**Objetivo:** registrar la prueba de la tapa, medir el conjunto soldado y modelar la distribución de la carcasa con medidas reales.

**Qué se hizo:**
- Prueba de `tapa_trasera_prueba_3` en la pared: entra algo rígida pero bien; retención, salida y paralelismo correctos. Conectores **arriba**.
- Mediciones de Carlos (calibrador): placa **50 × 50 × 1.0** (no 64 × 64), 4 barrenos Ø2.95 a 45.17 entre centros (42.22 de orilla a orilla); pines del Wemos 4.5 por abajo; USB sobresale 2.2 con su centro a 17.6 del borde; plástico de los pines del Wemos 3.44; Wemos 6.8 sobre la placa; cable más alto 8.0; cabezal hembra de 8 pines (BME) de 8.5, primer pin a 4.89 del borde del USB y a 3.50 del borde superior. LCD: placa 80 × 36.24 × 1.6; barrenos Ø3 a 75.0 × 31.15 entre centros; marco 71 × 24 a 4.92 (izq.) / 5.33 (arriba), sobresale 7.18; área visible 64.53 × 14.12 a 2.70 / 4.24 del marco; módulo I2C hasta 9.81 detrás; conector derecho ~5 fuera del borde, centro a 11.6 del borde inferior, hasta 9.55 detrás; los Dupont hacen una curva suave de ~20. Botón táctil 12 × 12 **momentáneo**: cuerpo 3.18, total con tapa 8.82, tapa 10 × 10, recorrido ~0.4.
- Prueba funcional sin el sensor remoto y con el YAML viejo (sin apagado automático): funcionó.
- El BME local trae 0x76 por defecto con CSB y SDO sin conectar: bastan 4 hilos.
- Inventario consultado (sin cambios): M3 hasta ×25; insertos M3×4×4.2 y M2.5×4×3.5; tornillos M2.5 de ×3 a ×8.
- Plan `docs/superpowers/plans/2026-10-14-fase2-distribucion-carcasa.md`, ejecutado con subagentes (una revisión por tarea + revisión final). Código nuevo: `geom.py`, `components.py`, `tapa_trasera.py`, `caja_trasera.py`, `caja_delantera.py`, `boton.py`, `ensamble.py`, `prueba_frente.py`, `prueba_boton.py` y sus tests (60 en verde).
- Revisión de Carlos en Onshape (`ensamble_2`): ventana más grande, placa detallada, sujeción del botón y rejillas. Todo aplicado, revisado y reexportado.
- Rama `fase2-distribucion` unida a `main` (avance directo) y borrada; todo solo local.
- Reglas nuevas en `CLAUDE.md` (la de preguntas numeradas también en `~/.claude/CLAUDE.md`): preguntas numeradas y salida mínima en el chat.

**Decisiones:**
- **D-18 — Dos cajas separadas por profundidad:** caja trasera (placa + Wemos) y caja delantera (LCD, botón y BME abajo); la divisoria es el fondo de la caja trasera. Idea de Carlos. Alternativa: compartimento inferior con ranura (D-03/D-04, superadas). Razón: el Wemos y el BME no comparten compartimento; el BME sobresalía solo 5.9 mm de la placa y su chip quedaba ~1.7 mm del lado caliente.
- **D-19 — Dos juegos de 4 M3×8** (A: delantera ↔ trasera, desde dentro de la caja trasera; B: tapa ↔ trasera, desde atrás) en lugar de 4 pasantes (D-11, superada). Alternativa: comprar M3×50. Razón: el M3 más largo del inventario es de 25 mm.
- **D-20 — El marco del LCD atraviesa el frente y queda a ras;** ventana = marco + 0.3 por lado, centrada en el marco. Alternativa: ventana al ~90 % del marco con el LCD detrás. Razón: mejor ángulo de visión; la caja pierde 2.4 mm de fondo.
- **D-21 — El BME sale del cabezal con un cable propio** (pines macho rectos doblados a 90° + cabezal hembra). Alternativas: Dupont recto (+~11 mm de fondo) o soldar directo (sin desconexión). Lo más alto de la placa queda en 12.5.
- **D-22 — Sujeción del botón por prueba física:** 3 variantes en `prueba_boton` (1 clip, 2 presión, 3 ambas). Alternativas: poste desde la divisoria (no se imprime: es la cara sobre la cama) y retenedor atornillado (respaldo).
- **D-23 — Rejillas hexagonales:** caja delantera en la franja baja del frente y en las paredes inferior y superior; caja trasera en las paredes inferior y superior (chimenea). Alternativa: rejilla en la tapa trasera (sale al hueco de 5.4 mm, poca circulación).

**Problemas y solución:**
- El STL del Wemos parecía más alto: trae tiras de pines hembra arriba que el de Carlos no tiene. Con el plástico de 3.44, el centro del USB queda a ~6.2 sobre la placa (antes se estimaba 5.4).
- La revisión final pidió 0.2 de holgura del marco del LCD contra el frente; después quedó sustituida por D-20.
- El clip del botón deformaba ~3.4 % al entrar y su holgura era menor que una capa. Se corrigió: rampa a 45°, ceja de 0.25, brazo de 0.8, holgura de 0.2 (~2 %); pared y aletas terminan 1 mm antes de la base para dejar libres las patas (van hacia arriba y abajo).

**Parámetros definidos:** exterior **98.8 × 86.04 × 49.49** mm (+ conectores); `Y_DIV0=25.5`, `Y_DIV1=27.9`, `Y_FRONT=49.49`; `PCB_TOP_H=12.5`; `USB_W=6.17`; `LCD_WIN_CLEAR=0.3`; `LCD_INSERT_DEPTH=5.0`; `M25_INSERT_DEPTH=6.0`; `BTN_MOUNT="clip"` (provisional); `CLIP_LIP=0.25`, `CLIP_T=0.8`, `CLIP_GAP=0.2`, `BTN_LEG_FREE=1.0`; `HEX_F2F=3.5`, `HEX_RIB=1.2`; columnas M3 Ø8 a `BOSS_X=42.5`.

**Archivos:** `cad/` (los de arriba más `parameters.py` y `cq_utils.py`), especificación (D-18 a D-23, §6.2), plan de la fase 2, `CLAUDE.md`. Exportados (no versionados): `tapa_trasera_1`, `caja_trasera_2`, `caja_delantera_4`, `ensamble_4.step`, `prueba_frente_4`, `prueba_boton_2`.

**Lecciones:**
- Antes de proponer un soporte, revisar en qué cara de impresión nace (el poste desde la divisoria era imposible).
- Los STL de componentes de terceros pueden traer piezas que el real no tiene; contrastarlos con una medida de Carlos.

**Pendientes:**
- Carlos imprime `prueba_boton_2` (elegir variante → `BTN_MOUNT`) y `prueba_frente_4` (insertos M2.5 en postes de paredes de ~1 mm, marco a ras, cabezal de 16 pines).
- Medir el sobremolde del cable micro-USB (se usa 12 × 8).
- Prueba funcional completa con `bmetesting_1.yaml` y el sensor remoto.
- Fase de detalles: soporte del BME, ruta del cable del BME (cabezal abajo a la izquierda → paso de la divisoria arriba a la derecha), alivio del USB, salida del CAT6, sellado del paso de cables, chaflán de ventanas, labio que centre las cajas, topes inferiores de la tapa si hacen falta; orejas de brim al imprimir la tapa de 86 mm de pie.

### 2026-10-15 — Pruebas del frente y del botón; carcasa compacta de 96 × 60

**Objetivo:** probar `prueba_frente_4` y las pruebas del botón, y ajustar la carcasa al lugar donde va (máx. 100 mm de ancho).

**Qué se hizo:**
- `prueba_frente_4`: el LCD entra bien y queda a ras con la holgura de 0.3; el marco a ras se conserva. Los insertos M2.5 entran, pero si se calientan de más el poste (pared de ~1 mm) se reblandece y se tuerce. Se probó 1 solo inserto en los 4 postes y se recuperó (consumo 0 en el inventario). El cabezal de 16 pines libra los postes; del lado del conector el espacio queda muy justo (Dupont + cable doblado sin forzar = 15 mm de lado).
- Botón: en `prueba_boton_2` solo entró la variante 1 (clip); "presión" y "ambas" no entraron. `prueba_boton_3` (ceja 0.40/0.55/0.70, brazo 0.8/0.7/0.6) mejoró pero le faltaba agarre. En `prueba_boton_4` (ceja 0.85/1.0/1.15, brazo 0.6) se rompieron las 3. En `caja_delantera_5`, el clip de 0.70/0.6 sostiene el botón sin pegamento.
- Ancho: se probó 116.8 (+9 por lado, simétrico), pero el lugar donde va la caja mide 100 mm y la de 98.8 ya entraba justa. Se quedó en **96.0**, con los pines del I2C del LCD doblados hacia atrás (nada sobresale de lado; Dupont: 8.5 hacia adentro del borde y 20 detrás de la placa verde).
- Alto: de 86.04 a 68.04 (botón y BME en la misma fila) y después a **60.04**, al mover las columnas del juego A. Ahora el límite es la caja delantera; la caja trasera queda con 2.7 mm sobre la placa de 50.
- `caja_delantera_5` impresa en PETG rojo: el tamaño cabe en el lugar y se ve bien; el rojo se queda. Los barrenos del LCD quedaron ~2 mm arriba de los postes; el BME entra en sus pines; el Dupont del LCD queda justo, pero se ve bien.
- Rejilla del frente revisada con PNG (`frente_hexagonos_1..3.png`): se agregaron columnas laterales, una fila arriba y una fila arriba del botón.
- `caja_delantera_6` exportada y mandada a imprimir. Commit `f5e718a` a medio día.

**Decisiones:**
- **D-24 — Ancho de 96: pines del I2C del LCD doblados hacia atrás**, con el Dupont pasando a la caja trasera por una ventana en la divisoria (~10.5 × 12). Alternativas: ensanchar los 2 lados a 116.8 (no cabe en 100), ensanchar solo el lado derecho (ventana descentrada), soldar el cable directo (sin desconexión), caja asimétrica de ~96 (cable apretado y ventana corrida ~4 mm). Razón: máximo de 98 (Carlos: mejor 96) y ventana centrada.
- **D-25 — Botón y BME en la misma fila bajo el LCD, con márgenes de 2 arriba y abajo.** Alternativa: zona propia del BME abajo (86 de alto). Razón: había mucho espacio perdido (idea de Carlos).
- **D-26 — Columnas del juego A cortas, medio embebidas en las paredes laterales** (centro a 3.0 de la cara interior), en las esquinas tocando piso y techo, de solo lo que pide el inserto desde la divisoria y con su cara hacia el frente a 45°. Juego B a ±15. Alternativa: columnas de esquina a 4.5 de las paredes y de largo completo (exigían 9 mm arriba del LCD y tapaban el frente). Razón: libera alto y deja el frente libre para la rejilla. Supone 2 mm libres detrás de las orillas izq./der. de la placa verde (confirmado por Carlos).
- **D-27 — Postes del LCD en cono, de Ø11 junto al frente a Ø8 en la punta,** recortados contra el marco + 0.3. Alternativa: Ø5.6 (pared de ~1 mm, se deforma con el cautín). Pared mínima: ~1.1 en el poste de arriba a la derecha, hacia la esquina del marco.
- **D-28 — Botón: clip con ceja de 0.70 y brazo de 0.6, sin pegamento** (cierra D-22). Alternativas: presión y "ambas" (no entraron), ceja de 0.85 a 1.15 (se rompió), pines remachados, placa de retención, clip + pegamento. Razón: en la caja real sostiene sin pegamento.
- **D-29 — BME sobre 2 escalones de 2 mm con pin de Ø2.5** en sus barrenos de 2.8 (sobresale 3 mm, remachable con el cautín). Alternativa: tornillo. Razón: sin tornillería; los pines crecen derechos al imprimir boca abajo.
- **D-30 — Rejilla del frente:** toda la zona bajo la ventana con 3 mm de margen; columna en zigzag de 5 por lado (a 2.2 de la orilla); 5 arriba de la pantalla; 3 arriba del botón (a ~1.4 de la ventana). Hexágono de 3.5; 47 en total; se saltan los que caerían bajo el botón, los escalones del BME o la base de los postes. Alternativas: 2 franjas a los lados del botón (poca rejilla), hexágono de 3.0 o 2.5, columnas pegadas a la pantalla (opción B). Razón: estética (Carlos).
- **D-31 — CAT6 por una muesca en la pared superior de la caja trasera, al centro,** abierta hacia la tapa (Ø5.5 + 0.4 por lado); alivio de tensión con un cincho apretado al cable por dentro. Conector de 90° delgado sobre 6 pines al centro de la orilla de la placa opuesta al USB. Alternativa: barreno cerrado (el cable tendría que pasar antes de ponerle el conector). Razón: se arma y desarma sin cortar ni volver a crimpar el cable (confirmado por Carlos).

**Problemas y solución:**
- Barrenos del LCD ~2 mm arriba de los postes: el marco se había medido a 5.33 del borde de arriba; lo real es 6.60 arriba y 5.40 abajo. `LCD_BEZEL_TOP = 6.72` (alto de 24.0 centrado donde lo dicen las 2 medidas); la ventana bajó ~1.4 y el LCD y sus postes no se movieron.
- Con la nueva altura, el paso de cables de la divisoria cortaba un poste de la placa y la caja trasera salía en 2 sólidos: se movió a la izquierda de la placa (8 × 14, centro en X = −30.5).
- `ensamble_8` tenía las 2 franjas de rejilla disparejas: los huecos bajo los escalones del BME ahora se quitan también en espejo.
- En `prueba_boton_4` los brazos de 0.6 se rompieron con flexión ≥ ~4.8 %: el brazo crece vertical y se abre entre capas.

**Parámetros definidos:** exterior **96.0 × 60.04 × 49.49** mm; `LCD_SIDE_GAP=5.6`; `TOP_MARGIN=2.0`; `BOTTOM_MARGIN=2.0`; `LCD_BEZEL_TOP=6.72`; `LCD_POST_D=8.0`, `LCD_POST_BASE_D=11.0`, `LCD_POST_BEZEL_CLEAR=0.3`; `LCD_CONN_T=8.5`, `LCD_CONN_BACK=20.0`, `LCD_BACK_EDGE_FREE=2.0`; `DIV_LCD_WIN_CLEAR=1.0`; `BOSS_SIDE_INSET=3.0` (`BOSS_X=42.6`), `A_BOSS_Z=(6.4, 53.64)`, `B_BOSS_DZ=15.0`, `A_COL_CAP=1.0`; `CLIP_LIP=0.70`, `CLIP_T=0.6`; `BME_L=15.2`, `BME_W=11.5`, `BME_PCB_T=1.5`, `BME_HOLE_D=2.8`, `BME_HOLE_PITCH=10.15`, `BME_STANDOFF_D=4.6`, `BME_PIN_CLEAR=0.15`, `BME_PIN_OUT=3.0`; `CAT6_D=5.5`, `CAT6_CLEAR=0.4`; `DIV_SLOT_W=8.0`, `DIV_SLOT_H=14.0`; `FRONT_VENT_MARGIN=3.0`, `SIDE_VENT_N=9`, `TOP_VENT_N=5`, `BTN_VENT_N=3`.

**Archivos:** `cad/parameters.py`, `caja_delantera.py`, `caja_trasera.py`, `components.py`, `geom.py` (`cone_y`), `boton.py`, `prueba_boton.py`, `prueba_frente.py` y sus tests (65 en verde); `CLAUDE.md`. Exportados (no versionados): `ensamble_5` a `ensamble_13`, `prueba_boton_3`, `prueba_boton_4`, `caja_delantera_5`, `caja_delantera_6`, `frente_hexagonos_1..3.png`.

**Lecciones:**
- Un brazo flexible impreso vertical (se abre entre capas) en PETG aguantó ~4.4 % de flexión y se rompió desde ~4.8 %: para más agarre, no alargar la ceja sobre el mismo brazo.
- Al medir el desfase de un elemento (marco del LCD), pedir las 2 distancias (arriba y abajo): la suma contra el total detecta si se midió desde el borde equivocado.

**Pendientes:**
- Carlos revisa `caja_delantera_6`: barrenos del LCD contra los postes e insertos M3 de las columnas del juego A.
- Regenerar la caja trasera y la tapa con 96 × 60 e imprimirlas; confirmar el espacio del Dupont del LCD.
- Pasar D-24 a D-31 a la especificación de diseño.
- Medir el sobremolde del cable micro-USB; prueba funcional completa con `bmetesting_1.yaml` y el sensor remoto.
- Detalles: alivio del USB, sellado del paso de cables, chaflán de ventanas, labio que centre las cajas y topes de la tapa si hacen falta.

### 2026-10-16 — Revisión de `caja_delantera_6`; caja trasera y tapa a 96 × 60

**Objetivo:** revisar la caja delantera impresa, regenerar la caja trasera y la tapa con 96 × 60 y pasar D-24 a D-31 a la especificación.

**Qué se hizo:**
- `caja_delantera_6` impresa: los barrenos del LCD ya caen sobre los postes. Con los pines de 3 mm el BME queda mejor y deja lugar para una gota de silicón encima. Los insertos M3 del juego A se prueban en la noche (no bloquean: si cambia `INS_M3_HOLE_D` solo se regenera).
- Caja trasera y tapa regeneradas con 96 × 60 (`caja_trasera_3`, `tapa_trasera_2`, `ensamble_14`).
- Carlos revisó `caja_trasera_3` en Onshape: la ventana del Dupont del LCD quedaba ~13 mm abajo y el paso de cables del BME, muy arriba. Con medidas tomadas en la caja real se regeneró `caja_trasera_4` / `ensamble_15`. Carlos la aprobó y la manda a imprimir sola; la tapa (`tapa_trasera_2`, sin cambios) se imprime después si la caja funciona.
- Se verificó que el código actual de la caja delantera da exactamente el mismo sólido que `caja_delantera_6` (mismo volumen, traslape del 100 %): la caja trasera nueva es compatible con la impresa.
- D-24 a D-32 pasadas a la especificación de diseño (D-22 marcada como cerrada por D-28; piezas y vista lateral al día). Comentarios de `OUT_H` (60.04) e `IN_H` (55.24) corregidos en `parameters.py`.
- Sin consumos de inventario en esta sesión (decisión de Carlos).

**Decisiones:**
- **D-29 (ajuste)** — El BME se fija con una gota de silicón sobre los pines, **sin remachar**. Alternativa: remachar con el cautín. Razón: queda firme y se quita si hay que cambiar el sensor.
- **D-32 — Paso de cables del botón y del BME abajo**, a 1.5 del piso interior (z 3.9–17.9), en la misma X (centro en −30.5, a la izquierda de la placa). Alternativa: centrado en el alto (z 23–37). Razón: queda a la altura del BME (z ≈ 10.4) y del botón; más a la derecha no cabe porque ahí empieza la placa.

**Problemas y solución:**
- Ventana del Dupont del LCD ~13 mm abajo: `LCD_CONN_ZC = 11.6` se había contado desde el borde equivocado de la placa verde (contado desde arriba coincide con los 8.75 que midió Carlos). Se reemplazó por la posición medida en la caja con el LCD montado: de 8.75 a 25 del techo interior, borde a 14.0–14.2 de la cara interior de la pared lateral, ~10 de ancho. El Dupont queda a 0.6 del poste superior de la placa y a 1.2 de la placa; ya no choca con la columna superior del juego B (> 7 mm).

**Parámetros definidos:** `LCD_CONN_TOP0=8.75`, `LCD_CONN_TOP1=25.0`, `LCD_CONN_SIDE=14.0`, `LCD_CONN_W=10.0` (sustituyen a `LCD_CONN_T`, `LCD_CONN_H` y `LCD_CONN_ZC`); `DIV_SLOT_FLOOR=1.5` (`DIV_SLOT_ZC=10.9`).

**Archivos:** `cad/parameters.py`, `cad/components.py` (`lcd_cable_box`), `cad/test_components.py` (65 en verde); `docs/superpowers/specs/2026-09-25-carcasa-monitor-design.md`; `CLAUDE.md`. Exportados (no versionados): `caja_trasera_3`, `caja_trasera_4`, `tapa_trasera_2`, `ensamble_14`, `ensamble_15`.

**Lecciones:**
- Otra vez una cota contada desde el borde equivocado (como el marco del LCD el 2026-10-15): la posición de un conector se mide mejor en la caja real con la pieza montada, desde las caras interiores, que sobre el componente suelto.

**Pendientes:**
- Carlos imprime `caja_trasera_4` y prueba: unión con la delantera (juego A), placa en sus postes, Dupont por su ventana, cables del botón y del BME, cable USB (sobremolde aún nominal 12 × 8).
- Carlos prueba los insertos M3 en las columnas del juego A (Ø4.0).
- Si la caja trasera funciona, imprimir `tapa_trasera_2`.
- Medir el sobremolde del cable micro-USB; prueba funcional completa con `bmetesting_1.yaml` y el sensor remoto.
- Detalles: alivio del USB, sellado del paso de cables, chaflán de ventanas, labio que centre las cajas y topes de la tapa si hacen falta. Después: cápsula remota.

### 2026-10-16 (noche) → 2026-10-19 — Armado de las cajas, tapa avellanada, repo en GitHub y firmware v2

**Objetivo:** armar las cajas impresas, preparar la tapa final, publicar el proyecto en GitHub y ajustar el firmware tras la prueba de varios días.

**Qué se hizo:**
- PNG de armado con el mapa de insertos y tornillos por hueco: `output/insertos_caja_trasera_1.png` y `output/insertos_caja_delantera_1.png` (vista desde el lado abierto).
- Carlos armó `caja_delantera_6` + `caja_trasera_4`: todo cabe y el USB embona bien (sale directo hacia abajo).
- Inventario (repo `inventario`, commit 615b10d): consumo de 8 INS-M3x4x4.2, 8 INS-M2.5x4x3.5, 8 TOR-M3x8 y 8 TOR-M2.5x6-negro (medidorTHR). INS-M2.5x4x3.5 ajustado a 5 por conteo físico (los faltantes probablemente se usaron en pruebas sin registrar). Sin mínimo. No se registra filamento todavía (decisión de Carlos).
- Tapa: barrenos del juego B con avellanado de 90° → `tapa_trasera_3` / `ensamble_16` (D-33). Impresa y validada: las cabezas asientan bien. La carcasa quedó **colgada en la pared HSW**, con el montaje validado con la tapa final.
- Lecciones 3 a 6 agregadas a la sección 4 de esta bitácora; la versión general, en `~/.claude/extras.md`.
- Repo remoto privado: github.com/quilofucar-web/Temp_TH_tester_wemos (rama `main` con todo el historial). Se suben también `output/ensamble_16.step` (forzado sobre el `.gitignore`), `externalfiles/3mfs/carcasa_completa_1.3mf` (la cama de Carlos con las 3 piezas vigentes; se había guardado encima de `tapa_trasera_prueba_3.3mf`, que volvió a su versión anterior) y `README.md` (estado, BOM y resumen).
- Prueba continua del 2026-10-16 al 10-19: la humedad coincide con otros medidores de Carlos; la temperatura difiere ~1 °C. Se deja sin offset (D-35).
- El firmware instalado no era la v1 (no apagaba la luz). Carlos pasó el YAML instalado: el bus de sensores tiene SDA = GPIO5 (D1) y SCL = GPIO4 (D2), así quedó soldada la placa; las direcciones no cambiaron. Se creó `esphome/bmetesting_2.yaml` (D-36), instalado por Carlos; desde HA, el switch "Luz LCD" se apaga solo a los 30 s.
- El LED rojo del módulo PCF8574 es de encendido y está fijo a 5 V: no se apaga por software (quitarlo o cubrirlo).

**Decisiones:**
- **D-33 — Avellanado de 90° en los barrenos del juego B de la tapa**: boca Ø6.4 (`M3_CSK_D=6.0` + 0.2 por lado), 1.5 de profundidad, en la cara hacia el panel. Alternativa: barreno recto (la cabeza cónica sobresalía). Razón: los TOR-M3x8 son de cabeza cónica.
- **D-34 — Sensor remoto y cápsula, en pausa**: por ahora solo el sensor de ambiente. Razón: decisión de Carlos.
- **D-35 — Sin offset de temperatura**. Alternativa: `filters: offset` de ~−1 °C. Razón: decisión de Carlos; la humedad coincide (un BME 1 °C más caliente marcaría ~5–6 % menos), así que la diferencia parece del error propio del sensor (±1 °C) y no de calentamiento.
- **D-36 — Firmware v2**: fila 1 = ambiente; fila 2 = "Lun 19/10  14:35" (hora de HA) mientras no haya lecturas del 0x77; con el remoto vuelve a mostrar filamentos. `project` versión "2", visible en HA. Pines del bus de sensores según la placa real.
- **D-37 — Sin labio de alineación entre cajas ni nuevas versiones de la carcasa**: queda como está. Razón: ya funciona; Carlos no imprimirá otra versión (queda como lección).

**Problemas y solución:**
- Cabeza cónica de los M3×8 sobresalía de la tapa → avellanado (D-33).
- La luz no se apagaba sola → el Wemos tenía un YAML anterior a la v1; se instaló la v2.
- La guía de fase 2 dice SDA D2 / SCL D1, pero la placa quedó al revés → la v2 usa SDA GPIO5 (D1) y SCL GPIO4 (D2).

**Parámetros definidos:** `M3_CSK_D=6.0` (nominal DIN 7991, validado en la tapa impresa), `M3_CSK_CLEAR=0.2`.

**Archivos:** `cad/parameters.py`, `cad/tapa_trasera.py`, `cad/test_tapa_trasera.py` (66 en verde); `esphome/bmetesting_2.yaml`; `README.md`; `CLAUDE.md`; `docs/bitacora.md`; `externalfiles/3mfs/carcasa_completa_1.3mf`; `output/ensamble_16.step`. Exportados (no versionados): `tapa_trasera_3`, `insertos_caja_trasera_1.png`, `insertos_caja_delantera_1.png`.

**Pendientes:**
- Foto del medidor montado en la pared, para el README y el proyecto.
- Ver la fecha y la hora en la pantalla (v2).
- Opcional: quitar o tapar el LED rojo del PCF8574.
- Después: sensor remoto y cápsula (D-34).

---

## 4. Lecciones aprendidas

1. **Antes de descartar una opción por "no se puede acceder", preguntar por la secuencia de armado.** Descarté los tornillos por detrás suponiendo que la pieza se atornilla ya colgada; en una pared HSW, el conjunto se arma completo y después se encaja (2026-09-25).
2. **Al clonar una pieza probada, no omitir detalles "menores" sin preguntar.** La pestaña de 0.5 mm de la primera capa parecía accesoria, pero es la razón de que la pieza se imprima limpia sin brim (2026-09-25).
3. **La tornillería quedó sobrediseñada para una pieza que casi no carga** (Carlos, 2026-10-16). Se usaron 16 insertos y 16 tornillos. Hubiera bastado con:
   - **Placa:** 2 pines en diagonal (esquinas opuestas) más 2 tornillos en las otras 2 esquinas, en vez de 4 tornillos.
   - **Unión de cajas y tapa:** un labio o chaflán que las autoalinee, 2 pines cruzados que guíen el montaje y solo 2 tornillos por unión, en vez de 4. Se cumple la regla de ≥ 2 puntos y se ahorra hardware.
   - El labio que centra las cajas se quedó como "detalle si hace falta" y al final no se hizo. La alineación va desde la primera versión, no como corrección.
4. **El acabado se pensó al final y la caja quedó "cuadrada"** (Carlos, 2026-10-16). Redondear las esquinas verticales, chaflanes en casi todas las aristas y quizá fuzzy skin en las caras visibles la hubieran hecho ver más profesional. El acabado se define desde la arquitectura, porque cambia cotas y holguras.
5. **Definir el tipo de cabeza del tornillo antes de modelar sus barrenos.** La tapa salió con barreno recto y los M3×8 son de cabeza cónica: se corrigió con un avellanado de 90° en `tapa_trasera_3` (2026-10-16).
6. **Objetivo para los próximos diseños:** que salgan bien a la primera prueba y gastar menos material. Más análisis y piezas de prueba chicas antes de imprimir la pieza completa.
