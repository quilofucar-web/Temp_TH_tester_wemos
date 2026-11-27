import cadquery as cq
import pytest

import parameters as P
from capsula import build_body as cap_body, build_lid as cap_lid, dupont_envelope
from conector import (Y0, Y1, build_body, build_body_print, build_lid, build_lid_print,
                      cat6_envelope, cat6_zc, female_envelope, ly, screws)
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
    for s in (body, lid, build_body_print(), build_lid_print()):
        assert s.val().isValid()
        assert len(s.solids().vals()) == 1


def test_size(body, lid):
    bb = body.val().BoundingBox()
    assert bb.xlen == pytest.approx(P.CON_W, abs=0.01)
    assert bb.ymin == pytest.approx(Y0 - P.CAP_PIN_L, abs=0.01)      # el pin sale de la cara
    assert bb.ymax == pytest.approx(Y1, abs=0.01)
    assert bb.zmax == pytest.approx(P.CAP_BODY_H, abs=0.01)
    assert lid.val().BoundingBox().zmax == pytest.approx(P.CAP_H, abs=0.01)
    for s in (build_body_print(), build_lid_print()):
        assert s.val().BoundingBox().zmin == pytest.approx(0.0, abs=0.01)


def test_mates_with_capsule(body, lid):
    """Pines en los huecos cruzados, sin tocar la capsula."""
    for a in (body, lid):
        for c in (cap_body(), cap_lid()):
            assert overlap_volume(a, c) < 1e-6


def test_pocket_tight_and_centered(body):
    zc = P.CAP_POCK_Z0 + P.CAP_POCK_H / 2
    h = P.CON_POCK_H
    assert not _inside(body, (0, Y0 + 0.5, zc))
    assert _inside(body, (0, Y0 + 0.5, zc - h / 2 - 0.05))
    assert _inside(body, (0, Y0 + 0.5, zc + h / 2 + 0.05))
    assert _inside(body, (0, Y0 + P.OL2_TOTAL_DEPTH + 0.3, zc))


def test_females_slot_and_stop(body):
    zr = P.CAP_ROW_ZC
    for y in (0.5, P.DUP_F_SLOT_DEPTH - 0.1):
        assert not _inside(body, (P.CAP_ROW_W / 2 - 0.3, ly(y), zr))
    yt = ly(P.DUP_F_SLOT_DEPTH + P.CAP_ROW_STOP_T / 2)
    assert _inside(body, (4 * 2.54 / 2 - 0.2, yt, zr))                   # tope de las carcasas
    assert not _inside(body, (0, yt, zr))                                # paso de cables
    for c in (cap_body(), body):
        assert overlap_volume(c, female_envelope()) < 1e-6
    # hembras 0.1 afuera: tocan a los machos antes que se junten las caras (D-49)
    assert overlap_volume(female_envelope(), dupont_envelope()[0]) > 0


def test_pin_and_hole_crossed(body):
    zr = P.CAP_ROW_ZC
    assert _inside(body, (P.CAP_PIN_DX, Y0 - P.CAP_PIN_L + 1.0, zr))
    assert not _inside(body, (-P.CAP_PIN_DX, Y0 + P.CAP_HOLE_DEPTH - 0.3, zr))
    assert _inside(body, (-P.CAP_PIN_DX, Y0 + P.CAP_HOLE_DEPTH + 0.3, zr))


def test_cat6_clamp(body, lid):
    zc = cat6_zc()
    # canal abierto y salida por atras; la funda queda al ras arriba
    for y in (Y1 - 1.0, Y1 - P.CON_SAD_L + 1.0):
        assert not _inside(body, (0, y, zc))
    assert zc + P.CAT6_D / 2 == pytest.approx(P.CAP_BODY_H)
    # canal mas angosto que la funda: la aprieta por los lados
    assert _inside(body, (P.CON_CH_W / 2 + 0.1, Y1 - 3.0, zc))
    # 2 costillas abajo y 1 en la tapa, entre las 2
    zb = zc - P.CAT6_D / 2
    for yr in P.CON_RIBS_BODY:
        assert _inside(body, (0, ly(yr), zb + P.CON_RIB_H - 0.1))
    assert P.CON_RIBS_BODY[0] < P.CON_RIB_LID < P.CON_RIBS_BODY[1]
    assert _inside(lid, (0, ly(P.CON_RIB_LID), P.CAP_BODY_H - P.CON_RIB_H + 0.1))
    assert overlap_volume(lid, cat6_envelope()) > 0                      # muerde la funda


def test_screws_diagonal(body, lid):
    (x0, y0), (x1, y1) = screws()
    assert x0 < 0 < x1 and y0 < y1
    for x, y in screws():
        assert not _inside(body, (x, y, P.CAP_BODY_H - 1.0))            # barreno del inserto
        assert _inside(body, (x + P.INS_M3_HOLE_D / 2 + 0.5, y, P.CAP_BODY_H - 1.0))
        assert not _inside(lid, (x, y, P.CAP_H - 0.3))                   # avellanado


def test_lid_does_not_touch_body(body, lid):
    assert overlap_volume(body, lid) < 1e-6


def test_left_screw_in_front_block(body):
    """El poste de la izq. va casi todo en el bloque del frente, detras del hueco del pin."""
    x, y = screws()[0]
    yb = Y0 + P.CAP_HOLE_DEPTH
    assert y - P.INS_M3_HOLE_D / 2 == pytest.approx(yb + P.CON_SCREW_WALL)
    assert y + P.CON_BOSS_D / 2 - ly(P.CON_FRONT) < 2.5                 # sale poco a la cavidad
    assert _inside(body, (-P.CAP_PIN_DX, yb + P.CON_SCREW_WALL / 2, P.CAP_ROW_ZC))


def test_clamp_front_corners_cut(body):
    ys0 = Y1 - P.CON_SAD_L
    xs = P.CON_CH_W / 2 + P.CON_SAD_WALL
    z = P.CAP_FLOOR + 3.0
    for sx in (-1, 1):
        assert not _inside(body, (sx * (xs - 0.3), ys0 + 0.3, z))        # esquina cortada
        assert _inside(body, (sx * (xs - 0.3), ys0 + P.CON_SAD_CH + 0.5, z))


def test_bosses_joined_to_walls(body):
    """Sin medias lunas ni rendijas entre los postes y las paredes."""
    import numpy as np
    xw = P.CON_W / 2 - P.CAP_WALL
    (x0, y0), (x1, y1) = screws()
    r = P.CON_BOSS_D / 2
    z = P.CAP_FLOOR + 3.0
    for y in np.arange(y1 - r + 0.3, Y1 - P.CAP_WALL, 0.5):             # pared lateral, atras
        assert _inside(body, (xw - 0.2, y, z))
    for x in np.arange(P.CON_CH_W / 2 + P.CON_SAD_WALL + 0.2, xw, 0.5):  # pared de atras, del canal al poste
        assert _inside(body, (x, Y1 - P.CAP_WALL - 0.2, z))
    for y in np.arange(ly(P.CON_FRONT), y0 + r - 0.3, 0.5):              # pared lateral, adelante
        assert _inside(body, (-xw + 0.2, y, z))


def test_nothing_outside_outer_shell(body):
    """Nada se sale de la caja con su orilla en gota (salvo el pin de la cara)."""
    from capsula import gota
    from conector import outline
    from geom import box_between
    shell = gota(outline(0, P.CAP_BODY_H), "<Z", 0.0)
    out = body.cut(shell).intersect(box_between((-50, Y0 + 0.05, -1), (50, Y1 + 1, 30)))
    assert sum(s.Volume() for s in out.solids().vals()) < 1e-6
