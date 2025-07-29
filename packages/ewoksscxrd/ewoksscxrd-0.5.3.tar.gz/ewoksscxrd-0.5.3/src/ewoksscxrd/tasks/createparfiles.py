import os
import re
import logging
from ewokscore import Task
from .utils import create_par_file

logger = logging.getLogger(__name__)

# Mapping of user-friendly parameter keys to regex patterns and formatting functions
PARAM_MAPPING = {
    "distance": {
        "pattern": re.compile(r"^(§?\s*-\s*DETECTOR DISTANCE.*)$", re.IGNORECASE),
        "formatter": lambda v: f"   - DETECTOR DISTANCE (MM): {float(v):.5f}",
    },
    "energy": {
        "pattern": re.compile(r"^(§?CRYSTALLOGRAPHY\s+WAVELENGTH.*)$", re.IGNORECASE),
        "formatter": lambda v: f"CRYSTALLOGRAPHY WAVELENGTH    {float(v):.5f} {float(v):.5f} {float(v):.5f}",
    },
    "wavelength": {
        "pattern": re.compile(
            r"^(§?\s*-\s*WAVELENGTH USERSPECIFIED.*)$", re.IGNORECASE
        ),
        "formatter": lambda v: f"   - WAVELENGTH USERSPECIFIED (ANG): A1    {float(v):.5f} A2    {float(v):.5f}  B1    {float(v):.5f}",
    },
    "polarization": {
        "pattern": re.compile(r"^(§?\s*-\s*POLARISATION FACTOR.*)$", re.IGNORECASE),
        "formatter": lambda v: f"   - POLARISATION FACTOR    {float(v):.5f}",
    },
    "beam": {
        "pattern": re.compile(
            r"^(§?\s*-\s*DETECTOR ZERO \(PIX, 1X1 BINNING\).*)$", re.IGNORECASE
        ),
        "formatter": lambda v: f"   - DETECTOR ZERO (PIX, 1X1 BINNING): X {float(v[1]):.5f} Y {float(v[0]):.5f}",
    },
}


class CreateParFiles(
    Task,
    input_names=["output", "par_file"],
    optional_input_names=list(PARAM_MAPPING.keys()),
    output_names=["saved_files_path"],
):
    def run(self):
        # Required inputs
        output = self.get_input_value("output")
        par_file = self.get_input_value("par_file")
        saved_files = []

        # Paths
        ext = os.path.splitext(par_file)[-1].lower()
        dest_basename = os.path.basename(output) + ext
        dest_dir = os.path.dirname(output)
        dest_path = os.path.join(dest_dir, dest_basename)

        logger.info(f"Starting CreateParFiles for {par_file}")
        logger.debug(f"Computed destination: {dest_path}")

        # Validate .par
        if not os.path.exists(par_file) or ext != ".par":
            logger.warning(f"Invalid .par file: {par_file}")
            self.outputs.saved_files_path = []
            return

        source = par_file
        # Detect provided optional params (using get_input_value to avoid MissingData)
        provided = [
            k for k in PARAM_MAPPING if self.get_input_value(k, None) is not None
        ]
        if provided:
            logger.info(f"Applying optional parameters: {provided}")
            with open(par_file, encoding="latin-1") as f:
                lines = f.readlines()
            new_lines = []
            for line in lines:
                applied = False
                for key in provided:
                    info = PARAM_MAPPING[key]
                    val = self.get_input_value(key)
                    if info["pattern"].search(line):
                        new_lines.append(info["formatter"](val) + "\n")
                        applied = True
                        break
                if not applied:
                    new_lines.append(line)

            os.makedirs(dest_dir, exist_ok=True)
            temp = os.path.join(dest_dir, "temp.par")
            with open(temp, "w", encoding="latin-1") as f:
                f.writelines(new_lines)
            source = temp

        # Forward kwargs
        forward = {k: self.get_input_value(k) for k in provided}

        os.makedirs(dest_dir, exist_ok=True)
        try:
            create_par_file(source, dest_dir, dest_basename, **forward)
        except TypeError as err:
            if "unexpected keyword argument" in str(err):
                create_par_file(source, dest_dir, dest_basename)
            else:
                raise

        saved_files.append(dest_path)
        self.outputs.saved_files_path = saved_files
        logger.info(
            "CreateParFiles task completed. Saved files: " + ", ".join(saved_files)
        )
