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


def board_parts():
    """Placa principal por partes (para verla clara en Onshape):
    placa de 1 mm con sus 4 barrenos, Wemos sobre el plastico de sus pines,
    pines del Wemos por la cara de soldadura, cabezal hembra del BME con su
    cable y receptaculo del micro-USB."""
    w = P.PCB_W
    pcb = pcb_box(0, w, 0, w, -P.PCB_T, 0)
    for x, z in pcb_holes_xz():
        pcb = pcb.cut(cyl_y(x, z, P.PCB_HOLE_D, P.PCB_Y_COMP - 1.0, P.PCB_Y_SOLDER + 1.0))
    u0, u1 = -P.USB_PROTRUDE, -P.USB_PROTRUDE + P.WEMOS_L
    v0, v1 = P.USB_V - P.WEMOS_W / 2, P.USB_V + P.WEMOS_W / 2
    uc = (u0 + u1) / 2
    pu0, pu1 = uc - P.WEMOS_PINS_L / 2, uc + P.WEMOS_PINS_L / 2
    rows = (P.USB_V - P.WEMOS_ROW_PITCH / 2, P.USB_V + P.WEMOS_ROW_PITCH / 2)
    hw = P.PIN_W / 2
    wemos = pcb_box(u0, u1, v0, v1, P.WEMOS_GAP, P.WEMOS_TOP)
    for v in rows:                                   # plastico de los pines
        wemos = wemos.union(pcb_box(pu0, pu1, v - hw, v + hw, 0, P.WEMOS_GAP))
    hr, hh = P.USB_RECEPT_W / 2, P.USB_RECEPT_H / 2
    wemos = wemos.union(pcb_box(-P.USB_PROTRUDE, 0, P.USB_V - hr, P.USB_V + hr,
                                P.USB_W - hh, P.USB_W + hh))
    pins = pcb_box(pu0, pu1, rows[0] - hw, rows[1] + hw,
                   -P.PCB_T - P.PCB_BOTTOM_H, -P.PCB_T)
    hv = P.PCB_W - P.HDR_FROM_TOP
    hdr = pcb_box(P.HDR_U0 - hw, P.HDR_U0 + (P.HDR_PINS - 1) * P.PIN_W + hw,
                  hv - hw, hv + hw, 0, P.HDR_PLUG_H)
    return {"placa": pcb, "wemos": wemos, "pines_wemos": pins, "cabezal_bme": hdr}


def board_envelope():
    """Todas las partes de la placa en un solo solido (para pruebas)."""
    parts = list(board_parts().values())
    env = parts[0]
    for p in parts[1:]:
        env = env.union(p)
    return env


def usb_plug_envelope():
    """Sobremolde del cable micro-USB: entra por la pared inferior hasta
    USB_PLUG_INSET antes de la cara interior, y sigue USB_CABLE_ENV_L hacia afuera."""
    x, y, _ = usb_center()
    hw, hh = P.USB_PLUG_W / 2, P.USB_PLUG_H / 2
    return box_between((x - hw, y - hh, -P.USB_CABLE_ENV_L),
                       (x + hw, y + hh, P.Z_IN0 - P.USB_PLUG_INSET))


# --- LCD ----------------------------------------------------------------------
def lcd_holes_xz():
    xc, zc = P.LCD_X0 + P.LCD_W / 2, P.LCD_Z0 + P.LCD_H / 2
    dx, dz = P.LCD_HOLE_PITCH_X / 2, P.LCD_HOLE_PITCH_Z / 2
    return [(xc + sx * dx, zc + sz * dz) for sx in (-1, 1) for sz in (-1, 1)]


def lcd_envelope():
    """Placa verde + marco (a ras de la cara frontal, pasa por la ventana) +
    modulo I2C (el area de la placa menos una franja libre en cada orilla
    izquierda/derecha, por donde pasan las columnas del juego A)."""
    x0, x1 = P.LCD_X0, P.LCD_X0 + P.LCD_W
    z0, z1 = P.LCD_Z0, P.LCD_Z1
    y_front = P.LCD_Y_PCB_FRONT
    y_back = y_front - P.LCD_PCB_T
    pcb = box_between((x0, y_back, z0), (x1, y_front, z1))
    bx0 = x0 + P.LCD_BEZEL_LEFT
    bz1 = z1 - P.LCD_BEZEL_TOP
    bezel = box_between((bx0, y_front, bz1 - P.LCD_BEZEL_H),
                        (bx0 + P.LCD_BEZEL_W, P.Y_FRONT, bz1))
    e = P.LCD_BACK_EDGE_FREE
    back = box_between((x0 + e, y_back - P.LCD_BACK_D, z0), (x1 - e, y_back, z1))
    return pcb.union(bezel).union(back)


def lcd_cable_box():
    """(x0, x1, z0, z1) del conector del LCD con los pines doblados hacia atras
    y su Dupont, segun lo medido en la caja con el LCD montado."""
    x1 = P.IN_W / 2 - P.LCD_CONN_SIDE
    return x1 - P.LCD_CONN_W, x1, P.Z_IN1 - P.LCD_CONN_TOP1, P.Z_IN1 - P.LCD_CONN_TOP0


def lcd_cable_envelope():
    """Dupont + cable detras del modulo I2C (los pines doblados ya caen en la
    envolvente del LCD), hasta LCD_CONN_BACK de la cara trasera de la placa
    verde; cruza la divisoria hacia la caja trasera."""
    x0, x1, z0, z1 = lcd_cable_box()
    y_back = P.LCD_Y_PCB_FRONT - P.LCD_PCB_T
    return box_between((x0, y_back - P.LCD_CONN_BACK, z0),
                       (x1, y_back - P.LCD_BACK_D, z1))


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


def bme_holes_xz():
    dx = P.BME_HOLE_PITCH / 2
    return [(P.BME_XC - dx, P.BME_HOLES_Z), (P.BME_XC + dx, P.BME_HOLES_Z)]


def bme_envelope():
    """BME de ambiente detras de la rejilla, a la izquierda del boton: placa
    paralela al frente (sin el volumen de sus 2 barrenos, por donde pasan los
    pines del frente) + bloque de los pines doblados y el Dupont, que bajan
    del borde inferior y van hacia atras."""
    y1 = P.Y_FRONT_IN - P.BME_FRONT_GAP
    y_back = y1 - P.BME_PCB_T
    hl = P.BME_L / 2
    z0 = P.BME_ZC - P.BME_W / 2
    board = box_between((P.BME_XC - hl, y_back, z0),
                        (P.BME_XC + hl, y1, P.BME_ZC + P.BME_W / 2))
    for x, z in bme_holes_xz():
        board = board.cut(cyl_y(x, z, P.BME_HOLE_D, y_back - 1.0, y1 + 1.0))
    dupont = box_between((P.BME_XC - hl, y1 - P.BME_ENV_D, z0 - P.BME_PIN_BEND),
                         (P.BME_XC + hl, y_back, z0 + P.PIN_W))
    return board.union(dupont)


def all_envelopes():
    """{nombre: Workplane} para el ensamble y las pruebas."""
    return {
        **board_parts(),
        "cable_usb": usb_plug_envelope(),
        "lcd": lcd_envelope(),
        "cable_lcd": lcd_cable_envelope(),
        "boton": button_envelope(),
        "bme": bme_envelope(),
    }
