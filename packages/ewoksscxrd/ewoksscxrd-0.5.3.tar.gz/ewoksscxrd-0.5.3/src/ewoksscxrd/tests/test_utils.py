import os
import h5py
import numpy as np
import pytest
from types import SimpleNamespace

import ewoksscxrd.tasks.utils as utils


# --- Tests for create_run_file ---
@pytest.fixture
def stub_crysalis(monkeypatch, tmp_path):
    """
    Stub crysalis module to record calls and simulate file creation.
    """
    calls = {}

    # Fake RunHeader
    def fake_RunHeader(name, dirpath, one):
        calls["RunHeader"] = (name, dirpath, one)
        return SimpleNamespace()

    # Fake RunDscr
    def fake_RunDscr(val):
        calls.setdefault("RunDscr", []).append(val)
        return SimpleNamespace()

    # Fake SCAN_AXIS
    fake_scan_axis = {"OMEGA": 42}

    # Fake saveRun writes a .run file
    def fake_saveRun(runname, header, runFile):
        calls["saveRun"] = (runname, header, runFile)
        # create a dummy .run file
        with open(runname + ".run", "w") as f:
            f.write("# run file")

    # Fake saveCrysalisExpSettings
    def fake_saveCrysalisExpSettings(dirpath):
        calls["saveCrysalisExpSettings"] = dirpath

    # Monkeypatch
    monkeypatch.setattr(
        utils,
        "crysalis",
        SimpleNamespace(
            RunHeader=fake_RunHeader,
            RunDscr=fake_RunDscr,
            SCAN_AXIS=fake_scan_axis,
            saveRun=fake_saveRun,
            saveCrysalisExpSettings=fake_saveCrysalisExpSettings,
        ),
    )
    return calls


def test_create_run_file_success(stub_crysalis, tmp_path):
    scans = [
        [{"kappa": 1, "omega_start": 0, "omega_end": 10, "domega": 0.5, "count": 5}]
    ]
    crys_dir = str(tmp_path / "crys")
    basename = "run1"
    os.makedirs(crys_dir, exist_ok=True)

    # Call utility
    utils.create_run_file(scans, crys_dir, basename)

    # Assertions
    calls = stub_crysalis
    # RunHeader called with encoded names
    assert calls["RunHeader"][0] == basename.encode()
    assert calls["RunHeader"][1] == crys_dir.encode()
    # RunDscr called once with 0
    assert calls["RunDscr"] == [0]
    # saveRun called with correct runname
    runname, header, runFile = calls["saveRun"]
    assert runname == os.path.join(crys_dir, basename)
    # .run file created
    assert os.path.exists(runname + ".run")
    # saveCrysalisExpSettings called
    assert calls["saveCrysalisExpSettings"] == crys_dir


# --- Tests for create_par_file ---
@pytest.fixture
def sample_par(tmp_path):
    path = tmp_path / "orig.par"
    content = [
        "LINE1\n",
        "FILE CHIP oldfile.ext\n",
        "LINE3\n",
    ]
    path.write_text("".join(content), encoding="iso-8859-1")
    return str(path)


def test_create_par_file(sample_par, tmp_path):
    dest_dir = str(tmp_path / "out")
    basename = "new.par"
    os.makedirs(dest_dir, exist_ok=True)
    utils.create_par_file(sample_par, dest_dir, basename)
    new_path = os.path.join(dest_dir, basename)
    assert os.path.exists(new_path)

    with open(new_path, encoding="iso-8859-1") as f:
        text = f.readlines()
    # First and third lines unchanged
    assert text[0] == "LINE1\n"
    # FILE CHIP line replaced
    assert text[1].startswith("FILE CHIP new.ccd")
    assert text[2] == "LINE3\n"


# --- Tests for read_dataset ---
@pytest.fixture
def sample_h5(tmp_path):
    path = tmp_path / "data.h5"
    arr = np.arange(24).reshape(2, 3, 4)
    with h5py.File(path, "w") as f:
        grp = f.require_group("entry_0000/measurement")
        grp.create_dataset("data", data=arr)
    return str(path), arr


def test_read_dataset(sample_h5):
    path, arr = sample_h5
    out = utils.read_dataset(path)
    assert isinstance(out, np.ndarray)
    assert out.shape == arr.shape
    assert np.array_equal(out, arr)


# --- Tests for subtract_frame_inplace ---
@pytest.fixture
def sample_frame():
    # frame shape (2,H,W)
    H, W = 2, 2
    dtype = np.uint32
    frame = np.zeros((2, H, W), dtype=dtype)
    # frame[0]
    frame[0] = np.array([[100, 0], [0, 0]], dtype=dtype)
    # frame[1]
    frame[1] = np.array([[1, 10], [np.iinfo(dtype).max, 2]], dtype=dtype)
    return frame


def test_subtract_frame_inplace(sample_frame):
    """
    Test subtract_frame_inplace with threshold set to max uint32.
    """
    frame = sample_frame.copy()
    scale = 2
    maxv = np.iinfo(np.uint32).max
    thresh = maxv  # threshold always max uint32
    utils.subtract_frame_inplace(frame, scale, thresh)

    # pixel [0,0]: frame1=1<thresh => sub:100-2*1=98
    assert frame[0, 0, 0] == 98
    # [0,1]: frame1=10<thresh => sub:0-2*10 = -20 clamped to 0
    assert frame[0, 0, 1] == 0
    # [1,0]: frame1=max => saturate => max
    assert frame[0, 1, 0] == maxv
    # [1,1]: frame1=2<thresh => sub:0-2*2 = -4 clamped to 0
    assert frame[0, 1, 1] == 0


def test_subtract_images_parallel_valid():
    # create data shape (2,2,2,2)
    data = np.zeros((2, 2, 2, 2), dtype=np.uint32)
    # fill frame0
    data[:, 0] = 100
    # frame1 values: first frame below thresh, second above
    data[0, 1] = 1
    data[1, 1] = 10
    out = utils.subtract_images_inplace_parallel(data, scale_factor=1, masking_value=5)
    # out shape: (2,2,2)
    assert out.shape == (2, 2, 2)
    # first frame: 100-1=99
    assert out[0, 0, 0] == 99
    # second frame: 100+10=110
    assert out[1, 0, 0] == 110


@pytest.mark.parametrize(
    "arr",
    [
        np.zeros((2, 2, 2), dtype=np.uint32),  # 3D
        np.zeros((2, 1, 2, 2), dtype=np.uint32),  # too small dim1
    ],
)
def test_subtract_images_parallel_invalid(arr):
    with pytest.raises(ValueError):
        utils.subtract_images_inplace_parallel(arr, 1, 5)


# --- Tests for create_header_from_file ---
@pytest.fixture
def sample_header_h5(tmp_path):
    path = tmp_path / "hdr.h5"
    with h5py.File(path, "w") as f:
        entry = f.create_group("entry_0000")
        entry.create_dataset("title", data=np.array("T", dtype="S1"))
        # create instrument group
        inst = entry.create_group("instr1")
        det = inst.create_group("det1")
        acq = det.create_group("acquisition")
        acq.create_dataset("exposure_time", data=1.23)
        acq.create_dataset("latency_time", data=0.45)
        acq.create_dataset("trigger_mode", data=np.array("Mode", dtype="S4"))
        # no nb_frames_per_trigger to test fallback
        info = det.create_group("detector_information")
        info.create_dataset("model", data=np.array("M", dtype="S1"))
        info.create_dataset("plugin", data=np.array("P", dtype="S1"))
        pix = info.create_group("pixel_size")
        pix.create_dataset("xsize", data=0.1)
        pix.create_dataset("ysize", data=0.2)
        # data dataset
        det.create_dataset("data", shape=(10, 20, 30), dtype="u4")
    return str(path)


def test_create_header_from_file(sample_header_h5):
    hdr = utils.create_header_from_file(sample_header_h5)
    # Check some keys
    assert hdr["title"] == "T"
    assert hdr["instrument"] == "instr1"
    assert hdr["detector"] == "det1"
    assert hdr["exposure_time"] == 1.23
    assert hdr["latency_time"] == 0.45
    assert hdr["trigger_mode"] == "Mode"
    assert hdr["model"] == "M"
    assert hdr["type"] == "P"
    assert hdr["pixel_size_x"] == 0.1
    assert hdr["pixel_size_y"] == 0.2
    assert "image_roi" in hdr
    # defaults
    assert hdr["image_bin"] == "<1x1>"


# --- Tests for write_lima_images ---
def test_write_lima_images(tmp_path, monkeypatch):
    # Prepare data and header
    data = np.arange(2 * 3 * 4, dtype=np.uint32).reshape(2, 3, 4)
    header = {
        "title": "test",
        "instrument": "ESRF-ID15B",
        "detector": "mydet",
        "exposure_time": 0.5,
        "latency_time": 0.1,
        "mode": "Single",
        "trigger_mode": "Trig",
        "model": "Mod",
        "type": "Typ",
        "pixel_size_x": 0.1,
        "pixel_size_y": 0.2,
        "image_roi": "<0,0>-<3x4>",
    }
    out = tmp_path / "out.nxs"
    # Ensure hdf5plugin is None to force gzip
    monkeypatch.setattr(utils, "hdf5plugin", None)
    # Execute write
    utils.write_lima_images(data, str(out), header)
    # Open with h5py and verify dataset exists
    with h5py.File(str(out), "r") as f:
        # path '/entry_0000/ESRF-ID15B/mydet/data'
        d = f["/entry_0000/ESRF-ID15B/mydet/data"]
        assert d.shape == (2, 3, 4)
        assert d.dtype == np.uint32
        # verify attribute
        assert d.attrs["interpretation"] == "image"
    # Check entry default attr
    with h5py.File(str(out), "r") as f:
        entry = f["/entry_0000"]
        assert "default" in entry.attrs
