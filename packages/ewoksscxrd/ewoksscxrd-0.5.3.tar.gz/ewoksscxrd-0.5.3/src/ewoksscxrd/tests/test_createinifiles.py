import os
from os import PathLike
import pytest

from ewoksscxrd.tasks.createinifiles import CreateIniFiles


@pytest.mark.parametrize(
    "exists, ext, expected_count",
    [
        (True, ".ini", 1),
        (True, ".INI", 1),
        (True, ".txt", 0),
        (False, ".ini", 0),
    ],
    ids=[
        "valid_ini",
        "valid_ini_uppercase",
        "invalid_extension",
        "missing_file",
    ],
)
def test_create_ini_files_various(
    tmp_path: PathLike, exists: bool, ext: str, expected_count: int
):
    """
    Test createIniFiles task with different scenarios:
      - existing .ini file (lowercase)
      - existing .INI file (uppercase)
      - existing non-.ini file
      - missing .ini file
    """
    # Setup source file path
    filename = f"config{ext}"
    src = tmp_path / filename
    if exists:
        # Write dummy ini content
        src.write_text("[section]\nkey=value")

    # Define output target (output path is used for directory resolution)
    output_target = tmp_path / "output_dir" / "ignored.ini"

    # Ensure the output directory exists so the copy won't fail
    os.makedirs(os.path.dirname(str(output_target)), exist_ok=True)

    # Execute the task
    task = CreateIniFiles(
        inputs={
            "ini_file": str(src),
            "output": str(output_target),
        },
    )
    task.execute()
    result = task.get_output_values()

    saved = result.get("saved_files_path", [])
    # Verify number of saved files
    assert len(saved) == expected_count

    if expected_count == 1:
        # Check that the file was copied to the expected destination
        expected_path = str(tmp_path / "output_dir" / filename)
        assert saved == [expected_path]
        assert os.path.exists(expected_path)
    else:
        # No files should be copied
        assert saved == []
