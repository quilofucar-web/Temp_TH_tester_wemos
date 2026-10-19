import cadquery as cq
import pytest

from cq_utils import (check_valid, export_assembly_versioned, export_versioned,
                      next_version_number, versioned)


def test_next_version_number_empty_dir(tmp_path):
    assert next_version_number(tmp_path / "foo.stl") == 1


def test_next_version_number_skips_to_max(tmp_path):
    (tmp_path / "foo_1.stl").write_text("x")
    (tmp_path / "foo_3.stl").write_text("x")
    (tmp_path / "foobar_9.stl").write_text("x")   # otro nombre base: no cuenta
    assert next_version_number(tmp_path / "foo.stl") == 4


def test_versioned_inserts_suffix():
    assert versioned("out/foo.stl", 3).replace("\\", "/") == "out/foo_3.stl"


def test_check_valid_raises_on_invalid():
    class Fake:
        def val(self):
            class V:
                def isValid(self):
                    return False
            return V()
    with pytest.raises(RuntimeError):
        check_valid(Fake(), "fake")


def test_export_versioned_writes_stl_and_step_same_number(tmp_path):
    box = cq.Workplane("XY").box(10, 10, 10)
    stl, step = export_versioned(box, "cubo", tmp_path)
    assert stl.endswith("cubo_1.stl") and step.endswith("cubo_1.step")
    (tmp_path / "cubo_1.stl").unlink()          # aunque falte el STL, el STEP _1 existe
    stl2, step2 = export_versioned(box, "cubo", tmp_path)
    assert stl2.endswith("cubo_2.stl") and step2.endswith("cubo_2.step")


def test_export_assembly_versioned_numbers_step(tmp_path):
    assy = cq.Assembly(cq.Workplane("XY").box(5, 5, 5), name="a")
    p1 = export_assembly_versioned(assy, "ens", tmp_path)
    p2 = export_assembly_versioned(assy, "ens", tmp_path)
    assert p1.endswith("ens_1.step") and p2.endswith("ens_2.step")
