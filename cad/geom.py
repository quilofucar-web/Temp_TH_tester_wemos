"""Primitivas geometricas compartidas (cajas entre 2 esquinas, cilindros
paralelos a Y) y medicion de traslapes. Solo primitivas, sin loft
(CLAUDE.md, convenciones)."""
import math

import cadquery as cq


def box_between(p0, p1):
    """Caja alineada a los ejes entre dos esquinas opuestas (en cualquier orden)."""
    lo = [min(a, b) for a, b in zip(p0, p1)]
    hi = [max(a, b) for a, b in zip(p0, p1)]
    size = [h - l for l, h in zip(lo, hi)]
    return cq.Workplane("XY").box(*size, centered=False).translate(tuple(lo))


def cyl_y(x, z, d, y0, y1):
    """Cilindro de diametro d con eje paralelo a Y, de y0 a y1 (en cualquier orden)."""
    lo, hi = min(y0, y1), max(y0, y1)
    return cq.Workplane(obj=cq.Solid.makeCylinder(
        d / 2, hi - lo, cq.Vector(x, lo, z), cq.Vector(0, 1, 0)))


def cone_y(x, z, d0, y0, d1, y1):
    """Tronco de cono con eje paralelo a Y: diametro d0 en y0 y d1 en y1."""
    h = y1 - y0
    base, top = (d0, d1) if h > 0 else (d1, d0)
    return cq.Workplane(obj=cq.Solid.makeCone(
        base / 2, top / 2, abs(h), cq.Vector(x, min(y0, y1), z), cq.Vector(0, 1, 0)))


def overlap_volume(a, b):
    """Volumen comun entre dos Workplane (0 si solo se tocan)."""
    return a.val().intersect(b.val()).Volume()


def hex_grid_points(a0, a1, b0, b1, f2f, rib):
    """Centros de una rejilla hexagonal (puntas sobre el eje a) que cabe
    completa en el rectangulo [a0, a1] x [b0, b1]. Columnas a lo largo de a
    separadas (f2f + rib) * cos30; filas a lo largo de b separadas f2f + rib,
    con media fila de desfase en columnas alternas."""
    s = f2f + rib
    r = f2f / math.sqrt(3)                 # radio circunscrito (punta)
    da = s * math.sqrt(3) / 2
    pts = []
    k = 0
    a = a0 + r
    while a <= a1 - r + 1e-9:
        b = b0 + f2f / 2 + (s / 2 if k % 2 else 0.0)
        while b <= b1 - f2f / 2 + 1e-9:
            pts.append((a, b))
            b += s
        a += da
        k += 1
    return pts


def hex_prisms(origin, a_dir, normal, pts, f2f, depth):
    """Prismas hexagonales para cortar una rejilla. El plano pasa por origin;
    a_dir es el eje de las puntas (y de la primera coordenada de pts), normal
    el eje del prisma; cada prisma va de -depth/2 a +depth/2 sobre el plano."""
    plane = cq.Plane(origin=origin, xDir=a_dir, normal=normal)
    wp = cq.Workplane(plane).workplane(offset=-depth / 2)
    return (wp.pushPoints(pts).polygon(6, 2 * f2f / math.sqrt(3))
            .extrude(depth))
