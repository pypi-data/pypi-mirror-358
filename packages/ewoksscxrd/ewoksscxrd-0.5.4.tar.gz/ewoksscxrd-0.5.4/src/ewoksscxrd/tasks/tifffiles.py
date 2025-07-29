import os
import logging
from silx.io import open as silx_open
from ewokscore import Task
from PIL import Image, TiffImagePlugin
from concurrent.futures import ProcessPoolExecutor, as_completed

try:
    import hdf5plugin  # noqa: F401
except ImportError:
    pass

logger = logging.getLogger(__name__)


def save_tiff_worker(frame, file_path, tiff_info_dict):
    """Worker to save a single TIFF frame."""
    im = Image.fromarray(frame)
    tif_info = TiffImagePlugin.ImageFileDirectory_v2()
    for key, value in tiff_info_dict.items():
        tif_info[key] = value
    im.save(file_path, format="TIFF", tiffinfo=tif_info)
    return file_path


class TiffFiles(
    Task,
    input_names=[
        "images",
        "output",
    ],
    optional_input_names=["detector_name"],
    output_names=["output_path", "images_list"],
):
    """
    Reads an HDF5 file with frames, extracts each individual frame,
    and saves them as TIFF images in a folder called 'xdi'.
    The TIFF images will have a key called imageDescription, default is `eiger`,
    if the detector name is supplied, it will be set accordingly

    The HDF5 file is assumed to contain a 2D or 3D dataset (n_frames, height, width)
    at the dataset path "/entry_0000/measurement/data". The output folder `xdi`
    is created in PROCESSED_DATA/sample/sample_dataset/scan0001.
    """

    def run(self):
        args = self.inputs

        # Getting the dataset name from the input "output"
        parts = args.output.split(os.sep)
        pd_idx = parts.index("PROCESSED_DATA")
        base_name = parts[pd_idx + 2]

        processed_data_dir = os.path.join(os.path.dirname(args.output), "xdi")
        os.makedirs(processed_data_dir, exist_ok=True)

        with silx_open(args.images[0]) as h5file:
            ds = h5file["/entry_0000/measurement/data"]
            n_frames = ds.shape[0]

            tiff_info_dict = {
                270: (
                    f"detector={args.detector_name}"
                    if args.detector_name
                    else "detector=eiger"
                )
            }

            # Use ProcessPoolExecutor for parallel TIFF writing
            saved_files = []
            with ProcessPoolExecutor() as executor:
                futures = []
                for i in range(n_frames):
                    frame = ds[i]
                    tiff_file_name = f"{base_name}_{i:04d}.tif"
                    file_path = os.path.join(processed_data_dir, tiff_file_name)
                    futures.append(
                        executor.submit(
                            save_tiff_worker, frame, file_path, tiff_info_dict
                        )
                    )
                for fut in as_completed(futures):
                    saved_files.append(fut.result())

        # Sort the files in order (as_completed is unordered)
        saved_files.sort()
        self.outputs.output_path = processed_data_dir
        self.outputs.images_list = saved_files
