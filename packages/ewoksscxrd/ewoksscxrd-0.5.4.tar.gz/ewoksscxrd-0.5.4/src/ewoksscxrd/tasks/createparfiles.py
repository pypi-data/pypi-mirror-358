import os
import logging
from ewokscore import Task
from .utils import create_par_file

logger = logging.getLogger(__name__)


def _transform_beam(beam, width, height, detector_square_size):
    """
    Center a rectangular detector (width×height) into a square of size detector_square_size,
    then flip the Y axis.

    x_new = x_old + pad_x
    y_new = detector_square_size - (y_old + pad_y)

    where
      pad_x = (detector_square_size - width) / 2
      pad_y = (detector_square_size - height) / 2
    """
    x, y = float(beam[0]), float(beam[1])
    W, H = float(width), float(height)
    pad_x = (detector_square_size - W) / 2.0
    pad_y = (detector_square_size - H) / 2.0
    x_new = x + pad_x
    y_new = float(detector_square_size) - (y + pad_y)
    return [x_new, y_new]


def _format_rotation(original_line: str, distance, beam):
    parts = original_line.strip().split()
    header = " ".join(parts[:2])
    nums = [float(x) for x in parts[2:]]
    nums[3] = float(distance)
    nums[4], nums[5] = float(beam[0]), float(beam[1])
    body = "   ".join(f"{v:.5f}" for v in nums)
    return f"{header}   {body}"


class CreateParFiles(
    Task,
    input_names=["output", "par_file"],
    optional_input_names=[
        "distance",
        "wavelength",
        "polarization",
        "beam",
        "detector_width",
        "detector_height",
        "detector_square_size",
    ],
    output_names=["saved_files_path"],
):
    def run(self):
        output = self.get_input_value("output")
        par_file = self.get_input_value("par_file")
        saved_files = []

        ext = os.path.splitext(par_file)[-1].lower()
        dest_basename = os.path.basename(output) + ext
        dest_dir = os.path.dirname(output)
        dest_path = os.path.join(dest_dir, dest_basename)

        logger.info(f"Starting CreateParFiles for {par_file}")

        if not os.path.exists(par_file) or ext != ".par":
            logger.warning(f"Invalid .par file: {par_file}")
            self.outputs.saved_files_path = []
            return

        # optional overrides
        dist = self.get_input_value("distance", None)
        wl = self.get_input_value("wavelength", None)
        pol = self.get_input_value("polarization", None)
        beam = self.get_input_value("beam", None)
        det_w = self.get_input_value("detector_width", 2068)
        det_h = self.get_input_value("detector_height", 2162)
        det_sq = self.get_input_value("detector_square_size", 2164)

        # transform beam if dimensions provided
        if beam is not None and det_w is not None and det_h is not None:
            beam = _transform_beam(beam, det_w, det_h, det_sq)

        source = par_file
        # rewrite file content if any override provided
        if any(v is not None for v in (dist, wl, pol, beam)):
            logger.info("Applying provided parameters to .par content")
            with open(par_file, encoding="latin-1") as f:
                lines = f.readlines()
            new_lines = []
            for line in lines:
                stripped = line.lstrip()
                # 1) DETECTOR DISTANCE
                if dist is not None and stripped.startswith("§   - DETECTOR DISTANCE"):
                    new_lines.append(
                        f"§   - DETECTOR DISTANCE (MM):  {float(dist):.5f}\n"
                    )
                    continue
                # 2) WAVELENGTH USERSPECIFIED
                if wl is not None and stripped.startswith(
                    "§   - WAVELENGTH USERSPECIFIED"
                ):
                    new_lines.append(
                        f"§   - WAVELENGTH USERSPECIFIED (ANG): "
                        f"A1    {float(wl):.5f} A2    {float(wl):.5f}  B1    {float(wl):.5f}\n"
                    )
                    continue
                # 3) CRYSTALLOGRAPHY WAVELENGTH
                if wl is not None and line.startswith("CRYSTALLOGRAPHY WAVELENGTH"):
                    new_lines.append(
                        f"CRYSTALLOGRAPHY WAVELENGTH    "
                        f"{float(wl):.5f}    {float(wl):.5f}    {float(wl):.5f}\n"
                    )
                    continue
                # 4) POLARISATION FACTOR
                if pol is not None and stripped.startswith("§   - POLARISATION FACTOR"):
                    new_lines.append(f"§   - POLARISATION FACTOR    {float(pol):.5f}\n")
                    continue
                # 5) DETECTOR ZERO
                if beam is not None and stripped.startswith(
                    "§   - DETECTOR ZERO (PIX, 1X1 BINNING)"
                ):
                    new_lines.append(
                        f"§   - DETECTOR ZERO (PIX, 1X1 BINNING): "
                        f"X {float(beam[0]):.5f} Y {float(beam[1]):.5f}\n"
                    )
                    continue
                # 6) ROTATION DETECTORORIENTATION
                if dist is not None and line.startswith("ROTATION DETECTORORIENTATION"):
                    new_lines.append(_format_rotation(line, dist, beam) + "\n")
                    continue
                # keep unchanged
                new_lines.append(line)
            # write temp file
            os.makedirs(dest_dir, exist_ok=True)
            temp = os.path.join(dest_dir, "temp.par")
            with open(temp, "w", encoding="latin-1") as f:
                f.writelines(new_lines)
            source = temp

        # forward kwargs
        kwargs = {}
        if dist is not None:
            kwargs["distance"] = dist
        if wl is not None:
            kwargs["wavelength"] = wl
        if pol is not None:
            kwargs["polarization"] = pol
        if beam is not None:
            kwargs["beam"] = beam
        if det_w is not None:
            kwargs["detector_width"] = det_w
        if det_h is not None:
            kwargs["detector_height"] = det_h
        if det_sq is not None:
            kwargs["detector_square_size"] = det_sq

        # call create_par_file
        os.makedirs(dest_dir, exist_ok=True)
        try:
            create_par_file(source, dest_dir, dest_basename, **kwargs)
        except TypeError:
            create_par_file(source, dest_dir, dest_basename)

        saved_files.append(dest_path)
        self.outputs.saved_files_path = saved_files
        logger.info(f"CreateParFiles completed: {saved_files}")
