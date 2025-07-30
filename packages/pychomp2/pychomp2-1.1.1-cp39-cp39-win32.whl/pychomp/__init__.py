### __init__.py
### MIT LICENSE 2016 Shaun Harker
#
# Marcio Gameiro
# 2022-12-04


# start delvewheel patch
def _delvewheel_patch_1_10_1():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'pychomp2.libs'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-pychomp2-1.1.1')
        if os.path.isfile(load_order_filepath):
            import ctypes.wintypes
            with open(os.path.join(libs_dir, '.load-order-pychomp2-1.1.1')) as file:
                load_order = file.read().split()
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.wintypes.HMODULE
            kernel32.LoadLibraryExW.argtypes = ctypes.wintypes.LPCWSTR, ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(lib_path, None, 8):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

from pychomp._chomp import *
#from pychomp.Braids import *
from pychomp.CondensationGraph import *
from pychomp.FlowGradedComplex import *
from pychomp.TopologicalSort import *
from pychomp.DirectedAcyclicGraph import *
from pychomp.InducedSubgraph import *
from pychomp.TransitiveReduction import *
from pychomp.TransitiveClosure import *
from pychomp.Poset import *
from pychomp.StronglyConnectedComponents import *
from pychomp.DrawGradedComplex import *
from pychomp.CubicalHomology import *
from pychomp.DirectedGraph import *
