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

### 2026-10-19 (tarde) — Repo público en GitHub

**Objetivo:** dejar el repo listo para hacerlo público, sin datos del trabajo ni archivos de terceros.

**Qué se hizo:**
- Revisión completa del repo:
  - Bloqueos: los 35 commits tenían como autor el correo corporativo; había 7 STL de terceros sin origen ni licencia registrados.
  - Detalles: mención del entorno corporativo en `CLAUDE.md`, `DesignerUserId` de Bambu en los 3MF y falta de `LICENSE`.
  - Sin problemas: secretos (WiFi por `!secret`), rutas de usuario, tamaño.
- Los 7 STL de `externalfiles/` salen del repo (`.gitignore`: `externalfiles/*.stl`); siguen en local. Los 2 tests que comparan el conector contra el STL original se saltan solos si falta (7 pasan y 2 se saltan sin él).
- Créditos (README y `cad/hsw_connector.py`):
  - Conector HSW: autor desconocido (letras "XYZ" en la cara trasera), reinterpretado; todos los derechos son de su autor y queda fuera de la licencia.
  - Componentes: modelos 3D de la biblioteca de EasyEDA, solo referencia, no incluidos.
  - Pared HSW: sistema de terceros, no incluida.
- `LICENSE` MIT con la excepción del conector. Se quitó la mención corporativa de `CLAUDE.md` y se borró el `DesignerUserId` de los 3 3MF.
- Historial nuevo en la rama `publico` (`git checkout --orphan`): 1 commit (`6fbafbc`) con autor `quilofucar@gmail.com`. Carlos borró el repo en GitHub y lo recreó público y vacío; se subió `publico` como `main`.
- Ramas locales: `main` = versión limpia enlazada a `origin/main`; `respaldo-historial-trabajo` = historial anterior, sin enlace a GitHub y **nunca se sube**.
- Git: `user.name` / `user.email` personales en el repo y como **globales** en la máquina. La causa del correo del trabajo: sin correo global, git lo armaba con el usuario de Windows y el dominio.
- Regla global agregada a `~/.claude/extras.md` (2026-10-19): nunca subir el correo ni datos del trabajo; checklist antes de publicar un repo.

**Decisiones:**
- **D-38 — Historial nuevo y repo recreado** en vez de reescribir `main` y hacer force push. Alternativa: `push --force` sobre el repo existente. Razón: GitHub conserva los commits viejos y muestra los force push en *Activity*; el `main` local se conserva como respaldo.
- **D-39 — STL de terceros fuera del repo público**, citando su origen. Alternativa: publicarlos. Razón: no se sabe su licencia; los componentes se descargan de EasyEDA.
- **D-40 — Licencia MIT** para el diseño propio, con excepción para el conector HSW. Razón: Carlos quiere que cualquiera lo use y lo mejore.

**Problemas y solución:**
- El correo corporativo estaba en todo el historial → historial nuevo (D-38) y correo personal global en git.
- El permiso automático bloqueó reescribir `main` → rama huérfana nueva sin tocar `main`.

**Archivos:** `.gitignore`, `LICENSE` (nuevo), `README.md`, `CLAUDE.md`, `cad/hsw_connector.py`, `cad/test_hsw_connector.py`, los 3 `externalfiles/3mfs/*.3mf`; `docs/bitacora.md`.

**Pendientes:** foto del medidor montado en la pared (README); ver la fecha y la hora en la pantalla (v2); opcional: LED rojo del PCF8574; después: sensor remoto y cápsula (D-34).

### 2026-10-24 → 2026-10-27 — Pendientes cerrados y fotos finales

**Objetivo:** cerrar los pendientes de la carcasa.

**Qué se hizo:**
- 2026-10-24: la fecha y la hora de la v2 se ven bien en la pantalla; el LED rojo del PCF8574 se queda como está.
- 2026-10-27: Carlos pasó 2 fotos del medidor en la pared HSW (tomadas el 2026-10-24 a las 21:55), con la luz de la pantalla encendida y apagada. Se agregaron al README como `docs/img/medidor_pared_1.jpg` y `_2.jpg`, reducidas a 1600 × 1200 y **sin metadatos EXIF** (traían GPS y el nombre del autor; el repo es público).

**Archivos:** `docs/img/medidor_pared_1.jpg`, `docs/img/medidor_pared_2.jpg` (nuevos), `README.md`, `CLAUDE.md`, `docs/bitacora.md`.

**Pendientes:** ninguno de la carcasa; después: sensor remoto y cápsula (D-34).

### 2026-11-23 — Medidor de corriente INA por el puerto del CAT6 (definición, sin diseño)

**Objetivo:** revisar el estado del proyecto y definir qué hace falta para agregar un medidor INA (V, A, W) en una cápsula enchufable por el CAT6.

**Qué se hizo:**
- Revisión de `CLAUDE.md`, `esphome/bmetesting_2.yaml` y de D-16, D-31 y D-34: el bus de sensores (D1/D2, 3.3 V) ya declara el 0x77, que no responde. La carcasa ya tiene la muesca del CAT6 (D-31). No está registrado si el conector de 90° de 6 pines se soldó en la placa ni qué lleva cada pin.
- Inventario consultado (sin cambios): no hay ningún INA ni conector RJ45/JST; hay `CON-borne-3p` ×15 (C02).
- Comparación de modelos con shunt R100: INA219 (26 V, ±3.2 A), INA226 (36 V, 16 bits, **±0.8 A**), INA3221 (26 V, 3 canales, ±1.6 A). Rango de uso según Carlos: de 3.3 a 12 V y hasta ~1 A (ESP y Arduino).
- 3 pendientes de Carlos en el repo de pendientes (`temp-th`): confirmar el INA y su shunt (ya estaba), revisar el conector de 6 pines y el CAT6, y medir la bornera de 3 polos.

**Decisiones:**
- **D-41 — Puerto I2C genérico en la cápsula:** el CAT6 queda fijo en la carcasa y termina en un **Dupont hembra de 4 pines** en el orden **GND, 3V3, SDA, SCL** (el de Qwiic/STEMMA). La cápsula lleva un alojamiento asimétrico y la marca del pin 1. Al revés no daña nada: el módulo no responde. Alternativas: desconectar en la placa; JST-XH (con traba, no está en el inventario). Razón: poder conectar otros módulos I2C cambiando solo el bloque del YAML; el Dupont ya lo tiene Carlos.
- **D-42 — INA en la cápsula con el shunt en el lado alto (+)** y una bornera de 3 polos **IN+ / OUT+ / GND** (`CON-borne-3p`). La cápsula es de base plana y se itera. Alternativa: bananas de 4 mm. Razón: la tierra común por el CAT6 pondría en corto un shunt en el lado bajo; el GND del CAT6 es solo referencia (la corriente regresa por su propio cable); las borneras conectan fácil y seguro. Si es un INA226 con shunt R100, solo llega a 0.8 A.
- **D-43 — Firmware v3 (por hacer):**
  - El módulo queda siempre en el YAML; si falta, solo falla ese sensor. ESPHome no lo vuelve a buscar hasta reiniciar.
  - 2a fila: el módulo, si está conectado; si no, la fecha y la hora. El BME de filamentos queda declarado, pero es probable que no se use.
  - Botón: 1 clic = luz por 30 s (responde ~0.4 s después); 2 clics = **modo banco** (luz fija y refresco de 1 s; se conserva después de reiniciar); clic largo (~3 s) = reinicio.
  - En HA: V, A, W, V del shunt y Wh; botones de puesta a cero de la energía y "Reiniciar"; interruptor "Modo banco".
  - Alternativa: un botón aparte. Razón: no cambia la carcasa (D-37).
- D-34 queda **sustituida en parte**: el puerto del sensor remoto se usa para la cápsula del INA.

**Problemas y solución:** ninguno.

**Archivos:** `docs/bitacora.md`, `CLAUDE.md`.

**Pendientes:**
1. Confirmar el INA y su shunt.
2. Revisar el conector de 6 pines de la placa y el CAT6.
3. Medir la bornera de 3 polos.

Después: boceto de la cápsula en PNG y `bmetesting_3.yaml`.

### 2026-11-24 — INA219, borneras y conector del puerto del CAT6 (bocetos, sin modelo)

**Objetivo:** cerrar los 3 datos pendientes de la cápsula del INA (D-41 a D-43) y bocetar la cápsula y su conector.

**Qué se hizo:**
- Inventario consultado (sin cambios): el INA es `MOD-INA219` (GY-219, 1 pieza, C26; 6 pines al frente y bornera de 2 atrás). `CON-borne-3p` ×15 (C02), `CON-borne-2p-negro` ×8 (C01). No hay Dupont ni tiras de pines registrados.
- El conector de 90° de 6 pines **no está soldado** en la placa: la asignación de pines y el armado del CAT6 se definen en el diseño.
- Análisis del riesgo de llevar la tierra en un conector aparte: (1) olvidarla da una lectura de voltaje sin sentido y sin aviso, y puede sacar VIN± del rango de modo común (0–26 V respecto a GND); (2) la bornera del módulo va soldada a su placa: la fuerza del desarmador y del cable va a las soldaduras. Ambos se mitigan con la disposición de D-45.
- Bocetos 2D (cotas nominales, POR MEDIR): `output/boceto_capsula_1.png` (cápsula ≈ 46 mm de ancho) y `output/boceto_conector_2.png` (conector; `_1` tenía el orden de pines sin espejar en la cara del cable). Geometría OpenLOCK tomada de `c:\marco-rompecabezas\cad\parameters.py` (`OL2_*`) y `cad/openlock_hembra.py`. Los scripts de los bocetos no se conservaron (solo los PNG).
- Pendientes de Carlos en CQX (`temp-th`): completado "revisar el conector de 6 pines"; "medir la bornera de 3 polos" se cambió a la de **2 polos negra**; nuevos: leer el shunt del INA219, medir el módulo y su bornera, y medir las tiras de pines 1×4 (todos para el 2026-11-25). Se borró de la bandeja local de pendientes un archivo de hacc del 2026-11-13 que nunca se subió.

**Decisiones:**
- **D-44 — El INA es el INA219 (GY-219)** del inventario. Con shunt R100: 26 V y ±3.2 A, suficiente para 3.3–12 V y ≤ 1 A. Dirección 0x40 (no choca con 0x76 ni 0x27). Falta confirmar el marcado del shunt.
- **D-45 — Borneras de la cápsula (sustituye la parte de la bornera de D-42):** IN+ / OUT+ en la bornera propia del módulo (VIN+ = fuente, VIN− = carga) y **GND en una `CON-borne-2p-negro` con los 2 polos puenteados** (llegan el negativo de la fuente y el de la carga), en una cuna impresa, unida con un cable al GND del módulo. Las 2 borneras en la misma cara y en una sola fila de 4 tornillos; **costilla bajo la bornera del módulo** hasta la base; el módulo en 2 postes. Alternativa: la bornera de 3 polos sola (D-42). Razón: propuesta de Carlos, más simple y sin soldar la corriente; la fila única evita olvidar la tierra y la costilla protege las soldaduras.
- **D-46 — Conector de 2 partes en el puerto del CAT6 (detalla D-41):**
  - Lado del cable (libre): **tira hembra 1×4** con el CAT6 **soldado** (es de cobre sólido: un crimpado Dupont agarra mal) y termofil, más un cincho o abrazadera sobre la funda.
  - Lado de la cápsula: **tira macho 1×4**, con cables al header del módulo (su orden VCC GND SCL SDA no coincide con GND 3V3 SDA SCL).
  - **Pin impreso Ø3 y hueco cruzados**, ~2 mm más largos que los pines metálicos. **Clip OpenLOCK** de tamaño completo, abajo de los pines (al revés no entra). El clip entra en la dirección de empuje y cierra con snap en los 2 bolsillos.
  - Orden al empujar: clip (10.8 mm), pines Ø3 (≈ 7.5) y Dupont (≈ 5.5). Cara de ≈ 25 × 13 mm; la cápsula solo lleva el bolsillo, y este diseño se reutiliza en cápsulas futuras.
  - **Clip suelto pegado con cianoacrilato** solo en la mitad del lado del cable, sin pasar de la cintura.
  - Alternativas: clip integrado a la parte del cable (Carlos prefirió el suelto); gancho integrado tipo RJ45 (más chico, pero exige pruebas, D-28).
  - Razón: idea de Carlos de una orientación con pin y hueco impresos; el OpenLOCK ya está probado en PETG y al pegarlo nunca se queda en la cápsula.
- Las tiras de pines **no se dan de alta** en el inventario por ahora (Carlos): se usan en el diseño con medidas nominales.

**Problemas y solución:** propuse al principio que el clip OpenLOCK bajara desde arriba. Al revisar el código del rompecabezas, el clip entra en la dirección de empuje: se corrigió antes de decidir.

**Parámetros definidos (nominales, por medir):** GY-219 25.5 × 22.3; borneras de paso 5.08; bolsillo OpenLOCK `OL2_*` del rompecabezas (boca 14.0, profundidad 10.8, espesor 4.2); pines guía Ø3 con hueco de +0.2.

**Archivos:** `output/boceto_capsula_1.png`, `output/boceto_conector_1.png`, `output/boceto_conector_2.png` (nuevos, fuera de git), `docs/bitacora.md`, `CLAUDE.md`.

**Pendientes (Carlos, 2026-11-25):**
1. Leer el marcado del shunt del INA219.
2. Medir la bornera de 2 polos negra (A–F).
3. Medir el módulo GY-219 y su bornera.
4. Medir las tiras de pines macho y hembra 1×4.

Después: modelo CadQuery de la cápsula y del conector, y `bmetesting_3.yaml`.

### 2026-11-25 — Cupón OpenLOCK, bornera de 2 polos medida y láminas de la cápsula y del conector

**Objetivo:** cerrar las medidas pendientes y dejar el diseño 2D de la cápsula del INA219 y del conector del CAT6.

**Qué se hizo:**
- Bornera de 2 polos negra (C01) medida por Carlos: 9.97 × 7.85 × 9.97 (tornillos al ras), paso 5.0 (4.92 por fuera con el cero en el grueso del pin; 3.62 por dentro), pin cuadrado 1 × 0.65 (0.65 en la dirección pin a pin) de 4.29 de largo, G1 3.14 / G2 4.15 / H1 3.58 / H2 4.65 (centro del pin a 3.65 de la cara del cable), hueco 4 × 5, E1 0.92 (E2 6.60, difícil de medir). En `cad/parameters.py` (`BORNE2_*`); pendiente cerrado en CQX.
- Juego del clip OpenLOCK medido en los STEP del rompecabezas: clip 13.2 × 19.5 × 3.5; bolsillo de 4.2 de alto (0.35 por lado), cámara de 13.6 (0.2 por lado), boca de 14.0. `OL2_*` copiados a `cad/parameters.py`.
- Cupón de retención `cad/cupon_openlock.py` → `output/cupon_openlock_N_1` (bolsillo nominal de 4.2, 17.6 × 12.8 × 8.2) y `cupon_openlock_T_1` (bolsillos de 3.8 con 2 puntos y de 3.6 con 4 puntos, 35.2 × 12.8 × 8.2). Mandados a imprimir; consumo de 5 g del FIL-0014 (laminado de 4.44 g) registrado en el inventario.
- GY-219 estimado con fotos de internet (`output/ina219_estimado_1.png`, `ina219_foto_web_1.png`): 25.5 × 22.3, 4 barrenos ≈ Ø2.8 a ≈ 21.0 × 17.4, header de 6 pines (VCC GND SCL SDA VIN− VIN+), bornera de paso 3.5. Carlos confirma que el suyo se parece (morado).
- Láminas técnicas con vistas numeradas y 3D aproximado (CadQuery + matplotlib): `cad/bocetos/lamina_capsula.py` → `output/boceto_capsula_12.png` (vistas 01–08) y `cad/bocetos/lamina_conector.py` → `output/boceto_conector_4.png` (vistas 11–17).
- Limpieza de `output/`: 42 versiones viejas a `output/historico/`; 15 ensambles viejos y 3 PNG con errores borrados (de 140 a 44 MB). `cq_utils.next_version_number` también cuenta `historico/`.
- Pendiente nuevo en CQX: contar los insertos M2.5 de C22 (el inventario marca 5 de M2.5×4×3.5 y 20 de M2.5×3×3.5).

**Decisiones:**
- **D-47 — Retención del clip OpenLOCK sin pegamento (sustituye el "pegado" de D-46):** el bolsillo del lado del cable es más bajo que el nominal (3.6–3.8, según el cupón); el de la cápsula queda en 4.2 y el ancho no se toca. Alternativas: pegarlo con cianoacrilato; apretar el ancho. Razón: si se rompe, el clip se cambia sin reimprimir; apretar el ancho flexionaría más el bulto del clip (D-28), y en el alto sobraban 0.35 por lado (el juego en Z del rompecabezas).
- **D-48 — Header del GY-219 desoldado:** cables soldados directo a sus huecos; a GND le llegan 2 (conector y bornera GND); VIN−/VIN+ del header sin cable. Alternativas: Dupont sobre el header (cápsula ≈ 25 de alto); cortar los pines y soldar sobre ellos. Razón: cápsula más baja, el orden se acomoda al soldar y no hay 12 V junto al I2C.
- **D-49 — Conector con Dupont sencillos:** 4 Dupont cortados y pegados con 2 vueltas de cinta de aislar en una ranura de ≈ 11.0 × 3.4 con tope atrás, de los 2 lados; **al ras de la cara** (fondo = largo de la hembra − 0.1; si salen, las caras no cierran y el clip no engancha). Se confirma D-46: machos en la cápsula, hembras en el cable.
- **D-50 — Cierre de la tapa de la cápsula:** tapa de 3.5, labio de 1.2 × 2.0 con entrada en chaflán de 0.8 × 45° y sin tramo al frente (chocaba con las borneras), 2 lengüetas en las esquinas del frente y 2 M3×8 cónicos avellanados atrás con insertos M3×4×4.2. Alternativas: clips flexibles (D-28); 4 tornillos. Razón: autoalineación desde la primera versión, sin piezas que se rompan ni tornillería de más.
- **D-51 — Acabado:** esquinas verticales R8 (cápsula) y R6 (conector); orillas sobre la cama en **gota r3.5** (tramo a 45° que entra 2.05 en la cama y luego arco). Alternativas: chaflán de 1.5 o 2; redondeo puro (voladizo > 45°); tapa de 2 con la gota partida o más chica. Razón: se ve redondo y se imprime sin voladizo.
- **D-52 — Frente simétrico:** 2 ventanas iguales de 9.5 × 6.5 r1, centradas a 8.6 de la base, a 18.8 entre sí y en espejo respecto al centro; postes del módulo de 2.0; separación módulo–GND de 1.0 (cable GND por la pared derecha); bornera GND en cuna de 3.2 con los pines cortados a 2. Cápsula de 52.3 × 44.1 × 19.7. Alternativa: esquinas R4 al frente. Razón: la ventana GND entraba 3.5 en la esquina R8 y caía en la gota, la bornera GND no cabía en el piso (pines de 4.29) y Carlos prefiere la simetría.
- **D-53 — Tapa con 2 ranuras ovaladas** de 8.0 × 4.5 y 9.5 × 4.5 sobre los tornillos de las borneras, nombres grabados. Alternativa: 4 círculos (pared de 0.3 entre los de paso 3.5).
- **D-54 — Prensa de costillas para el CAT6 (en lugar del cincho):** canal en U de 5.0 (funda Ø5.5) abierto arriba, 3 costillas de 1.2 × 0.5 (2 en el cuerpo, 1 en la tapa) que hacen una mini S. Alternativas: cincho; camino en S (radio mínimo del CAT6 ~22 mm, no cabe). Razón: menos espacio y sin piezas extra.
- **D-55 — Pin Ø3 × 7** con base r0.8 y punta en chaflán (debe pasar de 6 para impedir conectar volteado). Plan B: pin metálico (inserto M3 + tornillo sin cabeza, o pasador Ø3).
- **D-56 — Pieza del cable de 29 × 36 × 19.7:** mismo alto, gota y estilo que la cápsula; bloque macizo al frente de 16 (bolsillo, ranura de hembras de 14.5 y tope); 2 M3 en diagonal + labio, sin lengüetas. El largo se revisa con las piezas reales (podría bajar a ~30).
- **D-57 — Sin ventilación en la cápsula:** el shunt disipa 0.1 W a 1 A (a 3.2 A serían ~1 W y ahí sí haría falta).

**Problemas y solución:** la vista frontal reveló que la ventana GND entraba 3.5 en la esquina R8 y caía en la gota, y que la bornera GND no cabía en el piso (D-52). La vista 03 estaba dibujada desde adentro y no desde afuera; se espejeó. El numeral de exportación se reiniciaba al mover versiones al histórico; se corrigió en `cq_utils`.

**Parámetros definidos:** `OL2_*`, `OL_CLIP_T=3.5`, `OL_COUPON_WALL=2.0`, `OL_COUPON_TIGHT=(3.8, 3.6)`, `OL_COUPON_DOTS=(2, 4)`, `MARK_DOT_D=1.5`, `MARK_DOT_PITCH=2.0`, `MARK_DOT_DEPTH=0.6`, `BORNE2_*` (`cad/parameters.py`). Los valores de las láminas (D-50 a D-56) viven en `cad/bocetos/`; pasan a `parameters.py` al modelar.

**Archivos:** `cad/parameters.py`, `cad/cq_utils.py`, `cad/cupon_openlock.py`, `cad/bocetos/lamina_capsula.py`, `cad/bocetos/lamina_conector.py`; en `output/` (fuera de git): `cupon_openlock_N_1`, `cupon_openlock_T_1`, `boceto_capsula_11`/`_12`, `boceto_conector_3`/`_4`, `caja_frontal_1`/`_2`, `medidas_bornera_2p_3`/`_4`, `perfil_orilla_1`, `ina219_estimado_1`, `ina219_foto_web_1`, `boceto_tapa_capsula_1`/`_2`, `cupon_openlock_2.png`; `docs/bitacora.md`, `CLAUDE.md`.

**Pendientes (Carlos):**
1. Medidas reales del GY-219: placa, Ø y separación de barrenos (decide M3 o M2.5) y altura del centro del hueco de su bornera sobre la placa.
2. Marcado del shunt.
3. Largo de la carcasa de la hembra Dupont.
4. Resultado del cupón OpenLOCK.
5. Contar los insertos M2.5 de C22.
6. Decidir inserto o autorroscante en los postes del módulo (pregunta abierta).

### 2026-11-25 (2) — GY-219 medido y modelo CadQuery de la cápsula (checkpoint 1)

**Objetivo:** cerrar las medidas del INA219 y arrancar el modelo de la cápsula.

**Qué se hizo:**
- Carlos midió el GY-219 sobre `medidas_gy219_1.png`: placa A 20.9 × B 20.3 × H 1.5; 2 barrenos Ø2.9, ambos del lado de la bornera (orilla → orilla del hueco: D1 1.1, D2 1.0, E 2.5); bornera G1 = G2 = 5.3 (largo 9.7, centrada), F 10, J 10, K 1.0 (cara de la placa → orilla de abajo del hueco), L 1.5. Shunt R100 (0.1 Ω). Soldaduras de la bornera a 4.0–4.8 de la orilla, vistas por abajo (`medidas_pines_bornera_ina_1.png`).
- Dupont medidos: macho con carcasa de 14 × 2.5 y pin de 5.7; hembra de 12 × 2.5.
- Cupón OpenLOCK: los 2 bolsillos retienen bien; se queda el de 2 puntos (3.8).
- Inventario: los M2.5 están en la C24, no en la C14 ni en la C16. Ajuste de TOR-M2.5x6-negro de 12 a 20 (conteo físico). Insertos INS-M2.5x4x3.5: 5 en la C22, igual que el inventario.
- Láminas `boceto_capsula_13` → `_15` con el módulo medido; `parameters.py` con la sección CÁPSULA (`CAP_*`, `INA_*`, `GND_*`) y los Dupont (`DUP_*`).
- `cad/capsula.py` (cuerpo, tapa y envolventes) y `cad/test_capsula.py` (8 tests). Checkpoint 1 exportado: `capsula_cuerpo_2`, `capsula_tapa_2`, `capsula_ensamble_2` (42.85 × 43.1 × 21.6). Suite completa: 74 tests pasan.
- CQX (temp-th): completados el marcado del shunt, la medida del GY-219, el largo de la hembra Dupont, el conteo de insertos M2.5 y la decisión inserto/autorroscante.

**Decisiones:**
- **D-58 — Fijación del GY-219:** 2 postes Ø6 en los barrenos (ambos junto a la bornera), costilla bajo la bornera con ranura de 3.0–5.8 para sus pines y apoyo de 1.6 a 5 de la orilla del header. Alternativas: postes en diagonal (el módulo no tiene 4 barrenos); M3 (no pasa por Ø2.9). Razón: 2 tornillos bloquean el giro y el apoyo evita que el lado del header quede volado.
- **D-59 — Esquinas interiores R2.0** (antes R_OUT − WALL = 5.6); por fuera se queda R8. Razón: el módulo queda ~1 mm más pegado al frente (Carlos).
- **D-60 — Postes de 3.5 con inserto INS-M2.5x4x3.5 (barreno de 4.5, deja 1 de piso) y TOR-M2.5x6-negro avellanado** (5.7 de largo total, cabeza Ø3.8). Alternativas: autorroscante; poste de 2.0 (no alcanza para el inserto). Razón: lo que Carlos tiene. La cabeza cónica se apoya en la orilla del barreno sin avellanar (no apretar de más) y deja ~3.75 de rosca. La cápsula sube 1.5.
- **D-61 — Bolsillo OpenLOCK del lado del cable de 3.8** (cupón de 2 puntos). Razón: los 2 retuvieron bien; el de 3.8 aprieta menos.
- **D-62 — Bloque de atrás de 14.0** (antes 12.8). Alternativa: dejar que el macho sobresalga 1.2 dentro de la cavidad. Razón: el macho Dupont de 14 queda completo adentro (Carlos); la cápsula crece 1.2.

**Superadas:** de D-52, la cápsula de 52.3 × 44.1 × 19.7, las ventanas a 8.6 y a 18.8 entre sí, los postes de 2.0 y la cuna de 3.2 (ahora: ventanas a 10.5 y 16.15 entre sí, cuna de 5.08). De D-53, la ranura de 8.0 × 4.5 (ahora las 2 son de 9.5 × 4.5, porque la bornera del módulo tiene paso 5). De D-47, el rango de 3.6–3.8 (ahora 3.8).

**Problemas y solución:**
- La fórmula de la lámina (0.293 · r − CL) dejaba la esquina de la placa tocando el radio interior. Se cambió a `CAP_CLX = r − (r − CL)/√2` = 0.80; la cápsula quedó 0.4 más ancha que la lámina 15.
- OCC no redondea r3.5 en una tapa de 3.5: la tapa queda en gota r3.45.
- El plano "XZ" de CadQuery tiene la normal en −Y; las ventanas se cortaban hacia afuera. Se corrigió.
- La gota se arma como redondeo ∪ (chaflán ∩ franja de 1.03).

**Parámetros definidos:** `CAP_*`, `INA_*` (`INA_TB_PIN_SLOT = (3.0, 5.8)`, `INA_POST_H = 3.5`, `INA_POST_D = 6.0`, `INA_INS_DEPTH = 4.5`), `GND_*`, `CAP_BACK = 14.0`, `CAP_IN_R = 2.0`, `OL_CABLE_POCK_H = 3.8`, `DUP_W = 2.5`, `DUP_M_L = 14.0`, `DUP_M_PIN = 5.7`, `DUP_F_L = 12.0`, `DUP_F_SLOT_DEPTH = 11.9`.

**Archivos:** `cad/capsula.py`, `cad/test_capsula.py` (nuevos); `cad/parameters.py`, `cad/bocetos/lamina_capsula.py`, `cad/bocetos/lamina_conector.py` (bolsillo de 3.8, sin regenerar); en `output/` (fuera de git): `medidas_gy219_1`, `medidas_pines_bornera_ina_1`, `boceto_capsula_13`/`_14`/`_15` (`_11`, `_12` y `_13` pasaron a `historico/`), `capsula_cuerpo_1`/`_2`, `capsula_tapa_1`/`_2`, `capsula_ensamble_1`/`_2`.

**Pendientes (Carlos):**
1. Revisar `capsula_ensamble_2` en Onshape (checkpoint 1: cuerpo y posiciones).
2. Después: checkpoint 2, la cara de atrás (bolsillo OpenLOCK de 4.2, ranura de los 4 machos al ras y pin/hueco Ø3).

### 2026-11-27 — Cápsula completa (checkpoint 1 y 2), conector del CAT6 en CadQuery y firmware v3

**Objetivo:** cerrar las dudas del checkpoint 1 de la cápsula, modelar la cara del conector (checkpoint 2) y la pieza del cable, y preparar el firmware v3.

**Qué se hizo:**
- Checkpoint 1 revisado por Carlos en Onshape: faltaban la fijación de la bornera GND y la ruta de su cable. Se resolvieron en 3 vueltas (`capsula_*_3` a `_5`).
- Checkpoint 2: cara de atrás de la cápsula (`capsula_*_6`); luego, avellanado en el hueco del pin (`capsula_*_7`).
- Conector del CAT6 modelado en `cad/conector.py` (`conector_*_1` a `_4`), en coordenadas de la cápsula y probado acoplado contra ella sin interferencias.
- Firmware `esphome/bmetesting_3.yaml`: Carlos lo validó en HA y lo cargó por OTA. El log salió como se esperaba: 0x76 y 0x27 responden; 0x77 y el INA219 quedan FAILED porque no hay nada en el puerto.
- Carlos mandó a imprimir la cápsula [dato faltante: versión impresa; se le avisó que la vigente es `capsula_cuerpo_7` / `capsula_tapa_7`].
- Inventario: −19 g del FIL-0014 (PETG+ negro verde; 17 g laminados + 10 %), proyecto temp-th; quedan 105 g (commit `b78aa06` en el repo del inventario).
- 92 tests (antes 74): 13 de la cápsula y 13 del conector.

**Decisiones:**
- **D-63 — Bornera GND fijada entre la cuna y un bloque de la tapa:** la cuna es una **U** abierta del lado del cable. La tapa lleva un bloque casi sólido que baja 2.5 alrededor de la bornera, con paredes de 3.0 a la izquierda y atrás; a la derecha llega hasta el labio. Holgura de 0.2 a los lados y **0.1 arriba**. Al frente la detiene la pared de las ventanas. Solo le queda la ranura del desarmador. Alternativas: collar de 1.0 (Carlos: muy delgado); holgura de 0.2 arriba. Razón: antes la bornera solo estaba apoyada; al meter un cable se empuja hacia atrás y al apretar el tornillo gira.
- **D-64 — Cable GND libre por el piso junto a la pared derecha, cuna hueca hasta el piso (5.08):** entra a la cuna por el lado abierto de la U; adentro caben la soldadura y el puente entre los 2 pines. Alternativa: muesca de 3.0 en la pared de la cuna y canal de 2.5 con costilla baja de 1 × 2 (Carlos: deja sobrantes y la guía estorba). Razón: el cable se rutea más fácil.
- **D-65 — Ranura del desarmador recta, sin chaflán:** se decide después de imprimir. Alternativas: chaflán de ~1.5 en la boca de arriba (recomendada); chaflán en el fondo (con 1.0 el apoyo de cada franja baja de 1.67 a 0.67).
- **D-66 — Cara de atrás de la cápsula:**
  - Bolsillo OpenLOCK nominal de 4.2 a 1.6 del piso (z 3.6–7.8), con el perfil del cupón.
  - Ranura de los machos de 11.0 × 3.4 centrada a 11.2, de lado a lado del bloque de 14.
  - **Tope de los machos en la cavidad:** placa de 1.5 contra la pared de atrás, del piso a 14.4, con paso de cables de 9 × 2.
  - Alternativa: bloque de 15.5 con el tope adentro. Razón: la cápsula no crece; Carlos lo aprobó.
- **D-67 — Pin en gota y hueco con avellanado (sustituye la forma de D-55):**
  - Pin Ø3 × 7 con punta a 45° hacia abajo, base r0.8 y chaflán de 0.5 en la punta.
  - Hueco Ø3.2 × 9 con gota arriba y abajo y **avellanado de 45° de 1.7**.
  - Pin a −X y hueco a +X, a 9.5 del centro, cruzados en la pieza del cable.
  - Alternativa: pin metálico (plan B de D-55). Razón: un pin horizontal redondo no se imprime sin soporte; con el avellanado, la base r0.8 del pin no choca con la boca del hueco.
- **D-68 — Conector de 31 × 46 × 21.6 (sustituye las medidas de D-56):**
  - Mismo alto, pared, tapa, labio y orillas en gota que la cápsula.
  - Esquinas R4 en la cara de unión y R6 atrás.
  - Bolsillo de 3.8 centrado con el de la cápsula; ranura de hembras de 11.9 de fondo, con tope de 1.5 y paso de 9 × 2.
  - Alternativas: 29 × 36 con R6 (el pin y el hueco quedaban sobre la curva de la esquina); 36 de largo (Carlos: cavidad justa).
  - Razón: cara plana hasta ±11.5. La cavidad entre el tope de las hembras y la prensa pasa de 9.6 a **21.6**: las hembras entran por el frente con los cables sueltos hacia atrás, se acerca el CAT6 y se suelda cada hilo.
- **D-69 — Prensa del CAT6 recorrida 2 mm hacia atrás y con las esquinas del frente cortadas a 45°:**
  - Sección de 11 (antes 13).
  - Costillas del cuerpo a CON_D − 9 y CON_D − 3 (la de atrás, pegada a la pared); la de la tapa a CON_D − 6.
  - Canal de 5.0; esquinas del frente de la prensa cortadas a 45° (2.5) en la vista superior.
  - Razón: Carlos; más cavidad.
- **D-70 — Postes M3 del conector unidos a las paredes:**
  - El de la izquierda va en el bloque del frente, con el inserto a 0.8 del fondo del hueco del pin; sale 1.9 a la cavidad, antes 7.4.
  - Los 2 llevan relleno hasta sus paredes, sin medias lunas, recortado a 0.5 dentro de ellas. El de atrás también se une a la pared del canal.
  - Alternativa: recorrer el de atrás hacia la esquina (su centro ya está a 5.7 de la orilla, menos que los 6.5 de la cápsula; el avellanado se comería la gota).
  - Razón: queda todo de una pieza (Carlos).
- **D-71 — Firmware v3 (implementa D-43):**
  - INA219 a 0x40, 0.1 Ω, `max_current: 3.2A`, `max_voltage: 16V`.
  - INA y LCD se refrescan cada 5 s (cada 1 s en modo banco) con un `interval`.
  - Modo banco guardado en la flash (`restore_from_flash`); la energía no se guarda.
  - 2a fila: INA → filamentos → fecha y hora.
  - El nombre del dispositivo y el del botón no cambian.
  - En modo banco solo cambia la fila de abajo (Carlos).

**Superadas:** de D-56, 29 × 36 × 19.7, la costilla a CON_D − 5 / − 11 y la tapa a − 8 (ahora 31 × 46 × 21.6 y D-69). De D-55, el pin redondo (ahora en gota, D-67).

**Problemas y solución:**
- El relleno del poste de atrás se salía de la orilla en gota de la base (z 1.5–2.3, en la esquina R6; Carlos lo vio en Onshape). Se recortó con la cavidad agrandada 0.5 y se agregó un test de que nada sale de la caja exterior.
- La base r0.8 de cada pin chocaba con la boca del hueco de la otra pieza (1.7 mm³). Con un avellanado de 1.2 quedaba 0.006 y con 1.5, 0.00006; con 1.7 queda en 0.
- El poste de la izquierda tapaba el hueco del pin y parte del bolsillo: los cortes de la cara se pasaron después de los postes.
- La salida del CAT6 se comía la costilla de atrás: la salida empieza en la cara interior de la pared.

**Parámetros definidos:** `CAP_G_COLLAR_T = 3.0`, `CAP_G_COLLAR_CL = 0.2`, `CAP_G_COLLAR_H = 2.5`, `CAP_G_PRESS_CL = 0.1`; `CAP_POCK_Z0 = 3.6`, `CAP_POCK_H = 4.2`, `CAP_ROW_W = 11.0`, `CAP_ROW_H = 3.4`, `CAP_ROW_GAP = 1.7`, `CAP_ROW_ZC = 11.2`, `CAP_ROW_STOP_T = 1.5`, `CAP_ROW_STOP_W = 14.0`, `CAP_ROW_WIRE_W = 9.0`, `CAP_ROW_WIRE_H = 2.0`, `CAP_PIN_DX = 9.5`, `CAP_PIN_D = 3.0`, `CAP_PIN_L = 7.0`, `CAP_PIN_ROOT_R = 0.8`, `CAP_PIN_TIP_C = 0.5`, `CAP_HOLE_D = 3.2`, `CAP_HOLE_DEPTH = 9.0`, `CAP_HOLE_CSK = 1.7`; `CON_W = 31.0`, `CON_D = 46.0`, `CON_R_FACE = 4.0`, `CON_R_BACK = 6.0`, `CON_FRONT = 13.4`, `CON_POCK_H = 3.8`, `CON_CH_W = 5.0`, `CON_SAD_L = 11.0`, `CON_SAD_CH = 2.5`, `CON_SAD_WALL = 2.5`, `CON_RIB_T = 1.2`, `CON_RIB_H = 0.5`, `CON_RIBS_BODY = (CON_D − 9, CON_D − 3)`, `CON_RIB_LID = CON_D − 6`, `CON_BOSS_D = 7.4`, `CON_SCREW_WALL = 0.8`, `CON_SCREWS`.

**Archivos:** `cad/conector.py`, `cad/test_conector.py`, `esphome/bmetesting_3.yaml` (nuevos); `cad/capsula.py`, `cad/test_capsula.py`, `cad/parameters.py`, `CLAUDE.md`. En `output/` (fuera de git): `capsula_cuerpo/tapa/ensamble_3` a `_7` (`_1` a `_5` pasaron a `historico/`) y `conector_cuerpo/tapa/ensamble_1` a `_4` (`_1` y `_2` pasaron a `historico/`). Las láminas `boceto_capsula_15` y `boceto_conector_4` quedaron atrás del 3D (no se regeneraron).

**Pendientes (Carlos):**
1. Probar la cápsula impresa: pin en gota, techo del bolsillo, machos contra el tope, bornera GND en la U con el bloque de la tapa.
2. Confirmar el calibre del cable GND.
3. Imprimir el conector (`conector_*_4`) y ajustarlo según la cápsula; revisar el largo de la cavidad con las piezas reales.
4. Firmware v3: prueba del botón (1 clic, 2 clics, clic largo) y, con la cápsula, V y A contra el multímetro con una carga conocida.
5. Revisar en ESPHome que `presencetest1wemos.yaml` sea el archivo con el contenido de `bmetesting_3.yaml`.

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
