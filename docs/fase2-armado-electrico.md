# Fase 2 — Armado eléctrico en banco + mediciones

Guía para armar el circuito definitivo (ya validado en protoboard) en su forma final, **con cables largos sin recortar**, y medirlo para modelar la caja. Decisiones de referencia: especificación D-01, D-02, D-04, D-05, D-06, D-08.

---

## 1. Mapa de pines (confirmado con el YAML de la protoboard, 2026-09-25)

| Señal | Pin Wemos |
|---|---|
| Bus sensores SDA | D2 (GPIO4) |
| Bus sensores SCL | D1 (GPIO5) |
| Bus LCD SDA | D6 (GPIO12) |
| Bus LCD SCL | D5 (GPIO14) |
| Botón (a GND, con pull-up interno) | D7 (GPIO13) |

Ninguno es pin de arranque (D3, D4 y D8 se evitan). ✓

**Direcciones:** **0x76 = ambiente** (SDO→GND en la tira de bus) y **0x77 = filamentos** (SDO→3V3 en la cápsula). El YAML de la protoboard las tenía con las etiquetas invertidas; se corrige **en el YAML**, no en el hardware (ver la §8).

---

## 2. Materiales

- [ ] Stripboard (con tiras de cobre continuas), ~6 tiras × 10 agujeros, para cortar a ~25 × 18 mm
- [ ] Cabezal hembra de 6 pines (paso 2.54) para el BME de ambiente
- [ ] Stripboard de 6 tiras (no 4): las tiras 5 y 6 son para CSB y SDO del BME de ambiente
- [ ] Cable delgado flexible (26–28 AWG, idealmente de silicón) en varios colores
- [ ] Cable Dupont hembra de 4 pines para el PCF8574
- [ ] CAT6 de 1–1.5 m (lado de la caja: **soldado directo a la tira**) + bornera de 4 polos (2 de 2 lado a lado) **solo en la cápsula remota**, ver si caben 2 hilos de CAT6 por polo
- [ ] Termofil

---

## 3. Tira de bus (D-05)

**Diagrama:** `docs/img/tira_bus_3.png` (lo genera `docs/img/tira_bus.py`).

Stripboard con **6 tiras** paralelas. El cabezal de 6 pines del BME cruza las 6 tiras; las tiras 5 y 6 solo sirven para configurar la dirección del sensor de ambiente.

| Tira | Señal | Conecta |
|---|---|---|
| 1 | 3V3 | Wemos 3V3 · BME ambiente VCC · CAT6 (soldado) · puente desde la tira 5 |
| 2 | GND | Wemos GND · BME ambiente GND · CAT6 (soldado) · **GND del LCD** · **GND del botón** · puente desde la tira 6 |
| 3 | SCL (sensores) | Wemos D1 · BME ambiente SCL · CAT6 (soldado) |
| 4 | SDA (sensores) | Wemos D2 · BME ambiente SDA · CAT6 (soldado) |
| 5 | CSB (BME ambiente) | **puente a la tira 1 (3V3)** → modo I2C |
| 6 | SDO (BME ambiente) | **puente a la tira 2 (GND)** → dirección **0x76** |

El orden de pines del GY-BME280 es VCC, GND, SCL, SDA, CSB, SDO, así que el cabezal cae en orden sobre las tiras 1 a 6. **Verificar el orden en tu módulo antes de soldar.**

Resultado: al Wemos le llega **un solo cable por pad** (3V3, GND, D1, D2). El LCD y el botón toman GND de la tira 2.

**Orientación del BME de ambiente (D-04):** en la caja, el sensor asomará por una ranura hacia su compartimento inferior. Deja el cabezal hembra **en un borde de la tira**, con el módulo apuntando hacia afuera de ella.

---

## 4. Wemos (cables soldados, largo de sobra ~10–15 cm)

| Pad Wemos | Va a |
|---|---|
| 3V3 | Tira 1 |
| GND | Tira 2 |
| D1 | Tira 3 (SCL sensores) |
| D2 | Tira 4 (SDA sensores) |
| 5V | VCC del PCF8574 (Dupont) — **único consumidor de 5V** |
| D6 | SDA del PCF8574 (Dupont) |
| D5 | SCL del PCF8574 (Dupont) |
| D7 | Botón, terminal 1 |
| — | Botón, terminal 2 → tira 2 (GND) |
| micro-USB | Alimentación (cargador 5V/1A) — nada soldado |

**Recomendación:** suelda los cables **por arriba del Wemos, sin tiras de pines**. Así el módulo queda más bajo, que es la altura que vamos a medir. Si ya tiene pines soldados, díselo a Claude: cambia la altura del conjunto.

---

## 5. Cable remoto (CAT6) y cápsula (D-01, D-02, D-12)

Pares del CAT6 (colores estándar T568B; lo importante es que **SDA y SCL vayan en pares distintos**):

| Par | Hilo de color | Hilo blanco |
|---|---|---|
| Naranja | SDA | GND |
| Verde | SCL | GND |
| Azul | 3V3 | 3V3 |
| Café | sin usar | sin usar |

**Lado de la caja:** cada hilo va soldado en su propio agujero de la tira (ver el diagrama). **Lado de la cápsula:** en la bornera de 4 polos, los 2 hilos que llevan la misma señal van juntos en el mismo polo.

**Extremo remoto (BME, dirección 0x77):** VCC y **CSB → 3V3**; **SDO → 3V3**; GND; SCL; SDA. Los puentes de CSB y SDO se sueldan en el lado del sensor.

---

## 6. Prueba funcional (antes de medir)

- [ ] **Instalar en el Wemos `esphome/bmetesting_1.yaml`** (versión 1: etiquetas de BME corregidas + apagado automático del backlight; copiar y pegar completo)
- [ ] Al arrancar, la luz se enciende y se apaga sola a los 30 s
- [ ] Calentar con la mano el BME de la tira: debe subir **Temp Ambiente** (confirma los puentes)
- [ ] ESPHome detecta **0x76** (ambiente) y **0x77** (remoto) en el bus de sensores (el log de `i2c: scan: true` los lista)
- [ ] El LCD muestra lecturas de los 2 sensores
- [ ] El botón enciende el backlight **y se apaga solo después del tiempo configurado** (D-08)
- [ ] Moviendo el CAT6 a lo largo, las lecturas no se cortan (prueba de robustez del I2C a 1–1.5 m)

---

## 7. Mediciones del conjunto armado (especificación §6 y §6.1)

Para enviar a Claude. **Con una foto de cada conjunto** junto a una regla.

**Conjunto armado:**
- [ ] Tira de bus: largo × ancho × alto total, contando el cabezal; alto del BME enchufado
- [ ] Wemos con cables: alto total (del fondo del PCB a lo más alto de las soldaduras o cables) y hacia qué lados salen los cables
- [ ] LCD + PCF con el Dupont puesto: cuánto sobresale el Dupont del borde del LCD (de lado y hacia atrás)
- [ ] Diámetro de los cables usados; radio de doblez cómodo del manojo
- [ ] Diámetro exterior del CAT6
- [ ] Cabezal del cable micro-USB del cargador: ancho × alto × largo de la parte rígida

**Componentes sueltos (se pueden medir ya, sin armar nada):**
- [ ] **Botón:** Ø del barreno, rango de grosor de panel que admite, profundidad total detrás del panel, Ø y grosor de la tuerca
- [ ] **LCD:** Ø y posición de los 4 barrenos (medidos desde una esquina del PCB); área visible (largo × alto y distancia a los bordes del PCB); alto del bisel metálico sobre el PCB
- [ ] **BME280:** confirmar 11.5 × 15.3 mm del PCB
- [ ] **Tornillería disponible:** largos de M3 que tienes y tipo de cabeza; insertos térmicos (rosca, Ø exterior, largo)

---

## 8. Cambios al YAML de ESPHome (sobre el de la protoboard)

1. **Intercambiar las etiquetas de los BME280:** `0x76` → "Ambiente" (`temp_amb`, `hum_amb`) y `0x77` → "Filamentos" (`temp_fil`, `hum_fil`). El `lambda` del LCD no cambia, porque usa los `id`.
2. **Apagado automático del backlight (D-08):**

```yaml
switch:
  - platform: template
    name: "Luz LCD"
    id: sw_backlight
    optimistic: true
    restore_mode: ALWAYS_OFF             # arranca apagado
    turn_on_action:
      - lambda: 'id(lcddisp).backlight();'
      - script.execute: apagar_luz       # se apaga sola
    turn_off_action:
      - lambda: 'id(lcddisp).no_backlight();'

script:
  - id: apagar_luz
    mode: restart                        # otra pulsación reinicia la cuenta
    then:
      - delay: 30s
      - switch.turn_off: sw_backlight
```

Sin cambios: pines, `update_interval: 30s` (modo forzado, autocalentamiento despreciable) y la frecuencia del I2C por defecto (50 kHz, adecuada para 1.5 m de CAT6).
