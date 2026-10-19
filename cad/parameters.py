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
# Pestana de primera capa (sustituye al brim): 0.5 mm de alto, por dentro de
# cada brazo, de la punta hasta la placa B. Contorno (x, y) de la mitad +Y;
# la cara Y = CONN_ARM_IN la cierra contra el brazo.
CONN_FOOT_H = 0.5
CONN_FOOT_PROFILE = ((-9.8, 3.8), (-9.8, 2.45), (-9.52, 1.76), (-8.85, 1.45),
                     (-6.4, 1.32), (-5.9, 1.43), (-1.6, 3.8))
# Redondeo concavo pestana -> cara interior del brazo (quita la esquina de 90)
CONN_FOOT_FILLET_R = 1.0
# Separacion entre la cara de la base del conector y la cara del panel HSW:
CONN_STANDOFF = CONN_X_BASE - CONN_B_X1   # 6.4
# El puente de la base (1 mm) queda embebido dentro de la tapa trasera:
CONN_EMBED = CONN_BRIDGE_T

# --- Impresion ----------------------------------------------------------------
# Chaflan de 45 grados en aristas que tocan la cama (contra pie de elefante).
# No se aplica al conector: su pestana de 0.5 mm y sus caras planas definen el
# apoyo y el ajuste en la celda.
BED_CHAMFER = 0.4

# --- Tapa trasera (pieza 1) -------------------------------------------------
TAPA_T = 4.0              # espesor de la tapa trasera
TAPA_W = 90.0             # ancho provisional (~ancho de la caja; se fija en la fase 3)
CONN_SPACING = HSW_ROW_PITCH   # 2 conectores en la misma fila horizontal
TAPA_STANDOFF = CONN_STANDOFF - CONN_EMBED   # 5.4: cara trasera de la tapa a cara del panel

# --- Pieza de prueba de la tapa trasera (fase 1) ---------------------------
TAPA_PRUEBA_H = 30.0      # alto de la placa de prueba

# =============================================================================
# Fase 2: componentes medidos y distribucion de la carcasa (D-18, D-19)
# =============================================================================

# --- Placa principal (medida 2026-10-14) ------------------------------------
# Ejes LOCALES (u, v, w), como en la foto con la cara de componentes hacia el
# observador: u = derecha, v = arriba, w = normal de la cara de componentes;
# origen en la esquina inferior izquierda. El micro-USB sale por el borde u = 0.
PCB_W = 50.0              # placa cuadrada de 50 x 50
PCB_T = 1.0
PCB_BOTTOM_H = 4.5        # pines del Wemos por la cara de soldadura
PCB_HOLE_D = 2.95
PCB_HOLE_PITCH = 42.22 + PCB_HOLE_D            # 45.17 (se midio orilla a orilla)
PCB_HOLE_INSET = (PCB_W - PCB_HOLE_PITCH) / 2  # 2.415
# Wemos D1 mini (externalfiles/wemosd1mini.stl + medidas de Carlos 2026-10-14)
WEMOS_W = 25.7
WEMOS_L = 34.25
WEMOS_GAP = 3.44          # plastico de los pines: cara de componentes -> placa del Wemos
WEMOS_TOP = 6.8           # lo mas alto del Wemos sobre la cara de componentes
WEMOS_PINS_L = 8 * 2.54   # 8 pines por fila, centrados en el largo del Wemos
WEMOS_ROW_PITCH = 22.86   # entre las 2 filas de pines
PIN_W = 2.54              # ancho de una fila de pines (plastico)
CABLE_TOP = 8.0           # cable mas alto sobre la cara de componentes
# Cabezal hembra de 8 pines del BME (el BME sale a la caja delantera con un
# cable propio: pines macho rectos doblados a 90 grados + cabezal hembra)
HDR_PINS = 8
HDR_U0 = 4.89             # centro del primer pin, desde el borde u = 0
HDR_FROM_TOP = 3.5        # centro de la fila, desde el borde v = PCB_W
HDR_H = 8.5               # cabezal hembra sobre la cara de componentes
HDR_PLUG_H = 12.5         # cabezal + pines macho doblados + cable
PCB_TOP_H = max(HDR_PLUG_H, CABLE_TOP, WEMOS_TOP)   # 12.5: lo mas alto sobre la placa
USB_W = WEMOS_GAP + 2.73  # centro del USB sobre la cara de componentes (6.17; 2.73 del STL)
USB_PROTRUDE = 2.2        # el micro-USB sobresale del borde u = 0
USB_V = 17.6              # centro del USB, desde el borde v = 0
USB_RECEPT_W = 8.0        # receptaculo micro-USB (nominal)
USB_RECEPT_H = 2.0          # del STL del Wemos
USB_PLUG_W = 12.0         # sobremolde del cable micro-USB (POR MEDIR)
USB_PLUG_H = 8.0
USB_PLUG_INSET = 0.2      # el sobremolde entra hasta 0.2 mm antes de la cara interior
USB_CABLE_ENV_L = 15.0       # largo del cable modelado fuera de la carcasa

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
# Marco: 6.60 del borde superior y 5.40 del inferior (Carlos, 2026-10-15; la
# medida anterior de 5.33 dejaba los barrenos ~1.6 mm arriba de los postes).
# Con el alto de 24.0 se centra donde lo dicen las 2 medidas:
LCD_BEZEL_TOP = (LCD_H - LCD_BEZEL_H) / 2 + (6.60 - 5.40) / 2    # 6.72
LCD_BEZEL_D = 7.18        # el marco sobresale de la cara frontal de la placa
LCD_VIEW_W = 64.53
LCD_VIEW_H = 14.12
LCD_VIEW_LEFT = LCD_BEZEL_LEFT + 2.70    # 7.62 desde el borde izquierdo de la placa
LCD_VIEW_TOP = LCD_BEZEL_TOP + 4.24      # 9.57 desde el borde superior de la placa
LCD_BACK_D = 9.81         # modulo I2C (potenciometro) detras de la placa
# Conector del modulo I2C con los 4 pines doblados a 90 grados hacia atras
# (2026-10-14): nada sobresale del borde derecho de la placa verde; el Dupont
# y su cable pasan a la caja trasera por una ventana en la divisoria.
# Posicion medida por Carlos en caja_delantera_6 con el LCD montado (2026-10-16),
# desde las caras interiores de la caja; vista de frente, el conector queda a
# la derecha. (El LCD_CONN_ZC = 11.6 anterior se habia contado desde el borde
# equivocado de la placa verde y dejaba la ventana ~13 mm abajo.)
LCD_CONN_TOP0 = 8.75      # techo interior -> borde superior del conector
LCD_CONN_TOP1 = 25.0      # techo interior -> borde inferior (Dupont + cable)
LCD_CONN_SIDE = 14.0      # pared lateral derecha (cara interior) -> borde del conector (14 a 14.2)
LCD_CONN_W = 10.0         # ancho del conector + Dupont, hacia el centro
LCD_BACK_EDGE_FREE = 2.0  # franjas libres detras de la placa verde en sus orillas izq./der. (confirmado por Carlos 2026-10-14)
LCD_CONN_BACK = 20.0      # cara trasera de la placa verde -> punta del cable (medido 2026-10-14)

# --- Boton tactil 12 x 12, momentaneo (medido 2026-10-14) --------------------
BTN_BODY = 12.0
BTN_BODY_H = 3.18         # cuerpo negro sin vastago
BTN_CAP = 10.0
BTN_TOTAL_H = 8.82        # base del cuerpo -> cara de la tapa verde
BTN_TRAVEL = 0.4

# --- BME280 de ambiente (medido 2026-10-14) ----------------------------------
# Visto de frente: ancho BME_L en X, alto BME_W en Z; los 2 barrenos van a lo
# largo del borde superior y los pines por el borde inferior, doblados hacia
# atras con su Dupont. El chip mira al frente (a la rejilla).
BME_L = 15.2
BME_W = 11.5              # medido 2026-10-14
BME_PCB_T = 1.5           # medido 2026-10-14
BME_PIN_BEND = 2.0        # los pines doblados bajan del borde inferior antes de ir hacia atras
BME_HOLE_D = 2.8
BME_HOLE_PITCH = (7.0 + 13.3) / 2    # 10.15 (medido por dentro y por fuera)
BME_HOLE_EDGE = 1.0 + BME_HOLE_D / 2  # 2.4: centro del barreno -> borde superior
BME_ENV_D = 16.0          # modulo + pines doblados + carcasas Dupont, hacia atras
BME_FRONT_GAP = 2.0       # cara interior del frente -> modulo (= alto del escalon)
BME_STANDOFF_D = 4.6      # escalon donde se apoya el modulo
BME_PIN_CLEAR = 0.15      # pin en el barreno, por lado
BME_PIN_OUT = 3.0         # el pin sobresale detras de la placa (Carlos: +2 tras caja_delantera_5)

# --- Tornilleria (inventario 2026-10-14) -------------------------------------
INS_M3_HOLE_D = 4.0       # INS-M3x4x4.2 (diametro exterior 4.2, largo 4)
INS_M3_L = 4.0            # largo del inserto M3
M3_CLEAR_D = 3.4
M3_HEAD_D = 5.5
M3_CSK_D = 6.0            # cabeza avellanada (90 grados) del TOR-M3x8, DIN 7991 nominal -- POR MEDIR
M3_CSK_CLEAR = 0.2        # holgura por lado del avellanado (la cabeza queda 0.2 bajo la cara)
M3_SCREW_L = 8.0          # TOR-M3x8 en las 2 uniones (D-19)
INS_M25_HOLE_D = 3.3      # INS-M2.5x4x3.5 (diametro exterior 3.5, largo 4)
INS_M25_L = 4.0           # largo del inserto M2.5
M25_SCREW_L = 6.0         # TOR-M2.5x6: placa y LCD

# --- Carcasa: 3 piezas (D-18, D-19) -----------------------------------------
WALL_T = 2.4
FRONT_T = 2.4             # cara frontal de la caja delantera
DIV_T = 2.4               # pared divisoria = fondo de la caja trasera
LCD_SIDE_GAP = 5.6        # a cada lado del LCD: ancho exterior de 96 (Carlos: max. 98, mejor 96)
TOP_MARGIN = 2.0          # pared superior -> LCD (las columnas ya no estan arriba del LCD)
GAP_LCD_BTN = 3.0
BOTTOM_MARGIN = 2.0       # cuerpo del boton -> piso interior (boton y BME en la misma fila)
FRONT_BACK_GAP = 3.0      # modulo I2C -> pared divisoria (paso de cables)
REAR_POST_GAP = 1.5       # pines del Wemos -> pared divisoria
REAR_BACK_GAP = 2.0       # componentes de la placa -> tapa trasera
USB_EDGE_GAP = 0.3        # cara del micro-USB -> cara interior de la pared inferior
USB_WIN_CLEAR = 0.3       # holgura del sobremolde en su ventana, por lado
BOSS_D = 8.0              # columnas de tornillo M3
BOSS_SIDE_INSET = 3.0     # centro de la columna -> cara interior de la pared lateral (medio embebida)
B_BOSS_DZ = 15.0          # columnas tapa-caja trasera: centro vertical +- 15 (libra las cabezas del juego A)
A_COL_CAP = 1.0           # material detras del fondo del barreno del inserto (juego A)
A_INSERT_DEPTH = 7.0      # caja delantera: M3x8 - divisoria 2.4 = 5.6, + holgura
B_INSERT_DEPTH = 6.0      # caja trasera: M3x8 - tapa 4.0 = 4.0, + holgura
PCB_POST_D = 6.0
PCB_POST_ENV_CLEAR = 0.2  # holgura de la envolvente de pines alrededor de cada poste, por lado
LCD_POST_D = 8.0          # punta del poste (contra la placa del LCD)
LCD_POST_BASE_D = 11.0    # base del poste sobre el frente: cono con mas material abajo
LCD_POST_BEZEL_CLEAR = 0.3  # el poste se recorta contra el marco del LCD + esta holgura
M25_INSERT_DEPTH = 6.0    # placa: M2.5x6, punta a 5.0 de la boca
LCD_INSERT_DEPTH = 5.0    # LCD: M2.5x6, punta a 4.4 de la boca (deja 2.2 de frente)
BTN_CLEAR = 0.2           # cuerpo del boton en su alojamiento, por lado
BTN_CAP_CLEAR = 0.3       # tapa verde en su ventana, por lado
BTN_POCKET_WALL = 1.6
LCD_WIN_CLEAR = 0.3       # el marco del LCD pasa por la ventana del frente: holgura por lado
DIV_SLOT_W = 8.0          # paso de cables en la divisoria (boton y BME), a la izquierda de la placa
DIV_SLOT_H = 14.0
DIV_SLOT_GAP = 1.5        # orilla izquierda de la placa -> paso de cables
DIV_SLOT_FLOOR = 1.5      # piso interior -> paso de cables (abajo, junto al BME; Carlos 2026-10-16)
CAT6_D = 5.5              # cable CAT6 al sensor remoto (medido 2026-10-14)
CAT6_CLEAR = 0.4          # pasacables: holgura por lado
CAT6_X = 0.0              # sale por la pared superior de la caja trasera, al centro
                          # (sus 6 pines estan en la orilla de la placa opuesta al USB)
DIV_LCD_WIN_CLEAR = 1.0   # ventana del Dupont del LCD en la divisoria: holgura por lado

# --- Pieza de prueba del frente (ventana + postes del LCD + boton) ----------
PRUEBA_FRENTE_MARGIN = 3.0    # bajo el alojamiento del boton
PRUEBA_FRENTE_BACK = 1.0      # detras de la cara frontal de la placa del LCD

# --- Boton: sujecion en su alojamiento (se elige con prueba_boton) -----------
BTN_MOUNT = "clip"        # "clip" | "presion" | "ambos" (elegido: clip, prueba_boton_2)
CLIP_W = 5.0              # ancho de cada brazo con ceja (2 brazos, lados opuestos)
CLIP_T = 0.6              # espesor del brazo (prueba_boton_3, variante 3)
CLIP_SLOT = 0.6           # ranura a cada lado del brazo (lo separa de la pared)
CLIP_LIP = 0.70           # la ceja entra sobre la base del cuerpo (prueba_boton_3, variante 3)
CLIP_GAP = 0.2            # base del cuerpo -> cara de la ceja (1 capa de 0.2)
BTN_LEG_FREE = 1.0        # pared y aletas terminan 1 mm antes de la base: libres las patas
PRESS_INTERF = 0.15       # aletas a presion: interferencia por lado
PRESS_FIN_T = 0.8         # espesor de cada aleta (flexiona hacia afuera, sin pared detras)
PRESS_FIN_L = 8.0         # largo de cada aleta (esquinas abiertas)

# --- Rejillas hexagonales (BME abajo al frente; chimenea en la caja trasera) --
HEX_F2F = 3.5             # hexagono, entre caras planas
HEX_RIB = 1.2             # nervio entre hexagonos (3 lineas de 0.4)
VENT_EDGE = 1.0           # margen de la rejilla a paredes, columnas y otras ventanas
VENT_RIM = 2.0            # margen de la rejilla a los bordes de union de cada caja

# --- Pieza de prueba del boton (3 variantes lado a lado) ---------------------
# prueba_boton_2: con ceja de 0.25 el boton entra pero se bota al empujarlo.
# prueba_boton_3 (ceja 0.40/0.55/0.70, brazo 0.8/0.7/0.6): mejora, falta fuerza;
# la flexion alcanza. prueba_boton_4 (ceja 0.85/1.0/1.15, brazo 0.6): se rompieron
# las 3 (flexion >= ~4.8 %, brazo vertical: se abre entre capas). Se queda la
# variante 3 de la prueba 3: en caja_delantera_5 sostiene el boton sin pegamento.
PRUEBA_CLIP_VARIANTS = ((0.85, 0.6), (1.00, 0.6), (1.15, 0.6))   # (CLIP_LIP, CLIP_T)
PRUEBA_BOTON_PITCH = 24.0
PRUEBA_BOTON_H = 24.0
MARK_D = 1.5              # puntos grabados que numeran la variante (extras.md)
MARK_DEPTH = 0.6
MARK_PITCH = 2.0

# --- Derivados (no editar: salen de lo anterior) -----------------------------
IN_W = LCD_W + 2 * LCD_SIDE_GAP                                      # 91.2
IN_H = TOP_MARGIN + LCD_H + GAP_LCD_BTN + BTN_BODY + BOTTOM_MARGIN   # 55.24
OUT_W = IN_W + 2 * WALL_T                                            # 96.0
OUT_H = IN_H + 2 * WALL_T                                            # 60.04
Z_IN0 = WALL_T                                                       # piso interior
Z_IN1 = WALL_T + IN_H                                                # techo interior
# Profundidad: Y = 0 es la cara trasera de la tapa trasera (hacia la pared)
Y_REAR0 = TAPA_T                                                     # 4.0
PCB_POST_H = PCB_BOTTOM_H + REAR_POST_GAP                            # 6.0
REAR_IN_D = PCB_POST_H + PCB_T + PCB_TOP_H + REAR_BACK_GAP           # 21.5
Y_DIV0 = Y_REAR0 + REAR_IN_D                                         # 25.5
Y_DIV1 = Y_DIV0 + DIV_T                                              # 27.9
FRONT_IN_D = FRONT_BACK_GAP + LCD_BACK_D + LCD_PCB_T + LCD_BEZEL_D - FRONT_T   # 19.19 (marco a ras del frente)
Y_FRONT_IN = Y_DIV1 + FRONT_IN_D                                     # 47.09
Y_FRONT = Y_FRONT_IN + FRONT_T                                       # 49.49
# Vista frontal (X, Z)
LCD_X0 = -(LCD_BEZEL_LEFT + LCD_BEZEL_W / 2)                         # marco centrado en X
LCD_Z1 = Z_IN1 - TOP_MARGIN                                          # borde superior del LCD
LCD_Z0 = LCD_Z1 - LCD_H
LCD_Y_PCB_FRONT = Y_FRONT - LCD_BEZEL_D                              # marco a ras de la cara frontal
VIEW_XC = LCD_X0 + LCD_VIEW_LEFT + LCD_VIEW_W / 2
VIEW_ZC = LCD_Z1 - LCD_VIEW_TOP - LCD_VIEW_H / 2
BEZEL_XC = LCD_X0 + LCD_BEZEL_LEFT + LCD_BEZEL_W / 2                # 0: ventana centrada en el marco
BEZEL_ZC = LCD_Z1 - LCD_BEZEL_TOP - LCD_BEZEL_H / 2
BTN_XC = BEZEL_XC
BTN_ZC = LCD_Z0 - GAP_LCD_BTN - BTN_BODY / 2
# Placa con el USB hacia abajo (u -> +Z, v -> -X, w -> -Y), centrada en X
PCB_Z0 = Z_IN0 + USB_EDGE_GAP + USB_PROTRUDE
PCB_X0 = PCB_W / 2                                                   # v = 0 cae en X = +25
PCB_Y_SOLDER = Y_DIV0 - PCB_POST_H                                   # cara de soldadura
PCB_Y_COMP = PCB_Y_SOLDER - PCB_T                                    # cara de componentes
# Columnas de tornillo
BOSS_X = IN_W / 2 - BOSS_SIDE_INSET                                  # 42.6
A_BOSS_Z = (Z_IN0 + BOSS_D / 2, Z_IN1 - BOSS_D / 2)                  # esquinas, tocando piso y techo
B_BOSS_Z = ((Z_IN0 + Z_IN1) / 2 - B_BOSS_DZ, (Z_IN0 + Z_IN1) / 2 + B_BOSS_DZ)
# Rejilla del frente: toda la zona bajo la ventana del LCD, con un margen
# libre a las orillas de la caja y a la ventana. Se saltan los hexagonos bajo
# el alojamiento del boton, los escalones del BME y la base de los postes.
FRONT_VENT_MARGIN = 3.0
FRONT_VENT_X = OUT_W / 2 - FRONT_VENT_MARGIN
FRONT_VENT_Z0 = FRONT_VENT_MARGIN
FRONT_VENT_Z1 = (BEZEL_ZC - LCD_BEZEL_H / 2 - LCD_WIN_CLEAR) - FRONT_VENT_MARGIN
# Hexagonos extra (2026-10-15): columna en zigzag a cada lado de la pantalla
# (misma reticula que la zona baja, n-esima posicion; queda a 2.2 de la orilla),
# fila arriba de la pantalla y fila corta arriba del boton
SIDE_VENT_N = 9           # posicion en la reticula de las filas pares (impares: n - 1 + medio paso)
TOP_VENT_N = 5            # igual que cada columna lateral
BTN_VENT_N = 3
# BME a la izquierda, entre el alojamiento del boton y la base de los postes
# del LCD (su cabezal en la placa queda abajo a la izquierda)
_LCD_HOLE_XMIN = min(abs(LCD_X0 + (LCD_W - LCD_HOLE_PITCH_X) / 2),
                     abs(LCD_X0 + (LCD_W + LCD_HOLE_PITCH_X) / 2))
_BME_X0 = BTN_BODY / 2 + BTN_CLEAR + BTN_POCKET_WALL + VENT_EDGE
_BME_X1 = _LCD_HOLE_XMIN - LCD_POST_BASE_D / 2 - VENT_EDGE
BME_XC = -(_BME_X0 + _BME_X1) / 2
BME_ZC = BTN_ZC
BME_HOLES_Z = BME_ZC + BME_W / 2 - BME_HOLE_EDGE
DIV_SLOT_X = -(PCB_W / 2 + DIV_SLOT_GAP + DIV_SLOT_W / 2)           # -30.5
DIV_SLOT_ZC = Z_IN0 + DIV_SLOT_FLOOR + DIV_SLOT_H / 2                 # 10.9: a la altura del BME y del boton
