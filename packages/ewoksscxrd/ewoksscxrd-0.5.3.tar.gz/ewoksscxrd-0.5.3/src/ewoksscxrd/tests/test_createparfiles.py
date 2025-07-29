import os
from os import PathLike
import pytest

import ewoksscxrd.tasks.createparfiles as module
from ewoksscxrd.tasks.createparfiles import CreateParFiles


@pytest.fixture
def sample_par_file(tmp_path):
    """
    Creates a valid .par file for testing.
    """
    par = tmp_path / "sample.par"
    # include a line that matches the distance pattern
    par.write_text("# header line\n   - DETECTOR DISTANCE (MM): 100.00000\n")
    return str(par)


@pytest.fixture
def stub_create_par_file(monkeypatch, tmp_path):
    """
    Stub out create_par_file to record inputs and write a dummy .par file.
    """
    calls = {}

    def fake_create_par_file(src_file, dest_dir, basename):
        # Ensure destination directory exists
        os.makedirs(dest_dir, exist_ok=True)
        # Record the arguments
        calls["src_file"] = src_file
        calls["dest_dir"] = dest_dir
        calls["basename"] = basename
        # Write dummy .par file
        filepath = os.path.join(dest_dir, basename)
        with open(filepath, "w") as f:
            f.write("# dummy par file\n")

    # patch the function in our task module
    monkeypatch.setattr(module, "create_par_file", fake_create_par_file)
    return calls


def test_create_par_files_success(
    tmp_path: PathLike, sample_par_file, stub_create_par_file
):
    """
    Verify CreateParFiles invokes create_par_file correctly,
    writes a .par file, and populates saved_files_path.
    """
    output = tmp_path / "dirA" / "dirB" / "output_name"

    task = CreateParFiles(
        inputs={
            "par_file": sample_par_file,
            "output": str(output),
        },
    )
    task.execute()
    result = task.get_output_values()
    saved = result.get("saved_files_path", [])

    expected_basename = os.path.basename(str(output)) + ".par"
    expected_dest_dir = os.path.dirname(str(output))
    expected_src = sample_par_file  # since no optional args, direct input

    assert stub_create_par_file["src_file"] == expected_src
    assert stub_create_par_file["dest_dir"] == expected_dest_dir
    assert stub_create_par_file["basename"] == expected_basename

    expected_file = os.path.join(expected_dest_dir, expected_basename)
    assert saved == [expected_file]
    assert os.path.exists(expected_file)
    with open(expected_file, "r") as f:
        assert "# dummy par file" in f.read()


def test_create_par_files_missing(tmp_path: PathLike):
    """
    If the .par file does not exist, no files are saved.
    """
    missing = str(tmp_path / "does_not_exist.par")
    output = tmp_path / "out"

    task = CreateParFiles(
        inputs={
            "par_file": missing,
            "output": str(output),
        },
    )
    task.execute()
    result = task.get_output_values()
    assert result.get("saved_files_path", []) == []


def test_create_par_files_wrong_extension(tmp_path: PathLike):
    """
    If the file exists but has the wrong extension, no files are saved.
    """
    wrong = tmp_path / "file.txt"
    wrong.write_text("not par")
    output = tmp_path / "out"

    task = CreateParFiles(
        inputs={
            "par_file": str(wrong),
            "output": str(output),
        },
    )
    task.execute()
    result = task.get_output_values()
    assert result.get("saved_files_path", []) == []


def test_create_par_files_with_distance(
    tmp_path: PathLike, sample_par_file, stub_create_par_file
):
    """
    If an optional 'distance' is provided, we should rewrite via temp.par
    and stub_create_par_file should see src_file ending in temp.par.
    """
    output = tmp_path / "dirX" / "outname"
    new_distance = 250.5

    task = CreateParFiles(
        inputs={
            "par_file": sample_par_file,
            "output": str(output),
            "distance": new_distance,
        },
    )
    task.execute()
    result = task.get_output_values()
    saved = result.get("saved_files_path", [])

    expected_dest_dir = os.path.dirname(str(output))
    expected_basename = os.path.basename(str(output)) + ".par"

    # The stub should be called with src_file pointing to temp.par
    assert stub_create_par_file["src_file"].endswith(
        os.path.join(expected_dest_dir, "temp.par")
    )
    assert stub_create_par_file["dest_dir"] == expected_dest_dir
    assert stub_create_par_file["basename"] == expected_basename

    expected_file = os.path.join(expected_dest_dir, expected_basename)
    assert saved == [expected_file]
    assert os.path.exists(expected_file)
