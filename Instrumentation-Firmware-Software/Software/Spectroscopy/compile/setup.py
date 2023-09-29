#Available run commands:
#'python setup.py build' for creating a standalone directory
#'python setup.py bdist_msi' for creating an installer ('bdist_dmg' for mac)

from cx_Freeze import setup, Executable
import sys
import os
#import scipy

#os.environ["TCL_LIBRARY"] = r'C:/Users/rainw/AppData/Local/Programs/Python/Python36/tcl/tcl8.6'
#os.environ["TK_LIBRARY"] = r'C:/Users/rainw/AppData/Local/Programs/Python/Python36/tcl/tk8.6'


includefiles_list = []
#includefiles_list.append(os.path.dirname(scipy.__file__))#scipy_path)
#includefiles_list.append(r"C:/Users/rainw/AppData/Local/Programs/Python/Python36/DLLs/tcl86t.dll")
#includefiles_list.append(r"C:/Users/rainw/AppData/Local/Programs/Python/Python36/DLLs/tk86t.dll")

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

#test_includes.append(os.path.dirname(scipy.__file__))#scipy_path)
#includefiles_list.append(os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'))
#includefiles_list.append(os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'))

packages_list = []
#packages_list.append('tkinter')
#packages_list.append('_tkinter')
#packages_list.append('numpy')
#packages_list.append('matplotlib.backends.backend_tkagg')
#packages_list.append('os')
#packages_list.append('PyQt5')
#packages_list.append('time')
#packages_list.append('math')
#packages_list.append('matplotlib.pyplot')
#packages_list.append('jdcal')
#packages_list.append('_tkinter')
#packages_list.append('multiprocessing.process')
#packages_list.append('numpy.matlib')
#packages_list.append('matplotlib')
#packages_list.append('scipy')
#packages_list.append('lmfit')
#packages_list.append('csv')
#packages_list.append('netCDF4')
#packages_list.append(
#packages_list.append(
#packages_list.append('scipy.sparse.csgraph._validation')
#packages_list.append('scipy.spatial.cKDTree')
#packages_list.append('netCDF4')

excludes = []
includes = []

includes.append('scipy.sparse.csgraph._validation')
includes.append('numpy.core._methods')
includes.append('numpy.lib.format')
includes.append('netCDF4.utils')
#includes.append('netcdftime')
includes.append('cftime')
#includes.append('scipy._distributor_init')
#includes.append('scipy.ndimage._ni_support')
#includes.append('scipy.ndimage._ni_docstrings')
#includes.append('scipy.ndimage')
#includes.append('scipy')

excludes.append('scipy.spatial.cKDTree')

#build_exe_options = {"excludes": packages_list,
#	"include_files": test_includes,
#	"optimize": 2}#includefiles_list}#[
	#,"excludes":["tkinter"]}

build_exe_options = {"packages": packages_list,
	"include_files": includefiles_list,#[
	"includes":includes,
	"excludes":excludes,
	"optimize": 2}

#base = None
#base = "Win32GUI" #Changed here to suppress terminal window from opening
#
base = 'Win32GUI' if sys.platform == 'win32' else None
#if sys.platform == "win64":
#	base = "Win64GUI"

setup( name = "CLH2Processing",
	version = "0.5",
	description = "CLH2Processing",
	options = {"build_exe": build_exe_options},
	executables = [Executable("clh2process.py", base = base)])#, targetName = 'sample-app')])
