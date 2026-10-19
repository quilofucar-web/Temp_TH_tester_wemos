import cadquery as cq
import pytest

import boton
import parameters as P
from prueba_boton import build_local, build_print, variant_x


@pytest.fixture(scope="module")
def pieza():
    return build_local()


def _inside(solid, p):
    return solid.val().isInside(cq.Vector(*p))


def test_print_orientation_single_valid_solid_on_bed():
    p = build_print()
    assert p.val().isValid()
    assert len(p.solids().vals()) == 1
    assert p.val().BoundingBox().zmin == pytest.approx(0.0, abs=0.01)


def test_each_variant_has_cap_window_and_marks(pieza):
    hh = P.PRUEBA_BOTON_H / 2
    z_mark = -hh + P.MARK_PITCH + P.MARK_D / 2
    for i, _ in enumerate(P.PRUEBA_CLIP_VARIANTS):
        x = variant_x(i)
        assert not _inside(pieza, (x, P.FRONT_T / 2, 0.0))             # ventana de la tapa
        for k in range(i + 1):
            xm = x + (k - i / 2) * P.MARK_PITCH
            assert not _inside(pieza, (xm, P.MARK_DEPTH / 2, z_mark))   # punto grabado
        assert _inside(pieza, (x + (i + 2) * P.MARK_PITCH, P.MARK_DEPTH / 2, z_mark))


def test_clip_variants_lip_and_arm(pieza):
    y_lip = -P.BTN_BODY_H - P.CLIP_GAP - 0.05
    pin = P.BTN_BODY / 2 + P.BTN_CLEAR
    for i, (lip, t) in enumerate(P.PRUEBA_CLIP_VARIANTS):
        x = variant_x(i)
        assert _inside(pieza, (x + P.BTN_BODY / 2 - lip + 0.05, y_lip, 0.0))    # ceja
        assert not _inside(pieza, (x + P.BTN_BODY / 2 - lip - 0.05, y_lip, 0.0))
        assert not _inside(pieza, (x + P.BTN_BODY / 2 - 0.1, -P.BTN_BODY_H - 0.1, 0.0))  # holgura
        assert _inside(pieza, (x + pin + t - 0.05, -1.0, 0.0))                  # brazo
        assert not _inside(pieza, (x + pin + t + 0.05, -1.0, 0.0))
