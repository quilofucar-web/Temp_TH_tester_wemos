"""Lectura minima de STL binarios de referencia (externalfiles/) con numpy.

No hay trimesh instalado; esto alcanza para medir y comparar."""
from pathlib import Path

import numpy as np

EXTERNAL = Path(__file__).resolve().parent.parent / "externalfiles"


def load_stl_triangles(path):
    """Regresa un array (n, 3, 3) con los vertices de cada triangulo."""
    data = Path(path).read_bytes()
    n = int(np.frombuffer(data[80:84], "<u4")[0])
    if 84 + n * 50 != len(data):
        raise ValueError(f"No es un STL binario valido: {path}")
    rec = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    return np.frombuffer(data[84:84 + n * 50], rec)["v"].astype(float)


def stl_volume(tris):
    """Volumen encerrado (teorema de la divergencia)."""
    return float(abs(np.einsum("ij,ij->i", tris[:, 0],
                               np.cross(tris[:, 1], tris[:, 2])).sum()) / 6)


def unique_vertices(tris, decimals=3):
    return np.unique(np.round(tris.reshape(-1, 3), decimals), axis=0)
