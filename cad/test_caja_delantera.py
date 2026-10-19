import cadquery as cq
import pytest

import parameters as P
from caja_delantera import build_global, build_print
from caja_delantera import VENT_X, front_vent_points
from components import bme_holes_xz, lcd_holes_xz
from geom import hex_grid_points

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


def test_bezel_window_open_and_framed(caja):
    hx = P.LCD_BEZEL_W / 2 + P.LCD_WIN_CLEAR - 0.1
    hz = P.LCD_BEZEL_H / 2 + P.LCD_WIN_CLEAR - 0.1
    for dx in (-hx, 0.0, hx):
        for dz in (-hz, 0.0, hz):
            assert not _inside(caja, (P.BEZEL_XC + dx, Y_PLATE_MID, P.BEZEL_ZC + dz))
    edge = P.LCD_BEZEL_H / 2 + P.LCD_WIN_CLEAR
    assert _inside(caja, (P.BEZEL_XC, Y_PLATE_MID, P.BEZEL_ZC + edge + 1.0))
    assert _inside(caja, (P.BEZEL_XC, Y_PLATE_MID, P.BEZEL_ZC - edge - 1.0))


def test_lcd_posts_with_insert_holes_and_intact_front(caja):
    for x, z in lcd_holes_xz():
        assert not _inside(caja, (x, P.LCD_Y_PCB_FRONT + 1.0, z))
        assert _inside(caja, (x + P.INS_M25_HOLE_D / 2 + 0.6, P.LCD_Y_PCB_FRONT + 1.0, z))
        assert _inside(caja, (x, Y_PLATE_MID, z))


def test_button_window_and_pocket(caja):
    assert not _inside(caja, (P.BTN_XC, Y_PLATE_MID, P.BTN_ZC))                 # tapa verde
    assert not _inside(caja, (P.BTN_XC + P.BTN_BODY / 2, P.Y_FRONT_IN - 1.0, P.BTN_ZC))
    wall_x = P.BTN_XC + P.BTN_BODY / 2 + P.BTN_CLEAR + P.BTN_POCKET_WALL / 2
    z_wall = P.BTN_ZC + P.CLIP_W / 2 + P.CLIP_SLOT + 0.5          # fuera de la ranura del brazo
    assert _inside(caja, (wall_x, P.Y_FRONT_IN - 1.0, z_wall))
    assert _inside(caja, (P.BTN_XC + P.BTN_CAP / 2 + P.BTN_CAP_CLEAR + 0.5,
                          Y_PLATE_MID, P.BTN_ZC))


def test_button_clip_lip_holds_body(caja):
    if P.BTN_MOUNT == "presion":
        pytest.skip("sin ceja en la variante a presion")
    y_lip = P.Y_FRONT_IN - P.BTN_BODY_H - P.CLIP_GAP - 0.05     # justo detras de la cara que retiene
    for sx in (-1, 1):
        x = P.BTN_XC + sx * (P.BTN_BODY / 2 - P.CLIP_LIP + 0.05)
        assert _inside(caja, (x, y_lip, P.BTN_ZC))


def test_vents_front_band_and_walls(caja):
    pts = front_vent_points()
    assert any(x < 0 for _, x in pts) and any(x > 0 for _, x in pts)    # 2 franjas
    half = P.BTN_BODY / 2 + P.BTN_CLEAR + P.BTN_POCKET_WALL
    r = P.HEX_F2F / 3 ** 0.5
    for z, x in pts:                                                    # libra el boton
        assert abs(x - P.BTN_XC) >= half + r or abs(z - P.BTN_ZC) >= half + r
    z, x = pts[len(pts) // 2]
    assert not _inside(caja, (x, Y_PLATE_MID, z))                       # frente
    wall = hex_grid_points(P.Y_DIV1 + P.VENT_RIM, P.Y_FRONT_IN - P.VENT_EDGE,
                           -VENT_X, VENT_X, P.HEX_F2F, P.HEX_RIB)
    y, b = wall[len(wall) // 2]
    assert not _inside(caja, (-b, y, P.WALL_T / 2))                     # pared inferior
    assert not _inside(caja, (-b, y, P.OUT_H - P.WALL_T / 2))           # pared superior
    assert _inside(caja, (P.BOSS_X, Y_PLATE_MID, P.A_BOSS_Z[0]))        # columnas intactas


def test_a_columns_with_insert_holes(caja):
    for sx in (-1, 1):
        for z in P.A_BOSS_Z:
            x = sx * P.BOSS_X
            assert not _inside(caja, (x, P.Y_DIV1 + 1.0, z))
            assert _inside(caja, (x, P.Y_DIV1 + P.A_INSERT_DEPTH + 1.0, z))


def test_bme_standoffs_and_pins(caja):
    y_seat = P.Y_FRONT_IN - P.BME_FRONT_GAP
    pin_r = P.BME_HOLE_D / 2 - P.BME_PIN_CLEAR
    for x, z in bme_holes_xz():
        assert _inside(caja, (x + pin_r + 0.3, y_seat + 0.5, z))               # escalon
        assert not _inside(caja, (x + pin_r + 0.3, y_seat - 0.5, z))           # placa del BME
        assert _inside(caja, (x, y_seat - P.BME_PCB_T - P.BME_PIN_OUT + 0.1, z))  # punta del pin
        assert _inside(caja, (x, Y_PLATE_MID, z))                              # frente sin hueco


def test_front_vents_inside_face_and_clear_of_window():
    pts = front_vent_points()
    r = P.HEX_F2F / 3 ** 0.5
    wx = P.LCD_BEZEL_W / 2 + P.LCD_WIN_CLEAR
    wz0 = P.BEZEL_ZC - P.LCD_BEZEL_H / 2 - P.LCD_WIN_CLEAR
    wz1 = P.BEZEL_ZC + P.LCD_BEZEL_H / 2 + P.LCD_WIN_CLEAR
    low = [(z, x) for z, x in pts if z + r <= P.FRONT_VENT_Z1 + 1e-6]
    assert len({round(z, 3) for z, _ in low}) >= 3                      # zona baja: varias filas
    assert any(abs(x) > wx for z, x in pts if z > wz0)                  # columnas laterales
    assert any(z > wz1 for z, _ in pts)                                 # fila de arriba
    for z, x in pts:
        assert abs(x) + P.HEX_F2F / 2 <= P.OUT_W / 2 - 2.0             # margen a la orilla (ancho = entre caras)
        assert r <= z - 2.0 and z + r <= P.OUT_H - 2.0
        assert (abs(x) - P.HEX_F2F / 2 >= wx + 1.0 or z + r <= wz0 - 1.0
                or z - r >= wz1 + 1.0)                                  # libra la ventana
    assert sorted(pts) == sorted((z, -x) for z, x in pts)               # simetrica


def test_a_columns_short_and_clear_of_front(caja):
    y_c = P.Y_DIV1 + P.A_INSERT_DEPTH + P.A_COL_CAP
    for sx in (-1, 1):
        for z in P.A_BOSS_Z:
            x = sx * P.BOSS_X
            assert _inside(caja, (x + P.INS_M3_HOLE_D / 2 + 0.5, y_c - 0.5, z))
            assert not _inside(caja, (x - sx * (P.BOSS_D / 2 - 0.5), y_c + 1.0, z))  # cuna a 45
            assert not _inside(caja, (x, y_c + P.BOSS_D / 2 + 0.5, z))  # termina antes del frente
