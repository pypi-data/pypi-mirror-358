import os
import glob

DRIVER_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "drivers"))

def get_driver(system, driver_type="jdbc", version=None):
    driver_dir = os.path.join(DRIVER_BASE, driver_type)
    if driver_type == "jdbc":
        pattern = f"{system}-{driver_type}-{version}*.jar" if version else f"{system}-{driver_type}-*.jar"
    elif driver_type == "odbc":
        pattern = f"{system}-{driver_type}-{version}*.so" if version else f"{system}-{driver_type}-*.so"
    else:
        raise ValueError("driver_type must be 'jdbc' or 'odbc'")

    candidates = sorted(glob.glob(os.path.join(driver_dir, pattern)), reverse=True)
    if not candidates:
        raise FileNotFoundError(f"No driver found for {system} ({driver_type}, version={version})")
    return candidates[0]