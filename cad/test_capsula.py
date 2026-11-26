import cadquery as cq
import pytest

import parameters as P
from capsula import (build_body, build_lid, build_lid_print, gnd_envelope,
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
    assert bb.ylen == pytest.approx(P.CAP_D, abs=0.01)
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
    for comp in (pcb, tb, gnd_envelope()):
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
