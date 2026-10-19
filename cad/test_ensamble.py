import cadquery as cq
import pytest

import parameters as P
from components import all_envelopes
from ensamble import build_assembly, pieces
from geom import overlap_volume
from prueba_frente import build_print as prueba_frente_print


@pytest.fixture(scope="module")
def ps():
    return pieces()


def _inside(solid, p):
    return solid.val().isInside(cq.Vector(*p))


def test_pieces_do_not_overlap(ps):
    names = list(ps)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            assert overlap_volume(ps[a], ps[b]) < 1e-3, (a, b)


def test_envelopes_clear_all_pieces(ps):
    for en, env in all_envelopes().items():
        for pn, piece in ps.items():
            assert overlap_volume(env, piece) < 1e-3, (en, pn)


def test_screw_set_a_coaxial_and_length_fits(ps):
    """M3x8 desde la cara trasera de la divisoria hasta el inserto de la caja
    delantera: agujero libre en ambas piezas, rosca >= largo del inserto y
    punta antes del fondo del agujero."""
    for sx in (-1, 1):
        for z in P.A_BOSS_Z:
            x = sx * P.BOSS_X
            assert not _inside(ps["caja_trasera"], (x, (P.Y_DIV0 + P.Y_DIV1) / 2, z))
            assert not _inside(ps["caja_delantera"], (x, P.Y_DIV1 + 1.0, z))
    tip = P.Y_DIV0 + P.M3_SCREW_L
    assert tip - P.Y_DIV1 >= P.INS_M3_L
    assert tip <= P.Y_DIV1 + P.A_INSERT_DEPTH - 0.5


def test_screw_set_b_coaxial_and_length_fits(ps):
    for sx in (-1, 1):
        for z in P.B_BOSS_Z:
            x = sx * P.BOSS_X
            assert not _inside(ps["tapa_trasera"], (x, P.TAPA_T / 2, z))
            assert not _inside(ps["caja_trasera"], (x, P.Y_REAR0 + 1.0, z))
    tip = P.M3_SCREW_L                       # desde la cara trasera de la tapa (Y = 0)
    assert tip - P.Y_REAR0 >= P.INS_M3_L
    assert tip <= P.Y_REAR0 + P.B_INSERT_DEPTH - 0.5


def test_m25_screws_fit_board_and_lcd():
    board_tip = P.M25_SCREW_L - P.PCB_T          # desde la boca del inserto
    lcd_tip = P.M25_SCREW_L - P.LCD_PCB_T
    assert P.INS_M25_L <= board_tip <= P.M25_INSERT_DEPTH - 0.5
    assert P.INS_M25_L <= lcd_tip <= P.LCD_INSERT_DEPTH - 0.5
    # el barreno del LCD no atraviesa el frente
    assert P.LCD_Y_PCB_FRONT + P.LCD_INSERT_DEPTH < P.Y_FRONT - 1.0


def test_set_a_heads_clear_rear_box(ps):
    """Las cabezas del juego A quedan dentro de la caja trasera, sobre la
    divisoria: no deben chocar con las columnas B ni con las paredes."""
    for sx in (-1, 1):
        for z in P.A_BOSS_Z:
            x = sx * P.BOSS_X
            for dx, dz in ((P.M3_HEAD_D / 2, 0), (-P.M3_HEAD_D / 2, 0),
                           (0, P.M3_HEAD_D / 2), (0, -P.M3_HEAD_D / 2)):
                assert not _inside(ps["caja_trasera"], (x + dx * 0.95, P.Y_DIV0 - 1.0,
                                                        z + dz * 0.95))


def test_assembly_builds():
    assy = build_assembly()
    assert len(assy.children) == 3 + len(all_envelopes())


def test_prueba_frente_single_solid_on_bed():
    p = prueba_frente_print()
    assert p.val().isValid()
    assert len(p.solids().vals()) == 1
    bb = p.val().BoundingBox()
    assert bb.zmin == pytest.approx(0.0, abs=0.01)
    assert bb.zmax == pytest.approx(P.Y_FRONT - P.LCD_Y_PCB_FRONT + P.PRUEBA_FRENTE_BACK)
