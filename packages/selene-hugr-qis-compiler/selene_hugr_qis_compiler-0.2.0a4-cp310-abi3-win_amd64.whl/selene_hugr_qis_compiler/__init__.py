"""""" # start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'selene_hugr_qis_compiler.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

from .selene_hugr_qis_compiler import *

__doc__ = selene_hugr_qis_compiler.__doc__
if hasattr(selene_hugr_qis_compiler, "__all__"):
    __all__ = selene_hugr_qis_compiler.__all__
