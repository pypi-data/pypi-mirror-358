import os
from os import PathLike
import pytest

from ewoksscxrd.tasks.createsetccdfiles import CreateSetCcdFiles


@pytest.fixture
def sample_set_file(tmp_path):
    """
    Create a dummy .set file.
    """
    path = tmp_path / "config.set"
    path.write_text("SET CONTENT")
    return str(path)


@pytest.fixture
def sample_ccd_file(tmp_path):
    """
    Create a dummy .ccd file.
    """
    path = tmp_path / "config.ccd"
    path.write_text("CCD CONTENT")
    return str(path)


@pytest.mark.parametrize(
    "src_file, ext, content",
    [
        ("sample_set_file", ".set", "SET CONTENT"),
        ("sample_ccd_file", ".ccd", "CCD CONTENT"),
    ],
    ids=["valid_set", "valid_ccd"],
)
def test_create_set_ccd_files_valid(
    tmp_path: PathLike, request, src_file, ext, content
):
    """
    Should copy .set or .ccd file and return saved_files_path.
    """
    src = request.getfixturevalue(src_file)
    # Define output target
    output = tmp_path / "outdir" / "base"
    # Ensure destination directory exists
    os.makedirs(os.path.dirname(str(output)), exist_ok=True)

    # Execute task
    task = CreateSetCcdFiles(
        inputs={"ccd_set_file": src, "output": str(output)},
    )
    task.execute()
    result = task.get_output_values()
    saved = result.get("saved_files_path", [])

    # Verify saved_files_path
    expected_file = os.path.join(
        os.path.dirname(str(output)), os.path.basename(str(output)) + ext
    )
    assert saved == [expected_file]
    # Verify file existence and content
    assert os.path.exists(expected_file)
    with open(expected_file, "r", encoding="iso-8859-1") as f:
        data = f.read()
    assert data == content


def test_create_set_ccd_files_missing(tmp_path: PathLike):
    """
    Should not save anything if source file does not exist.
    """
    missing = str(tmp_path / "nofile.set")
    output = tmp_path / "outdir" / "base"
    os.makedirs(os.path.dirname(str(output)), exist_ok=True)

    task = CreateSetCcdFiles(
        inputs={"ccd_set_file": missing, "output": str(output)},
    )
    task.execute()
    result = task.get_output_values()
    saved = result.get("saved_files_path", [])
    assert saved == []


def test_create_set_ccd_files_invalid_extension(tmp_path: PathLike):
    """
    Should not save anything if file has wrong extension.
    """
    wrong = tmp_path / "config.txt"
    wrong.write_text("TXT CONTENT")
    output = tmp_path / "outdir" / "base"
    os.makedirs(os.path.dirname(str(output)), exist_ok=True)

    task = CreateSetCcdFiles(
        inputs={"ccd_set_file": str(wrong), "output": str(output)},
    )
    task.execute()
    result = task.get_output_values()
    saved = result.get("saved_files_path", [])
    assert saved == []
