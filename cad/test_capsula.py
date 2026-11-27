import cadquery as cq
import pytest

import parameters as P
from capsula import (build_body, build_lid, build_lid_print, dupont_envelope, gnd_envelope,
                     ina_holes, module_envelope, tb_screws)
from geom import overlap_volume


@pytest.fixture(scope="module")
def body():
    return build_body()


@pytest.fixture(scope="module")
def lid():
    return build_lid()


def _inside(s, p):
    return s.val().isInside(cq.Vector(*p))


def test_valid_single_solids(body, lid):
    for s in (body, lid, build_lid_print()):
        assert s.val().isValid()
        assert len(s.solids().vals()) == 1


def test_size(body, lid):
    bb = body.val().BoundingBox()
    assert bb.xlen == pytest.approx(P.CAP_W, abs=0.01)
    assert bb.ymin == pytest.approx(0.0, abs=0.01)
    assert bb.ymax == pytest.approx(P.CAP_D + P.CAP_PIN_L, abs=0.01)   # el pin sale de la cara
    assert bb.zmin == pytest.approx(0.0, abs=0.01)
    assert bb.zmax == pytest.approx(P.CAP_BODY_H, abs=0.01)
    assert lid.val().BoundingBox().zmax == pytest.approx(P.CAP_H, abs=0.01)
    assert build_lid_print().val().BoundingBox().zmin == pytest.approx(0.0, abs=0.01)


def test_windows_symmetric_and_open(body):
    assert P.INA_XC == pytest.approx(-P.GND_XC)
    for xc in (P.INA_XC, P.GND_XC):
        assert not _inside(body, (xc, P.CAP_WALL / 2, P.CAP_HOLE_ZC))


def test_cable_holes_centered_on_windows():
    zm = P.INA_Z0 + P.INA_PCB_T + P.INA_TB_HOLE_Z0 + P.INA_TB_HOLE_H / 2
    zg = P.GND_Z0 + P.BORNE2_HOLE_Z0 + P.BORNE2_HOLE_H / 2
    assert zm == pytest.approx(P.CAP_HOLE_ZC)
    assert zg == pytest.approx(P.CAP_HOLE_ZC)


def test_components_do_not_touch_body_or_lid(body, lid):
    pcb, tb = module_envelope()
    for comp in (pcb, tb, gnd_envelope(), *dupont_envelope()):
        assert overlap_volume(body, comp) < 1e-6
        assert overlap_volume(lid, comp) < 1e-6


def test_pcb_sits_on_posts_and_support(body):
    z = P.INA_Z0 - 0.05
    for x, y in ina_holes():
        assert _inside(body, (x + 2.3, y, z))          # anillo del poste
        assert not _inside(body, (x, y, z))            # barreno del inserto
    ys = P.INA_Y0 + P.INA_MW - P.INA_SUP_Y
    assert _inside(body, (P.INA_XC, ys, z))


def test_lid_does_not_touch_body(body, lid):
    assert overlap_volume(body, lid) < 1e-6


def test_slots_over_terminal_screws(lid):
    for x, y in tb_screws():
        assert not _inside(lid, (x, y, P.CAP_H - 0.5))



def test_gnd_terminal_held(body, lid):
    """Cuna abajo; bloque de la tapa a los lados, atras y arriba."""
    xl, xr = P.GND_XC - P.BORNE2_L / 2, P.GND_XC + P.BORNE2_L / 2
    yb = P.GND_Y0 + P.BORNE2_D
    ym = P.GND_Y0 + P.BORNE2_D / 2
    ztop = P.GND_Z0 + P.BORNE2_H
    zc = ztop - 1.0
    cl, t = P.CAP_G_COLLAR_CL, P.CAP_G_COLLAR_T
    assert _inside(body, (xl + 0.5, P.GND_Y0 + 2.0, P.GND_Z0 - 0.05))   # apoyo de la cuna
    for dx in (0.1, t - 0.1):
        assert _inside(lid, (xl - cl - dx, ym, zc))                      # pared izq. de 3
        assert _inside(lid, (P.GND_XC, yb + cl + dx, zc))                # pared de atras de 3
    for x in (xr + cl + 0.1, P.CAP_W / 2 - P.CAP_WALL - P.CAP_LIP_CL - 0.1):
        assert _inside(lid, (x, ym, zc))                                 # der.: hasta el labio
    assert _inside(lid, (xl + 0.5, P.GND_Y0 + 0.8, ztop + P.CAP_G_PRESS_CL + 0.05))   # tope
    assert not _inside(lid, (xl + 0.5, P.GND_Y0 + 0.8, ztop + P.CAP_G_PRESS_CL - 0.05))


def test_gnd_wire_route_open(body):
    """Cuna en U hueca hasta el piso, abierta a la derecha; piso libre hasta la pared."""
    xr = P.GND_XC + P.BORNE2_L / 2
    z = P.CAP_FLOOR + 1.0
    assert not _inside(body, (P.GND_XC, P.GND_Y0 + P.BORNE2_D / 2, P.CAP_FLOOR + 0.3))
    for y in (P.GND_Y0 + 1.5, P.GND_Y0 + P.BORNE2_D - 1.5):
        assert not _inside(body, (xr, y, z))                             # sin pared derecha
    xw = P.CAP_W / 2 - P.CAP_WALL
    for x in (xr + 1.0, xw - 1.25):
        for y in (P.GND_Y0 + P.BORNE2_D + 3.0, P.CAP_CAV_Y1 - 4.0):
            assert not _inside(body, (x, y, z))                          # sin costilla


def test_connector_face(body):
    yf, zr = P.CAP_D, P.CAP_ROW_ZC
    zp = P.CAP_POCK_Z0 + P.CAP_POCK_H / 2
    # bolsillo OpenLOCK de 4.2, cerrado arriba y abajo
    assert not _inside(body, (0, yf - 0.5, zp))
    assert not _inside(body, (P.OL2_CHAMBER_W / 2 - 0.2, yf - P.OL2_TOTAL_DEPTH + 0.3, zp))
    assert _inside(body, (0, yf - 0.5, P.CAP_POCK_Z0 - 0.1))
    assert _inside(body, (0, yf - 0.5, P.CAP_POCK_Z0 + P.CAP_POCK_H + 0.1))
    assert _inside(body, (0, yf - P.OL2_TOTAL_DEPTH - 0.3, zp))     # no llega a la cavidad
    # ranura de los machos de lado a lado del bloque (= largo del macho)
    assert P.CAP_D - P.CAP_CAV_Y1 == pytest.approx(P.DUP_M_L)
    for y in (yf - 0.5, P.CAP_CAV_Y1 + 0.5):
        assert not _inside(body, (0, y, zr))
    # tope: detiene las carcasas y deja pasar los cables
    w, h = 4 * 2.54 / 2, P.DUP_W / 2
    yt = P.CAP_CAV_Y1 - P.CAP_ROW_STOP_T / 2
    assert _inside(body, (w - 0.2, yt, zr))
    assert _inside(body, (0, yt, zr + h - 0.1))
    assert not _inside(body, (0, yt, zr))
    # hueco a +X y pin a -X
    assert not _inside(body, (P.CAP_PIN_DX, yf - P.CAP_HOLE_DEPTH + 0.3, zr))
    assert _inside(body, (P.CAP_PIN_DX, yf - P.CAP_HOLE_DEPTH - 0.3, zr))
    assert _inside(body, (-P.CAP_PIN_DX, yf + P.CAP_PIN_L - 1.0, zr))
    assert _inside(body, (-P.CAP_PIN_DX, yf + 3.0, zr - P.CAP_PIN_D / 2 - 0.3))   # punta de la gota
    assert not _inside(body, (-P.CAP_PIN_DX, yf + 3.0, zr + P.CAP_PIN_D / 2 + 0.1))


def test_pin_longer_than_dupont_pins():
    assert P.CAP_PIN_L > P.DUP_M_PIN + 1.0      # D-55: el pin entra antes que los Dupont
    assert P.CAP_HOLE_DEPTH > P.CAP_PIN_L


def test_face_clear_of_lid_inserts(body):
    """Material entre el hueco del pin y el barreno del inserto M3."""
    x = (P.CAP_PIN_DX + P.CAP_HOLE_D / 2 + P.CAP_SCREW_X - P.INS_M3_HOLE_D / 2) / 2
    assert _inside(body, (x, P.CAP_SCREW_Y, P.CAP_ROW_ZC + 1.0))
