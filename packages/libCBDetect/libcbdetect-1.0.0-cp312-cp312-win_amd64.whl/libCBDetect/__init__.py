"""
libCBDetect – Python bindings for the cbdetect C++ checkerboard detector.
"""


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'libcbdetect.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

from .Checkerboard import Checkerboard  # noqa: F401


import os, sys
from pathlib import Path

# shipped DLLs are put in …/libCBDetect.libs by delvewheel
_this_dir = Path(__file__).with_suffix('').parent
libs = _this_dir.parent / (f"{_this_dir.name}.libs")
if libs.exists() and hasattr(os, "add_dll_directory"):
    os.add_dll_directory(libs)