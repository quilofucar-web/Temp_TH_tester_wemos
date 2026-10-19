import cadquery as cq
import pytest

import parameters as P
from tapa_trasera import build_global, build_print


@pytest.fixture(scope="module")
def tapa():
    return build_global()


def _inside(solid, p):
    return solid.val().isInside(cq.Vector(*p))


def test_print_orientation_single_valid_solid_on_bed():
    t = build_print()
    assert t.val().isValid()
    assert len(t.solids().vals()) == 1
    assert t.val().BoundingBox().zmin == pytest.approx(0.0, abs=0.01)


def test_plate_size(tapa):
    bb = tapa.val().BoundingBox()
    assert bb.xmin == pytest.approx(-P.OUT_W / 2)
    assert bb.xmax == pytest.approx(P.OUT_W / 2)
    assert bb.zmin == pytest.approx(0.0, abs=0.01)
    assert bb.zmax == pytest.approx(P.OUT_H)
    assert bb.ymax == pytest.approx(P.TAPA_T)


def test_connectors_flush_with_top_edge(tapa):
    """Brazos de los 2 conectores presentes justo bajo el borde superior y
    terminando a 2 * CONN_HALF_H de el (resultado de la prueba: arriba)."""
    arm_mid = (P.CONN_ARM_IN + P.CONN_ARM_OUT) / 2
    z_low = P.OUT_H - 2 * P.CONN_HALF_H
    for xc in (-P.CONN_SPACING / 2, P.CONN_SPACING / 2):
        assert _inside(tapa, (xc - arm_mid, -10.0, P.OUT_H - 0.1))
        assert _inside(tapa, (xc - arm_mid, -10.0, z_low + 0.1))
        assert not _inside(tapa, (xc - arm_mid, -10.0, z_low - 0.5))


def test_b_screw_holes(tapa):
    for sx in (-1, 1):
        for z in P.B_BOSS_Z:
            x = sx * P.BOSS_X
            assert not _inside(tapa, (x, P.TAPA_T / 2, z))
            assert _inside(tapa, (x + P.M3_CLEAR_D / 2 + 0.5, P.TAPA_T / 2, z))


def test_b_screw_countersink(tapa):
    """Avellanado de 90 grados en la cara hacia el panel: hueco en la boca
    hasta el diametro de la cabeza + holgura, solido mas adentro."""
    d = P.M3_CSK_D + 2 * P.M3_CSK_CLEAR
    depth = (d - P.M3_CLEAR_D) / 2
    for sx in (-1, 1):
        for z in P.B_BOSS_Z:
            x = sx * P.BOSS_X
            assert not _inside(tapa, (x + d / 2 - 0.15, 0.05, z))
            assert _inside(tapa, (x + d / 2 + 0.2, 0.05, z))
            assert _inside(tapa, (x + P.M3_CLEAR_D / 2 + 0.2, depth + 0.1, z))
