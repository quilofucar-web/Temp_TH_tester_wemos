import cadquery as cq
import pytest
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Pnt

import parameters as P
from hsw_connector import connector_local, connector_placed
from stl_ref import EXTERNAL, load_stl_triangles, stl_volume, unique_vertices

REF_STL = EXTERNAL / "hexagonconector3dprint.stl"
# El STL original (de terceros) no se publica: sin el, se saltan las
# comparaciones contra el.
needs_ref = pytest.mark.skipif(not REF_STL.exists(), reason="STL de referencia no incluido")


@pytest.fixture(scope="module")
def local():
    return connector_local()


def _dist(shape, p):
    v = BRepBuilderAPI_MakeVertex(gp_Pnt(*map(float, p))).Vertex()
    return BRepExtrema_DistShapeShape(v, shape.wrapped).Value()


def test_local_is_single_valid_solid(local):
    assert local.val().isValid()
    assert len(local.solids().vals()) == 1


def test_local_bounding_box(local):
    bb = local.val().BoundingBox()
    assert bb.xmin == pytest.approx(P.CONN_X_TIP, abs=0.01)
    assert bb.xmax == pytest.approx(P.CONN_X_BASE, abs=0.01)
    assert bb.ymax == pytest.approx(P.CONN_B_YTRUNC, abs=0.01)
    assert bb.zmax == pytest.approx(P.CONN_HALF_H, abs=0.01)


@needs_ref
def test_volume_matches_reference_stl(local):
    ref = stl_volume(load_stl_triangles(REF_STL))
    assert ref == pytest.approx(P.CONN_REF_VOLUME, rel=0.001)
    assert local.val().Volume() == pytest.approx(ref, rel=0.03)


@needs_ref
def test_surface_matches_reference_stl(local):
    """>= 97% de los vertices del STL original a <= 0.3 mm del modelo
    (incluye la pestana de primera capa)."""
    pts = unique_vertices(load_stl_triangles(REF_STL))
    shape = local.val()
    close = sum(_dist(shape, p) <= 0.3 for p in pts)
    assert close / len(pts) >= 0.97


def test_first_layer_foot_present(local):
    """Pestana de 0.5 mm en la primera capa (sustituye al brim): hay material
    dentro de la ranura entre brazos solo en Z < -9.4."""
    s = local.val()
    assert s.isInside(cq.Vector(-8.0, 2.5, -9.8))
    assert s.isInside(cq.Vector(-8.0, -2.5, -9.8))
    assert not s.isInside(cq.Vector(-8.0, 2.5, -9.2))
    assert not s.isInside(cq.Vector(-8.0, 0.0, -9.8))      # las mitades siguen separadas


def test_foot_to_arm_fillet(local):
    """Redondeo concavo entre la cara superior de la pestana (Z=-9.4) y la
    cara interior del brazo (|Y|=3.8): material en la esquina, hueco en el
    centro del arco."""
    r = P.CONN_FOOT_FILLET_R
    z_top = -P.CONN_HALF_H + P.CONN_FOOT_H
    s = local.val()
    for sgn in (1, -1):
        # muy cerca de la esquina (dentro del redondeo)
        assert s.isInside(cq.Vector(-8.0, sgn * (P.CONN_ARM_IN - 0.05), z_top + 0.05))
        # centro del arco: fuera del solido
        assert not s.isInside(cq.Vector(-8.0, sgn * (P.CONN_ARM_IN - r), z_top + r))
    # fuera del contorno de la pestana (x > -1.6) no hay redondeo
    assert not s.isInside(cq.Vector(-1.0, P.CONN_ARM_IN - 0.05, z_top + 0.05))


def test_standoff_is_6_4():
    assert P.CONN_STANDOFF == pytest.approx(6.4)


def test_tapa_standoff_with_embedded_bridge():
    assert P.CONN_EMBED == pytest.approx(P.CONN_BRIDGE_T)
    assert P.TAPA_STANDOFF == pytest.approx(5.4)


def test_placed_connector_frame():
    bb = connector_placed(20.0, z_bottom=0.0).val().BoundingBox()
    assert bb.ymax == pytest.approx(P.CONN_EMBED, abs=0.01)                   # puente dentro de la tapa
    assert bb.ymin == pytest.approx(-(P.CONN_X_BASE - P.CONN_X_TIP - P.CONN_EMBED), abs=0.01)  # punta -14.6
    assert bb.zmin == pytest.approx(0.0, abs=0.01)                            # a ras de la cama
    assert bb.zmax == pytest.approx(2 * P.CONN_HALF_H, abs=0.01)
    assert (bb.xmin + bb.xmax) / 2 == pytest.approx(20.0, abs=0.01)           # centrado en X
    assert bb.xmax - bb.xmin == pytest.approx(2 * P.CONN_B_YTRUNC, abs=0.01)  # puntas en X
