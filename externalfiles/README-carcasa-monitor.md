# Carcasa para monitor de temperatura/humedad (rack)

Brief de diseño para generar la carcasa impresa en 3D de un monitor ambiental
basado en ESP8266 (Wemos D1 mini) + ESPHome. Este documento es la especificación
de entrada; el objetivo es que ayudes a diseñar la carcasa de forma paramétrica.

---

## 1. Objetivo

Diseñar una carcasa impresa en FDM que aloje la electrónica de un monitor que
vive **dentro/detrás de un rack**. El monitor muestra en un LCD la temperatura y
humedad de dos puntos:

- **Ambiente** — sensor montado en la propia carcasa.
- **Caja de filamentos** — sensor remoto, conectado por un tramo de cable
  (Ethernet CAT6) que sale de la carcasa hacia otra ubicación.

La carcasa debe verse limpia por el frente (LCD + botón) y resolver bien el
cableado por detrás, ya que esa cara queda oculta.

## 2. Herramientas y entregable

- **CAD:** CadQuery (Python, paramétrico). Todas las cotas relevantes deben ser
  variables al inicio del script, no números mágicos repartidos en el código.
- **Salida:** exportar **STEP** (para importar a Onshape como referencia y seguir
  editando) y **STL** (para laminar e imprimir).
- **Fabricación:** impresión FDM. Diseñar respetando las restricciones de la
  sección 6.
- Preferencia de trabajo: iterativo, con puntos de confirmación. Ir por partes
  (primero el cuerpo y las posiciones, luego detalles) en vez de escupir el
  diseño completo de un jalón.

## 3. Componentes confirmados

> **IMPORTANTE:** las cotas de abajo son **nominales/típicas**. Antes de fijar el
> diseño hay que medir las piezas reales con calibrador (ver sección 7); los
> módulos clon varían de lote a lote. Trata estos valores como valores por
> defecto de las variables paramétricas.

| Pieza | Cant. | Cotas nominales (MEDIR) | Necesidades de montaje |
|-------|-------|-------------------------|------------------------|
| Wemos D1 mini (ESP8266) | 1 | PCB 34.2 × 25.6 mm; micro-USB en un borde corto, sobresale ~2 mm | Sujeción por soportes/clips; acceso al puerto micro-USB para el cable de alimentación |
| LCD 16×2 + backpack PCF8574 | 1 | PCB ~80 × 36 mm; área visible ~64.5 × 16 mm; barrenos M3 en las 4 esquinas (~75 × 31 mm entre centros); el backpack sobresale por detrás ~12–15 mm | Ventana frontal para el área visible; fijación por los 4 barrenos; hueco/holgura para el backpack y acceso al trimpot de contraste |
| BME280 (6 pines: VCC GND SCL SDA CSB SDO) — **ambiente** | 1 | PCB pequeño ~13 × 18 mm (MEDIR) | Montado en la carcasa pero **con flujo de aire y aislado del calor** (ver sección 4) |
| BME280 (6 pines) — **remoto (filamentos)** | 1 | igual que el anterior | NO va en la carcasa; sale por cable CAT6. La carcasa solo necesita la **salida de cable con sujeción** |
| Botón momentáneo (backlight) | 1 | según el que elija (típico panel: barreno ⌀ 6–12 mm) | Barreno en el panel frontal; el diámetro depende del botón elegido |
| Cargador micro-USB 5V/1A | 1 | — | El cable micro-USB entra a la carcasa hasta el puerto del Wemos |

## 4. Requisitos funcionales

**Panel frontal (cara visible):**
- Ventana para el área visible del LCD, con el PCB del LCD fijado por detrás a sus
  4 barrenos (soportes con inserto o autorroscante).
- Barreno para el botón, colocado de forma ordenada respecto al LCD (p. ej.
  centrado debajo o a un costado).

**Sensor de ambiente (crítico para la exactitud):**
- El BME280 de ambiente **no debe leer el calor de la electrónica**. El Wemos
  (su regulador) y el backlight del LCD generan algo de calor que sesgaría la
  lectura hacia más caliente y más seco.
- Diseñar para el sensor un **alojamiento ventilado, separado del compartimento
  de la electrónica**: rejillas/ranuras que den aire libre y, de ser posible, una
  pared o distancia que lo aísle del Wemos y del LCD. Alternativa a evaluar:
  montarlo asomando al exterior de la carcasa en su propio nicho ventilado.

**Sensor remoto:**
- Salida para el cable CAT6 con **sujeción/alivio de tensión** (pasacables,
  laberinto, o brida interna) para que un jalón no mueva las soldaduras.
- Opcional: un pequeño clip/soporte impreso aparte para fijar el sensor remoto en
  su destino (puede ser un segundo entregable, no parte de la carcasa principal).

**Alimentación:**
- Apertura para el cable **micro-USB** que llega al puerto del Wemos, con algo de
  alivio de tensión (el puerto micro-USB es el punto mecánico más débil).

**Ventilación general:**
- Ranuras o rejillas que dejen salir el calor y ayuden a que la lectura de
  ambiente sea honesta. Evitar que se convierta en una caja sellada.

## 5. Ensamble y estructura

- Diseño en **dos partes** a evaluar: cuerpo + tapa (frontal o trasera). Definir
  cuál cara se abre para el ensamble/servicio.
- Unión por **tornillos M3 con insertos térmicos** (el usuario tiene equipo para
  ponerlos) o autorroscantes en torres/bosses. Preferir insertos para poder
  abrir/cerrar varias veces.
- Ruteo interno pensado para los **dos buses**: sensores (3.3 V) por un lado y
  LCD (5 V) por otro; dejar espacio para una pequeña placa/perfboard de
  conexiones y un riel de GND común.

## 6. Restricciones de impresión FDM

- Espesor de pared ≥ 2.4 mm (≥ 2 perímetros).
- Tolerancia para ajustes deslizantes: ~0.2 mm (holgura) en huecos donde entra una
  pieza; ~0.3–0.4 mm para cables/pasacables.
- Evitar voladizos > 45° sin necesidad; orientar la pieza para minimizar soportes.
- Torres de tornillo y bosses con base reforzada (fillet) para que no se despeguen
  de la cama.
- Considerar la orientación de impresión al definir dónde caen las ventanas y
  rejillas (que no queden en caras que exijan soporte feo).

## 7. Mediciones a confirmar antes de fijar (checklist)

- [ ] Wemos: largo, ancho, altura total con headers soldados; cuánto sobresale y
      qué tan alto es el conector micro-USB; posición del puerto respecto al borde.
- [ ] LCD: dimensiones del PCB; posición y ⌀ de los 4 barrenos; tamaño y posición
      exacta del área visible; cuánto sobresale el backpack por detrás; posición
      del trimpot de contraste.
- [ ] BME280 (ambos iguales): dimensiones del PCB y posición de los barrenos si los
      tiene; altura con headers.
- [ ] Botón: diámetro del barreno y grosor de panel que admite.
- [ ] Diámetro exterior del cable CAT6 (para el pasacables).
- [ ] Conector del cargador: dimensiones del cabezal micro-USB para el hueco de
      entrada.

## 8. Preguntas abiertas / decisiones a tomar

- **Montaje al rack:** ¿pestañas para atornillar a una superficie, orejas para
  tornillo, imanes, o simplemente apoyada? (definir método y agregar sus features).
- **Orientación del LCD:** ¿carcasa horizontal (LCD acostado) o vertical?
- **Cara de apertura:** ¿tapa frontal (portezuela del LCD) o trasera (acceso a
  electrónica)?
- **Sensor de ambiente:** ¿nicho ventilado interno separado, o asomado al
  exterior? (impacta la exactitud, ver sección 4).
- **Insertos vs autorroscante** para el cierre.

---

### Resumen de conexiones (contexto eléctrico, ya validado en protoboard)

- **Bus sensores (3.3 V):** dos BME280 comparten SDA/SCL; VCC→3V3, GND común.
  Ambiente con SDO→GND (0x76), filamentos con SDO→3V3 (0x77); CSB de ambos→3V3.
- **Bus LCD (5 V):** backpack PCF8574 en SDA/SCL aparte; VCC→5V, GND común;
  jumper de backlight puesto.
- **Botón:** entre un GPIO y GND (controla el backlight).
- **Alimentación:** 5 V del cargador micro-USB → pin/puerto 5 V, que alimenta el
  LCD y el regulador interno del Wemos (3.3 V para los sensores).

*Nota: el ruteo eléctrico ya está resuelto; este README es solo para el diseño
mecánico de la carcasa. No hace falta rediseñar el circuito.*
