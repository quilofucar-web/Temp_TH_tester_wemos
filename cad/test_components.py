import cadquery as cq
import pytest

import components as C
import parameters as P
from geom import cyl_y, overlap_volume


def test_measured_hole_pitches_center_to_center():
    assert P.PCB_HOLE_PITCH == pytest.approx(45.17)
    assert P.LCD_HOLE_PITCH_X == pytest.approx(75.0)
    assert P.LCD_HOLE_PITCH_Z == pytest.approx(31.15)


def test_case_size_and_depth_stack():
    assert P.OUT_W == pytest.approx(96.0)
    assert P.OUT_H == pytest.approx(60.04)
    assert P.Y_DIV0 == pytest.approx(25.5)
    assert P.Y_DIV1 == pytest.approx(27.9)
    assert P.Y_FRONT == pytest.approx(49.49)


def test_bezel_centered_in_case():
    assert P.BEZEL_XC == pytest.approx(0.0, abs=1e-9)


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


def test_lcd_envelope_clears_front_and_divider():
    bb = C.lcd_envelope().val().BoundingBox()
    assert bb.ymax == pytest.approx(P.Y_FRONT)                  # marco a ras del frente
    assert bb.ymin == pytest.approx(P.Y_DIV1 + P.FRONT_BACK_GAP)
    assert bb.xmax <= P.IN_W / 2


def test_board_parts_pcb_holes_and_pins_clear_posts():
    parts = C.board_parts()
    for x, z in C.pcb_holes_xz():
        y_mid = P.PCB_Y_COMP + P.PCB_T / 2
        assert not parts["placa"].val().isInside(cq.Vector(x, y_mid, z))
        post = cyl_y(x, z, P.PCB_POST_D, P.PCB_Y_SOLDER, P.Y_DIV0)
        assert overlap_volume(parts["pines_wemos"], post) < 1e-3


def test_board_top_height_is_bme_header():
    assert P.PCB_TOP_H == pytest.approx(P.HDR_PLUG_H)
    bb = C.board_parts()["cabezal_bme"].val().BoundingBox()
    assert bb.ymin == pytest.approx(P.PCB_Y_COMP - P.HDR_PLUG_H)


def test_button_cap_protrudes_from_front():
    bb = C.button_envelope().val().BoundingBox()
    assert bb.ymax - P.Y_FRONT == pytest.approx(P.BTN_TOTAL_H - P.BTN_BODY_H - P.FRONT_T)


def test_envelopes_do_not_overlap_each_other():
    env = C.all_envelopes()
    names = list(env)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            assert overlap_volume(env[a], env[b]) < 1e-3, (a, b)


def test_lcd_cable_inside_board_edge_and_reaches_rear_box():
    bb = C.lcd_cable_envelope().val().BoundingBox()
    assert bb.xmax <= P.LCD_X0 + P.LCD_W                      # nada sobresale de lado
    assert bb.xmax == pytest.approx(P.IN_W / 2 - P.LCD_CONN_SIDE)   # medido en la caja
    assert bb.zmax == pytest.approx(P.Z_IN1 - P.LCD_CONN_TOP0)
    assert bb.ymin < P.Y_DIV0                                  # cruza la divisoria
    assert bb.ymin > P.Y_REAR0 + P.REAR_BACK_GAP
