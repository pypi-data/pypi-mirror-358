import os
from pathlib import Path
from os import PathLike
import pytest
import h5py
import numpy as np
from PIL import Image

from ewoksscxrd.tasks.tifffiles import TiffFiles

# Path to existing Eiger HDF5 test file
EIGER_FILE = Path(__file__).parent / "data" / "eiger_0000.h5"


@pytest.fixture(scope="module")
def eiger_h5_path():
    """
    Fixture providing the path to the existing Eiger HDF5 file under tests/data.
    """
    assert EIGER_FILE.exists(), f"Test data file not found: {EIGER_FILE}"
    return str(EIGER_FILE)


def test_tiff_files_default_detector(tmp_path: PathLike, eiger_h5_path):
    """
    Validate TiffFiles with default detector name (eiger), using existing Eiger HDF5.
    """
    # Read frames from the EIGER file
    with h5py.File(eiger_h5_path, "r") as f:
        frames = f["/entry_0000/measurement/data"][()]

    # Construct output path containing PROCESSED_DATA/.../scan0001
    output = tmp_path / "PROCESSED_DATA" / "sample" / "dataset" / "scan0001"

    task = TiffFiles(
        inputs={
            "images": [eiger_h5_path],
            "output": str(output),
        },
    )
    task.execute()
    result = task.get_output_values()

    processed_dir = result["output_path"]
    expected_dir = os.path.join(os.path.dirname(str(output)), "xdi")
    assert processed_dir == expected_dir

    images_list = result["images_list"]
    assert len(images_list) == frames.shape[0]

    for idx, img_path in enumerate(images_list):
        assert os.path.exists(img_path)
        with Image.open(img_path) as im:
            desc = im.tag_v2.get(270)
            arr = np.array(im)
            arr = np.array(im)
            arr = arr.astype(frames.dtype)
        assert desc == "detector=eiger"
        assert np.array_equal(arr, frames[idx])


def test_tiff_files_with_custom_detector(tmp_path: PathLike, eiger_h5_path):
    """
    Validate TiffFiles with a provided detector_name using existing Eiger HDF5.
    """
    task = TiffFiles(
        inputs={
            "images": [eiger_h5_path],
            "output": str(tmp_path / "PROCESSED_DATA" / "X" / "Y" / "Z"),
            "detector_name": "mycam",
        },
    )
    task.execute()
    result = task.get_output_values()

    images_list = result["images_list"]
    assert images_list, "No TIFF images created"

    for img_path in images_list:
        with Image.open(img_path) as im:
            desc = im.tag_v2.get(270)
        assert desc == "detector=mycam"
