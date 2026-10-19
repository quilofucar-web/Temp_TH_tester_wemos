import cadquery as cq
import pytest

import parameters as P
from caja_trasera import VENT_X, build_global, build_print
from components import pcb_holes_xz, usb_center, usb_plug_envelope
from geom import hex_grid_points, overlap_volume

Y_DIV_MID = (P.Y_DIV0 + P.Y_DIV1) / 2


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


def test_divider_solid_and_cavity_open_to_back(caja):
    assert _inside(caja, (0.0, Y_DIV_MID, 40.0))
    assert not _inside(caja, (0.0, P.Y_REAR0 + 1.0, 40.0))
    assert not _inside(caja, (0.0, P.Y_DIV0 - 1.0, 40.0))


def test_pcb_posts_with_insert_holes(caja):
    for x, z in pcb_holes_xz():
        assert not _inside(caja, (x, P.PCB_Y_SOLDER + 1.0, z))
        assert _inside(caja, (x + P.INS_M25_HOLE_D / 2 + 0.6, P.PCB_Y_SOLDER + 1.0, z))


def test_b_columns_with_insert_holes(caja):
    for sx in (-1, 1):
        for z in P.B_BOSS_Z:
            x = sx * P.BOSS_X
            assert not _inside(caja, (x, P.Y_REAR0 + 1.0, z))
            assert _inside(caja, (x, P.Y_REAR0 + P.B_INSERT_DEPTH + 1.0, z))


def test_a_holes_through_divider(caja):
    for sx in (-1, 1):
        for z in P.A_BOSS_Z:
            assert not _inside(caja, (sx * P.BOSS_X, Y_DIV_MID, z))
            assert _inside(caja, (sx * P.BOSS_X + P.M3_CLEAR_D / 2 + 0.5, Y_DIV_MID, z))


def test_cable_slot_in_divider(caja):
    assert not _inside(caja, (P.DIV_SLOT_X, Y_DIV_MID, P.DIV_SLOT_ZC))


def test_vents_top_and_bottom_walls(caja):
    pts = hex_grid_points(P.Y_REAR0 + P.VENT_RIM, P.Y_DIV0 - P.VENT_EDGE,
                          -VENT_X, VENT_X, P.HEX_F2F, P.HEX_RIB)
    y, b = [(a, bb) for a, bb in pts if abs(-bb - P.CAT6_X) > 10.0][0]
    assert not _inside(caja, (-b, y, P.OUT_H - P.WALL_T / 2))           # salida arriba
    far = [(a, bb) for a, bb in pts if abs(-bb - usb_center()[0]) > 15.0]
    y, b = far[0]
    assert not _inside(caja, (-b, y, P.WALL_T / 2))                     # entrada abajo


def test_usb_window_and_plug_clearance(caja):
    x, y, _ = usb_center()
    assert not _inside(caja, (x, y, P.WALL_T / 2))
    assert _inside(caja, (x - P.USB_PLUG_W / 2 - P.USB_WIN_CLEAR - 1.0, y, P.WALL_T / 2))
    assert overlap_volume(usb_plug_envelope(), caja) < 1e-3


def test_cat6_notch_in_top_wall_open_to_lid(caja):
    r = P.CAT6_D / 2
    z = P.OUT_H - P.WALL_T / 2
    for dx in (-r, 0.0, r):
        assert not _inside(caja, (P.CAT6_X + dx, P.Y_REAR0 + r + P.CAT6_CLEAR, z))
    assert not _inside(caja, (P.CAT6_X, P.Y_REAR0 + 0.1, z))             # abierta a la tapa
    assert _inside(caja, (P.CAT6_X, P.Y_REAR0 + 2 * (r + P.CAT6_CLEAR) + 0.5, z))
