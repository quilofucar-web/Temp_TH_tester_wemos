import cadquery as cq
import pytest

import parameters as P
from tapa_trasera_prueba import build


@pytest.fixture(scope="module")
def tapa():
    return build()


def _inside(solid, p):
    return solid.val().isInside(cq.Vector(*p))


def test_single_valid_solid(tapa):
    assert tapa.val().isValid()
    assert len(tapa.solids().vals()) == 1


def test_sits_flat_on_bed(tapa):
    assert tapa.val().BoundingBox().zmin == pytest.approx(0.0, abs=0.01)


def test_connectors_spaced_on_hsw_row_pitch(tapa):
    """Brazos presentes a +-4.8 mm del centro de cada conector y ranura vacia
    en el centro, a Y=-10 (zona de brazos), justo encima de la cama."""
    arm_mid = (P.CONN_ARM_IN + P.CONN_ARM_OUT) / 2
    for xc in (-P.CONN_SPACING / 2, P.CONN_SPACING / 2):
        for z in (0.1, P.CONN_HALF_H):
            assert _inside(tapa, (xc - arm_mid, -10.0, z))
            assert _inside(tapa, (xc + arm_mid, -10.0, z))
            assert not _inside(tapa, (xc, -10.0, z))
    assert P.CONN_SPACING == pytest.approx(40.88)


def test_bed_edges_chamfered(tapa):
    """Chaflan de 45 grados en las aristas de la placa que tocan la cama
    (contra el pie de elefante), lejos de los conectores."""
    c = P.BED_CHAMFER
    x_edge = P.TAPA_W / 2
    assert not _inside(tapa, (x_edge - 0.1, P.TAPA_T / 2, 0.1))    # esquina recortada
    assert _inside(tapa, (x_edge - c - 0.1, P.TAPA_T / 2, 0.1))    # adentro del chaflan
    assert not _inside(tapa, (0.0, P.TAPA_T - 0.1, 0.1))           # arista frontal inferior
    assert _inside(tapa, (0.0, P.TAPA_T / 2, 0.1))


def test_plate_back_face_at_y0(tapa):
    assert _inside(tapa, (0.0, 0.1, 10.0))                # placa entre conectores
    assert not _inside(tapa, (0.0, -0.1, 10.0))           # nada detras entre conectores
    assert _inside(tapa, (0.0, P.TAPA_T - 0.1, 10.0))
    assert not _inside(tapa, (0.0, P.TAPA_T + 0.1, 10.0))
