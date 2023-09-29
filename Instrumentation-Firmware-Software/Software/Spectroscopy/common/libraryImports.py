###Library importing###
import sys

# Added copy for deepcopy dictionary copying to prevent recursive referencing
import copy

# Just in time compiler (put @jit(forceobj=True) before each compiled function)
# from numba import jit, njit, vectorize, float64, float32
#import numba as nb

# Used to speed up functions using caches (@cache(maxsize=None)) prior to function
# Only useful if similar calculations are performed?
# from functools import lru_cache as cache


# Main Qt imports for creating GUI
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# Math libraries
import numpy as np
import math

# Plotting library
import matplotlib as mpl

# matplotlib.use("Agg")
# matplotlib.use("Qt5Agg")
from matplotlib import pyplot as plt
from matplotlib import animation
from matplotlib import cm as cm

from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap

# Library option for alternative fitting
# import scipy
# from scipy import *
# from scipy.optimize import leastsq

# Specific libraries for spectral fitting
from numpy import exp, pi, sqrt

# from scipy.special import erf, erfc  # , wofz

# from scipy.special.cython_special import wofz

import scipy.special as sc
#import numba_special


# cimport scipy.special.cython_special

# import mpmath as mpm

# import scipy.special as sc

# import scipy.integrate as integrate
from scipy.optimize import minimize as scimin
from lmfit import fit_report, Parameters, minimize

# Filtering library option
# from scipy.signal import savgol_filter

# Spectral filtering library
from scipy.signal import butter, filtfilt  # , savgol_filter
from scipy import signal

# For measuring execution time of code
from time import time
import time

# Specific fitting models
# from lmfit import Model, CompositeModel
# from lmfit.models import ConstantModel, ExpressionModel, LinearModel, VoigtModel
# from lmfit.models import PolynomialModel, QuadraticModel, ExponentialModel

# Used to create embedded canvas in Qt environment
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# For parsing julian date into something usable
from jdcal import *

# File I/O libraries
import csv
import pickle
import os
import pandas as pd


# MAY Require manual install of numpy+mkl
from netCDF4 import Dataset

# from hapi import *

import winsound
import seaborn as sns

from brokenaxes import brokenaxes

import ctypes

# matplotlib.use('module://pyemf')

# IMport pretty print for dictionaries and lists
import pprint

# use pprint.format(...) to just return the string for the logging function


import logging

# Used for printing to screen
# logging.basicConfig(
#    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
# )
# logging.debug("This is a log message.")

# Can set logging level to debug, info, warning, error, critical

# To write log messages to a file
logging.basicConfig(
    filename="../generalLog.txt",
    filemode="w",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Not working, should check into rotating file handlers.
# logging.handlers.RotatingFileHandler(
#    filename="../generalLog.txt",
#    mode="a",
#    maxBytes=5 * 1024 * 1024,
#    backupCount=2,
#    encoding=None,
#    delay=0,
# )

# Set up a specific logger with our desired output level
# my_logger = logging.getLogger("MyLogger")
# my_logger.setLevel(logging.DEBUG)
# Add the log message handler to the logger
# handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=20, backupCount=5)
# my_logger.addHandler(handler)


# logging.debug("This is a log message.")
# From here just run a "watch -n1 "cat file | tail -50" to print to screen separately

# For printing to screen AND file
# logger = logging.getLogger()
# ogger.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# fh = logging.FileHandler('log_filename.txt')
# fh.setLevel(logging.DEBUG)
# fh.setFormatter(formatter)
# logger.addHandler(fh)

# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
# ch.setFormatter(formatter)
# logger.addHandler(ch)
