import os
import pytest
import numpy as np
from PIL import Image

from ewoksscxrd.tasks.dataportal import DataPortal


def create_dummy_image(shape=(10, 10)) -> np.ndarray:
    """Helper: create a gradient float image array."""
    return np.linspace(0, 255, num=shape[0] * shape[1], dtype=float).reshape(shape)


@pytest.fixture
def simple_image() -> np.ndarray:
    """Fixture providing a basic gradient image."""
    return create_dummy_image((10, 10))


@pytest.fixture
def output_paths(tmp_path):
    """Fixture providing a base output path and expected gallery dir."""
    base = tmp_path / "proc" / "sample"
    output_file = base / "image.tif"
    gallery_dir = base / "gallery"
    return {"output": str(output_file), "gallery_dir": str(gallery_dir)}


@pytest.fixture(autouse=True)
def stub_store_to_icat(monkeypatch):
    """Prevent real ICAT calls"""
    monkeypatch.setattr(DataPortal, "store_to_icat", lambda self: None)


@pytest.mark.parametrize(
    "binning, shape",
    [
        (1, (10, 10)),
        (2, (5, 5)),
    ],
)
def test_save_to_gallery_binning_and_defaults(
    simple_image, output_paths, binning, shape
):
    gallery_dir = output_paths["gallery_dir"]
    os.makedirs(gallery_dir, exist_ok=True)
    gallery_file = os.path.join(gallery_dir, "image_average.png")

    task = DataPortal(
        inputs={
            "image": simple_image,
            "output": output_paths["output"],
            "gallery_output_binning": binning,
            "gallery_overwrite": True,
        }
    )
    # Initialize attributes for save_to_gallery
    task.gallery_overwrite = True
    task.gallery_output_binning = binning

    task.save_to_gallery(gallery_file, simple_image)
    assert os.path.exists(gallery_file)
    with Image.open(gallery_file) as img:
        assert img.mode == "L"
        assert img.size == shape


def test_save_to_gallery_bounds(simple_image, output_paths):
    bounds = (50.0, 200.0)
    gallery_dir = output_paths["gallery_dir"]
    os.makedirs(gallery_dir, exist_ok=True)
    gallery_file = os.path.join(gallery_dir, "image_average.png")

    task = DataPortal(
        inputs={
            "image": simple_image,
            "output": output_paths["output"],
            "gallery_output_binning": 1,
            "gallery_overwrite": True,
        }
    )
    task.gallery_overwrite = True
    task.gallery_output_binning = 1

    task.save_to_gallery(gallery_file, simple_image, bounds=bounds)
    assert os.path.exists(gallery_file)


@pytest.mark.parametrize("dims", [(2, 2, 2), (3,)])
def test_save_to_gallery_invalid_dims(output_paths, dims):
    bad_image = np.zeros(dims)
    gallery_dir = output_paths["gallery_dir"]
    os.makedirs(gallery_dir, exist_ok=True)
    gallery_file = os.path.join(gallery_dir, "image_average.png")

    task = DataPortal(
        inputs={
            "image": bad_image,
            "output": output_paths["output"],
        }
    )
    task.gallery_overwrite = True
    task.gallery_output_binning = 1

    with pytest.raises(ValueError):
        task.save_to_gallery(gallery_file, bad_image)


def test_save_no_overwrite(simple_image, output_paths):
    gallery_dir = output_paths["gallery_dir"]
    os.makedirs(gallery_dir, exist_ok=True)
    gallery_file = os.path.join(gallery_dir, "image_average.png")
    with Image.new("L", (10, 10)) as dummy:
        dummy.save(gallery_file)

    task = DataPortal(
        inputs={
            "image": simple_image,
            "output": output_paths["output"],
            "gallery_output_binning": 1,
            "gallery_overwrite": False,
        }
    )
    task.gallery_overwrite = False
    task.gallery_output_binning = 1

    with pytest.raises(OSError):
        task.save_to_gallery(gallery_file, simple_image)


def test_run_creates_gallery_and_sets_output(simple_image, output_paths):
    task = DataPortal(
        inputs={
            "image": simple_image,
            "output": output_paths["output"],
        }
    )
    task.execute()
    result = task.get_output_values()
    out_path = result.get("gallery_file_path")
    assert os.path.exists(out_path)
    assert out_path.endswith("_average.png")
