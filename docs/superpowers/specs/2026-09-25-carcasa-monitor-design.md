# Diseño — Carcasa del monitor de temperatura/humedad (HSW) + cápsula del sensor remoto

**Fecha:** 2026-09-25 (decisiones al día hasta D-32, 2026-10-16) · **Estado:** carcasa de 96 × 60 modelada con medidas reales; caja delantera probada impresa.
**Insumo base:** `externalfiles/README-carcasa-monitor.md` (brief de Claude Web). Este documento lo actualiza donde difiere: el montaje ya no es "al rack" sino a una pared **HSW**.

---

## 1. Alcance

Dos entregables impresos en FDM (Bambu Lab P1S), modelados en CadQuery, exportados en STEP + STL:

1. **Carcasa principal** (3 piezas) montada en la pared HSW: LCD 16×2 + botón al frente; Wemos D1 mini, placa de bus y BME280 de ambiente dentro.
2. **Cápsula del sensor remoto**: BME280 atornillado a una cara de MDF dentro del espacio de filamentos, unido a la carcasa principal por cable CAT6.

Fuera de alcance por ahora: prensaestopas hermético de la cápsula (se hace si Carlos sella el espacio de filamentos), PCB diseñada, cambios al circuito.

## 2. Decisiones de arquitectura

| ID | Decisión | Razón | Alternativa descartada |
|---|---|---|---|
| D-01 | Sensor remoto por **I2C directo sobre CAT6**, cable de 1–1.5 m, 100 kHz | 1.5 m de CAT6 son ~85 pF, muy por debajo del límite de 400 pF del bus I2C | Extensor P82B715 o segundo ESP (solo se justifican a partir de ~2–3 m) |
| D-02 | En el CAT6, **SDA y SCL en pares distintos**, cada uno trenzado con GND (o 3V3); alimentación en un tercer par | Reduce la diafonía entre las líneas del bus | SDA+SCL en el mismo par |
| D-03 | **(Superada por D-18)** **BME280 de ambiente en un compartimento inferior separado por una pared**, con rejilla; por fuera se ve **una sola caja** | ~0.5 W de calor (ESP8266 + regulador + backlight) sesgan la lectura a más caliente y más seco, y el calor sube | Sensor junto al Wemos; cápsula externa visible |
| D-04 | **(Superada por D-18)** El BME de ambiente **se enchufa en un cabezal de la placa de bus y asoma a su compartimento por una ranura justa** en la pared divisoria | Quita cables y deja un hueco mínimo entre el aire caliente y el limpio | BME cableado suelto |
| D-05 | **Placa de bus**: stripboard de 6 tiras (3V3, GND, SCL, SDA + CSB y SDO del BME de ambiente con puentes), ~28 × 18 mm. Sobre ella: cabezal del BME de ambiente, **CAT6 soldado directo** (una bornera de paso 5.08 no cae en tiras vecinas de paso 2.54; la desconexión queda en la cápsula, D-12) y **un solo cable por señal hacia el Wemos**. El LCD y el botón toman GND de la tira; el 5V va directo del Wemos al LCD | El Wemos tiene un solo pad de 3V3 y uno de GND: 3–4 cables por pad dan soldaduras frágiles, y el CAT6 les transmite los jalones | Todo soldado directo al Wemos; perfboard de 2×8 cm |
| D-06 | **LCD conectado al PCF8574 por Dupont** (el resto va soldado) | La tapa de pantalla se separa por completo para darle servicio | PCF soldado |
| D-07 | **Todo detrás del LCD**: el Wemos va **junto al backpack**, en la misma capa de profundidad (hay ~33–37 × 36 mm libres junto al PCF8574) | Carcasa mínima, que no crezca hacia atrás | Wemos detrás del backpack (~+12 mm de fondo) |
| D-08 | Backlight: el botón lo enciende y **se apaga solo tras un tiempo** (configuración de ESPHome, sin impacto mecánico). BME280 en modo forzado, 1 lectura por minuto | Menos calor dentro de la caja; autocalentamiento del sensor despreciable | Backlight siempre encendido |
| D-09 | **3 piezas**, cada una en su orientación óptima y sin soportes (ver §3) | El conector HSW integrado obliga a imprimir de pie la pieza que lo lleva; la caja y la tapa quedan mejor acostadas | Caja trasera con conectores integrados (su techo quedaría como puente de ~90 mm); 2 piezas |
| D-10 | Montaje a la HSW con **2 conectores `hexagonconector3dprint` integrados en la tapa trasera, a 40.88 mm** (misma fila horizontal) | Conector probado por Carlos (resorte, se engancha detrás del panel, entra y sale fácil); 2 puntos bloquean el giro | Inserto estándar atornillado (a Carlos no le convence); tacos a presión |
| D-11 | **(Superada por D-19)** **Unión con 4 tornillos M3 pasantes** (tapa trasera → tubos en las esquinas de la caja → insertos térmicos en la tapa de pantalla). Las cabezas quedan en el hueco de 5.4 mm entre la tapa y el panel (una DIN 912 M3 mide 3 mm de alto), así que no hace falta avellanar | Se arma todo sobre la mesa y después se encaja en la rejilla. Un solo juego de 4 puntos, sin tornillos visibles al frente. Con dos juegos no se gana nada al abrir, porque la tapa 1 tapa los tornillos 2→3 | Dos juegos independientes (sigue siendo la opción de respaldo si los tornillos largos son un problema) |
| D-12 | **Cápsula remota atornillada con 2 tornillos a una cara de MDF**, con rejilla y **bornera de 4 polos dentro** (2 borneras de 2 lado a lado, o Dupont de 4). Los puentes CSB→3V3 y SDO→3V3 (dirección 0x77) se sueldan en la cápsula | La bornera sujeta el cable (alivio de tensión) y la cápsula se quita sin abrir la carcasa principal | Cable soldado fijo |
| D-18 | **Dos cajas separadas por profundidad** (2026-10-14): **caja trasera** (contra la pared) con la placa de 50 × 50 y el Wemos; **caja delantera** con el LCD, el botón y el BME de ambiente abajo. La pared divisoria es el fondo de la caja trasera. El BME sale de su cabezal con 4 cables Dupont (VCC, GND, SCL, SDA): el módulo trae por defecto la dirección 0x76 con CSB y SDO sin conectar | Idea de Carlos. El Wemos y el BME no comparten compartimento. En la caja delantera solo calienta la luz del LCD, que se apaga a los 30 s, y el BME va abajo con la entrada de aire abajo. D-04 ya no servía: el BME sobresale 5.9 mm de la placa y su chip queda a ~1.7 mm del lado caliente | Compartimento inferior en la misma caja con ranura (D-03/D-04) |
| D-19 | **Dos juegos de 4 M3×8** en lugar de 4 pasantes. Juego A: caja delantera ↔ caja trasera, desde dentro de la caja trasera. Juego B: tapa trasera ↔ caja trasera, desde atrás | Con ~54 mm de fondo, los pasantes medirían ~50 mm y el M3 más largo del inventario es de 25 mm. Se conservan el frente limpio, los 4 puntos por unión y el armado antes de colgar | Comprar M3×50 |
| D-20 | **El marco del LCD atraviesa el frente y queda a ras** (2026-10-14); ventana = marco + 0.3 por lado, centrada en el marco; postes con M2.5×6 (forma vigente en D-27) | Mejor ángulo de visión y frente limpio; la caja pierde 2.4 mm de fondo | Ventana al ~90% del marco con el LCD detrás |
| D-21 | **El BME sale del cabezal hembra de 8 pines con un cable propio**: pines macho rectos doblados a 90° + cabezal hembra en la otra punta. Lo más alto de la placa queda en 12.5 mm | Dupont macho recto sumaba ~11 mm de fondo; soldar directo quitaba la desconexión | Dupont recto; soldar directo |
| D-22 | **(Cerrada por D-28)** **Sujeción del botón por prueba física**: 3 variantes (clip con ceja, aletas a presión, ambas) en `prueba_boton`; se fija `BTN_MOUNT` | Un poste desde la divisoria no se puede imprimir (es la cara sobre la cama); el clip da tope real, la presión solo fricción | Retenedor atornillado (queda de respaldo) |
| D-23 | **Rejillas hexagonales**: caja delantera en la franja baja del frente y en sus paredes inferior y superior; caja trasera en sus paredes inferior y superior (chimenea). Puntas de los hexágonos en la vertical de impresión | Entrada de aire limpio abajo para el BME; el calor del Wemos sale arriba por su propia caja | Rejilla en la tapa trasera (sale al hueco de 5.4 mm, poca circulación) |
| D-24 | **Ancho exterior de 96: los pines del I2C del LCD van doblados hacia atrás** (2026-10-15) y el Dupont pasa a la caja trasera por una ventana en la divisoria (conector + 1.0 por lado) | El lugar donde va la caja mide 100 (Carlos: mejor 96) y la ventana queda centrada | Ensanchar los 2 lados a 116.8; solo el derecho (ventana descentrada); soldar el cable (sin desconexión) |
| D-25 | **Botón y BME de ambiente en la misma fila bajo el LCD**, con márgenes de 2 arriba y abajo | Había espacio perdido; el alto baja de 86 a 60 (idea de Carlos) | Zona propia del BME abajo |
| D-26 | **Columnas del juego A cortas y medio embebidas en las paredes laterales** (centro a 3.0 de la cara interior), en las esquinas tocando piso y techo, con su cara hacia el frente a 45°. Juego B a ±15 del centro | Liberan alto y dejan el frente libre para la rejilla | Columnas de esquina de largo completo (pedían 9 mm arriba del LCD) |
| D-27 | **Postes del LCD en cono, de Ø11 junto al frente a Ø8 en la punta**, recortados contra el marco + 0.3 | Con Ø5.6 (pared de ~1 mm) el poste se torcía al meter el inserto con el cautín | Postes cilíndricos delgados |
| D-28 | **Botón con clip: ceja de 0.70 y brazo de 0.6, sin pegamento** (cierra D-22) | En la caja real sostiene el botón; con ceja de 0.85 o más el brazo se rompe (flexión ≥ ~4.8 %, se abre entre capas) | Aletas a presión y "ambas" (no entraron); placa de retención; pegamento |
| D-29 | **BME de ambiente sobre 2 escalones de 2 mm con pin de Ø2.5** en sus barrenos de 2.8; el pin sobresale 3 mm y **se fija con una gota de silicón sobre los pines, sin remachar** (2026-10-16) | Sin tornillería; los pines crecen derechos al imprimir boca abajo; el silicón se quita si hay que cambiar el sensor | Tornillo; remachar los pines con el cautín |
| D-30 | **Rejilla del frente**: toda la zona bajo la ventana con 3 mm de margen, columna en zigzag de 5 por lado, 5 arriba de la pantalla y 3 arriba del botón (hexágono de 3.5, 47 en total, simétrica) | Estética (Carlos) | 2 franjas junto al botón; hexágonos de 3.0 o 2.5 |
| D-31 | **CAT6 por una muesca en la pared superior de la caja trasera, al centro, abierta hacia la tapa** (Ø5.5 + 0.4 por lado); alivio con un cincho por dentro. En la placa, conector de 90° delgado sobre 6 pines al centro de la orilla opuesta al USB | Se arma y desarma sin cortar ni volver a crimpar el cable | Barreno cerrado |
| D-32 | **Paso de cables del botón y del BME abajo** (2026-10-16): 8 × 14 a la izquierda de la placa (centro en X = −30.5), a 1.5 del piso interior (z 3.9–17.9) | Queda a la altura del BME y del botón; más a la derecha no cabe por la placa | Centrado en el alto (z 23–37) |

## 3. Piezas

| # | Pieza | Orientación de impresión | Contenido |
|---|---|---|---|
| 1 | **Tapa trasera** | De pie, con el borde de los conectores sobre la cama | 2 conectores hexagonales integrados a 40.88 mm, a ras de ese borde **superior** (prueba de la fase 1); 4 barrenos del juego B (D-19) |
| 2 | **Caja trasera** | Acostada sobre la pared divisoria (su fondo) | Placa de 50 × 50 en 4 postes con inserto M2.5 (componentes hacia la pared, USB hacia abajo); 4 columnas laterales con inserto M3 (juego B, ±15 del centro); 4 barrenos del juego A en la divisoria; paso de cables (botón y BME) de 8 × 14 a la izquierda de la placa, abajo (D-32); ventana del Dupont del LCD en la divisoria (D-24); ventana del micro-USB en la pared inferior; muesca del CAT6 en la pared superior (D-31); rejillas hexagonales en las paredes inferior y superior (D-23) |
| 3 | **Caja delantera** | Boca abajo (cara frontal en la cama) | Ventana del marco del LCD, que queda a ras del frente (D-20); 4 postes en cono con inserto M2.5 (D-27); fila bajo el LCD con el botón al centro (clip, D-28) y el BME a la izquierda (D-25, D-29); rejilla del frente (D-30) y en las paredes inferior y superior (D-23); 4 columnas cortas embebidas en las paredes con inserto M3 (juego A, D-26) |
| 4 | **Cápsula remota** | Por definir | BME280 + bornera, rejilla, 2 orejas para tornillo a MDF, entrada del CAT6 |

Vista lateral de referencia (D-18; exterior **96.0 × 60.04 × 49.49 mm**, más 5.4 mm de aire contra el panel):

```
  PARED HSW  5.4 aire | 1 tapa (4) | 2 caja trasera (23.9)      ║ 3 caja delantera (21.59)
  ◄═╣ conector  ═╪ M3 juego B ═▓ col. │ placa 50×50 + Wemos  ╪ A ▓│ LCD + botón
                                      │ (componentes → pared) ║   │ BME abajo ≋ rejilla
                                                    pared divisoria
```

## 4. Datos HSW (medidos del STL de la pared de Carlos; en la pared real, el eje Y del archivo es el vertical)

- Hexágonos con **cara plana arriba y abajo**, puntas a izquierda y derecha.
- Boca frontal: **22.0 mm** entre caras planas, **2.0 mm** de profundidad; chaflán de ~1 mm hasta el hexágono interior de **20.0 mm**.
- Grosor del panel: **8.0 mm**. Pared entre celdas: 1.6 mm al frente, 3.6 mm al fondo.
- Separación entre centros de celdas vecinas: 23.6 mm. **Misma fila horizontal: 40.88 mm.**
- Hueco detrás del panel: ~17 mm (el conector `3dprint` entra 15.8 mm).
- Conector `3dprint` (**corregido 2026-09-25**, al medir el detalle para el plan):
  - La **base** es el extremo con la U cerrada, un puente plano de 11.6 × 19.8 mm, y se une a la pieza.
  - La **placa B** (1.6 mm) asienta en la boca de 22.
  - La **placa A** (2.7 mm, en la punta, con chaflán de entrada) pasa el hexágono de 20 flexionando los brazos y se engancha detrás del panel con su rampa trasera. Por eso entra y sale con facilidad.
  - Las dos mitades solo se unen en la base, y ahí está el resorte.
  - **La tapa queda separada 5.4 mm de la cara del panel**: los brazos miden 6.4 mm de la base a la placa B, pero el puente de 1 mm de la base queda embebido en la tapa (pedido de Carlos, por estética). Ese hueco de aire ayuda al aislamiento térmico y deja lugar a las cabezas de los tornillos.
  - "Base en línea con la pieza": la cara inferior del conector (Z) va a **ras del borde de la pieza que apoya en la cama**. Así ni el conector ni la pieza necesitan soportes.
  - Protrusión total desde la cara de la tapa: 14.6 mm (5.4 en el aire + 9.2 dentro o detrás del panel).
  - Clon paramétrico validado contra el STL (volumen −0.6%), **incluida la pestaña de 0.5 mm de la primera capa**, que sustituye al brim.
  - **Resuelto (2026-10-14):** la prueba salió bien en todo; los conectores van a ras del borde **superior**.

## 5. Restricciones de impresión (del brief)

Pared ≥ 2.4 mm; holgura de 0.2 mm en ajustes deslizantes y de 0.3–0.4 mm en pasacables; sin voladizos > 45°; bosses con fillet en la base; ventanas y rejillas en caras que no requieran soporte.

## 6. Pendientes de medición (bloquean las cotas, no la arquitectura)

- [ ] **Botón:** Ø del barreno, rango de grosor de panel que admite, fondo detrás del panel, Ø de la tuerca.
- [x] **LCD:** Ø y posición de los 4 barrenos, área visible exacta, altura del bisel, posición del trimpot.
- [x] **PCF8574:** ¿los pines de I2C sobresalen del borde del LCD? Largo con el Dupont puesto.
- [x] **Wemos:** altura con los cables soldados; posición y altura del micro-USB.
- [ ] **Conexiones:** tamaño real de la placa de bus y de la bornera de la cápsula; Ø exterior del CAT6; cabezal del cargador micro-USB.
- [ ] **BME280:** confirmar con calibrador (el STL mide 11.5 × 15.3 mm, más chico que el nominal del brief).
- [x] **Tornillería:** resuelto con el inventario (D-19): M3×8 + insertos M3×4×4.2 en las 2 uniones; M2.5×6 + insertos M2.5×4×3.5 para la placa y el LCD.
- [ ] **Cápsula remota:** cara de MDF donde se atornilla y tornillos para MDF.

## 7. Verificación

- Tests en CadQuery: sólidos válidos, sin interferencias entre los componentes (STL de referencia) y la carcasa, los 2 juegos de 4 tornillos (D-19) coaxiales y con el largo justo, conectores a 40.88 mm.
- Revisión de Carlos en Onshape antes de cada impresión.
- **Piezas de prueba antes de la carcasa completa:** (a) tapa trasera con los 2 conectores sobre la pared real; (b) poste con inserto + ventana del LCD; (c) barreno del botón.

## 8. Orden de trabajo (acordado 2026-09-25)

1. **Etapa 1 — Tapa trasera:** base CAD + conector HSW + pieza de prueba en la pared real. (Plan de la fase 1; en curso.)
2. **Etapa 2 — Parte eléctrica + medición de componentes** (en paralelo con la prueba de la etapa 1). Carlos arma en banco:
   1. Tira de bus completa (6 tiras, cabezal hembra del BME de ambiente, CAT6 soldado directo; diagrama en `docs/img/tira_bus_3.png`).
   2. Cables soldados al Wemos y a la tira **con largo de sobra (~10–15 cm), sin recortar** (el largo final depende de la distribución).
   3. Prueba funcional con ESPHome: 2 BME, LCD y botón.
   4. Mediciones reales (§6 + §6.1) y foto del conjunto armado.
3. **Distribución final** (cuerpo + posiciones de la caja y la tapa de pantalla) con medidas claras y espacio para cables → revisión en Onshape → recorte de cables a su largo final.
4. Detalles: rejillas, compartimento del BME, alivios de tensión, pasacables.
5. Cápsula remota.

### 6.1 Mediciones del conjunto eléctrico armado (etapa 2)

- [ ] Tira de bus: largo × ancho × alto total, contando el cabezal.
- [ ] Wemos con cables soldados: altura total y hacia qué lado salen los cables.
- [ ] LCD + PCF con el Dupont puesto: cuánto sobresale de lado y hacia atrás.
- [ ] Calibre o diámetro de los cables usados y radio de doblez cómodo.
- [ ] Foto del conjunto armado.

### 6.2 Mediciones reales (2026-10-14, calibrador de Carlos)

| Pieza | Medida |
|---|---|
| Placa | 50 × 50 × 1.0; componentes hasta 14.2 sobre la placa; pines del Wemos 4.5 por abajo; 4 barrenos Ø2.95 a 45.17 entre centros |
| Wemos / USB | El USB sobresale 2.2 del borde, con su centro a 17.6 del borde vecino; cara inferior del Wemos a ~3.1 sobre la placa |
| BME local | En cabezal hembra; sobresale 5.9 del borde; cara superior a 14.22 |
| LCD | Placa 80 × 36.24 × 1.6; barrenos Ø3 a 75.0 × 31.15 entre centros; marco 71 × 24 a 4.92 (izq.) / 5.33 (arriba), sobresale 7.18; área visible 64.53 × 14.12 a 2.70 / 4.24 del marco; módulo I2C hasta 9.81 detrás; conector derecho: ~5 fuera del borde, centro a 11.6 del borde inferior, hasta 9.55 detrás; los Dupont hacen una curva suave de ~20 |
| Botón | Táctil 12 × 12, momentáneo; cuerpo 3.18; total con tapa 8.82; tapa 10 × 10; recorrido ~0.4 |
| Pendientes | Altura del centro del USB sobre la placa (se usa 5.4 estimado); sobremolde del cable micro-USB (se usa 12 × 8); BME con calibrador; posición del cabezal de 16 pines del LCD |
