from pathlib import Path
from os import PathLike
import numpy as np
import h5py
import pytest

from ewoksscxrd.tasks.averageframes import AverageFrames

TEST_DATA = Path(__file__).parent / "data" / "eiger_0000.h5"


@pytest.fixture(scope="module")
def eiger_h5_path():
    """
    Provide the path to the existing Eiger HDF5 test file.
    """
    assert TEST_DATA.exists(), f"Test data file not found: {TEST_DATA}"
    return str(TEST_DATA)


@pytest.fixture
def invalid_h5_2d(tmp_path):
    """
    Create a temporary HDF5 file containing a 2D dataset to trigger the dimension check.
    """
    path = tmp_path / "invalid_2d.h5"
    data = np.arange(12, dtype=float).reshape(3, 4)
    with h5py.File(path, "w") as f:
        grp = f.require_group("entry_0000/measurement")
        grp.create_dataset("data", data=data)
    return str(path)


def test_average_frames_with_eiger_file(tmp_path: PathLike, eiger_h5_path):
    """
    Validate that averageFrames correctly processes the provided Eiger HDF5 file,
    writes an EDF file, and returns the averaged image and output path.
    """
    # Use the existing test HDF5
    output_base = tmp_path / "lvl1" / "lvl2" / "lvl3" / "avg"
    task = AverageFrames(
        inputs={
            "images": [eiger_h5_path],
            "output": str(output_base),
        },
    )
    task.execute()
    result = task.get_output_values()

    # Check returned values
    assert result["output_path"] == str(output_base)
    avg_image = result["image"]
    # Read raw data to compute expected average
    with h5py.File(eiger_h5_path, "r") as f:
        frames = f["/entry_0000/measurement/data"][()]
    expected = np.mean(frames, axis=0)
    assert isinstance(avg_image, np.ndarray)
    assert avg_image.shape == expected.shape
    assert np.allclose(avg_image, expected)

    # Verify EDF file saved in edf_PX directory
    processed_dir = Path(output_base).parents[2] / "edf_PX"
    edf_file = processed_dir / (output_base.name + ".edf")
    assert processed_dir.is_dir()
    assert edf_file.exists(), f"EDF output not found at {edf_file}"


def test_average_frames_invalid_dimensions(tmp_path: PathLike, invalid_h5_2d):
    """
    Ensure averageFrames.run raises ValueError when the dataset is not 3D.
    """
    output_base = tmp_path / "out"
    task = AverageFrames(
        inputs={
            "images": [invalid_h5_2d],
            "output": str(output_base),
        },
    )
    # Directly invoke run() to catch ValueError before execute() wraps it
    with pytest.raises(ValueError) as excinfo:
        task.run()
    assert "Expected a 3D array" in str(excinfo.value)
