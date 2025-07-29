import os
from os import PathLike
import pytest

import ewoksscxrd.tasks.createrunfiles as module
from ewoksscxrd.tasks.createrunfiles import CreateRunFiles


@pytest.fixture
def fake_run_params():
    """
    Dummy run parameters object or dict.
    """
    return {"param1": "value1", "param2": 2}


@pytest.fixture
def stub_create_run_file(monkeypatch, tmp_path):
    """
    Stub out create_run_file to record inputs and write a dummy .run file.
    """
    calls = {}

    def fake_create_run_file(scans, dest_dir, basename):
        # Ensure destination directory exists
        os.makedirs(dest_dir, exist_ok=True)
        # Record the arguments
        calls["scans"] = scans
        calls["dest_dir"] = dest_dir
        calls["basename"] = basename
        # Write dummy .run file
        filepath = os.path.join(dest_dir, basename + ".run")
        with open(filepath, "w") as f:
            f.write("# dummy run file\n")

    monkeypatch.setattr(module, "create_run_file", fake_create_run_file)
    return calls


def test_create_run_files_success(
    tmp_path: PathLike, fake_run_params, stub_create_run_file
):
    """
    Verify CreateRunFiles invokes create_run_file with correct args,
    writes a .run file, and returns the expected saved_files_path.
    """
    # Setup output path
    output = tmp_path / "dirA" / "dirB" / "myrun"
    # Prepare task
    task = CreateRunFiles(
        inputs={
            "output": str(output),
            "run_parameters": fake_run_params,
        },
    )
    # Execute task
    task.execute()
    result = task.get_output_values()

    # Capture outputs
    saved = result.get("saved_files_path", [])

    # Check stub was called correctly
    expected_basename = os.path.basename(str(output))
    # scans should be a list of list containing run_parameters
    assert stub_create_run_file["scans"] == [[fake_run_params]]
    # Destination dir is parent of output
    expected_dest_dir = os.path.dirname(str(output))
    assert stub_create_run_file["dest_dir"] == expected_dest_dir
    assert stub_create_run_file["basename"] == expected_basename

    # Verify saved_files_path includes the .run file
    expected_file = os.path.join(expected_dest_dir, expected_basename + ".run")
    assert saved == [expected_file]
    # And the file exists with dummy content
    assert os.path.exists(expected_file)
    with open(expected_file, "r") as f:
        content = f.read()
    assert "# dummy run file" in content
