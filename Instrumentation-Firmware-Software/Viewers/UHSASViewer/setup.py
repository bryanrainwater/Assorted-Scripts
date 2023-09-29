#### GENERAL SETUP #####
# -*- coding: utf-8 -*-
#from setuptools import setup, find_packages

import sys
from cx_Freeze import setup, Executable

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

# CX_FREEZE OPTIONS
packages_list = []
includefiles_list = []
packages_list.append('numpy')

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')
# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

build_exe_options = {"packages": packages_list,
	"include_files": includefiles_list,#[
	"excludes":["scipy.spatial.cKDTree"],
	"optimize": 2}

setup(
    name='UHSASprocessing',
    version='0.1',
    description='UHSAS Quick-Look and file processing codes',
    long_description=readme,
    author='Bryan Rainwater',
    author_email='bryan.rainwater@colorado.edu',
    url='https://github.com/bryanrainwater/UHSASprocessing',
    license=license,
    #packages=find_packages(exclude=('tests', 'docs'),
    options = {"build_exe": build_exe_options},
    executables = [Executable("uhsasView.py", base=base, targetName = 'UHSASprocessing')]
)
