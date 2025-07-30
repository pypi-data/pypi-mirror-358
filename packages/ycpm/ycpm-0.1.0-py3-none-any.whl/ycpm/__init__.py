import importlib
import importlib.util
import os
import sys
import pathlib

__global__ = ["clyp_packages_folder", "ycpm_version", "clyp_version"]

def find_clyp_package():
    # Try to find the package using importlib
    spec = importlib.util.find_spec("clyp")
    clyp_folder = None
    if spec and spec.submodule_search_locations:
        clyp_folder = os.path.abspath(spec.submodule_search_locations[0])
    else:
        # Fallback: search for 'clyp' directory in sys.path
        for path in sys.path:
            candidate = os.path.join(path, "clyp")
            if os.path.isdir(candidate):
                clyp_folder = os.path.abspath(candidate)
                break

    wheel_dir = None
    clyp_packages = None
    # Only try to import and use __file__ if spec and spec.origin are valid
    if spec is not None and spec.origin is not None:
        try:
            clyp = importlib.import_module("clyp")
            if hasattr(clyp, "__file__") and clyp.__file__:
                wheel_dir = pathlib.Path(clyp.__file__).parent.parent
                clyp_packages = (wheel_dir / "clypPackages").resolve()
        except Exception:
            clyp_packages = None

    return {
        "clyp_folder": clyp_folder,
        "clyp_packages": str(clyp_packages) if clyp_packages else None
    }

# Try to import clyp_version, but handle if not available
try:
    from clyp import __version__ as clyp_version
except ImportError:
    clyp_version = None

clyp_packages_folder = find_clyp_package()["clyp_packages"]

# Define ycpm_version
# Update this version as needed

try:
    from .version import __version__ as ycpm_version
except ImportError:
    ycpm_version = "0.1.0"
