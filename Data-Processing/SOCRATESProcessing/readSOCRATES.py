import pickle
import matplotlib

# matplotlib.use('module://pyemf')
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
import jdcal
import seaborn as sns

from netCDF4 import Dataset

import time
import datetime


#%matplotlib qt
import matplotlib as mpl

# from matplotlib import rc
# rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
# rc('font',**{'family':'serif','serif':['Palatino']})
# rc('text', usetex=True)

import importlib
import pandas

import scipy.stats as scps



############### LOAD IN PICKLE DATA CONTAINING EVERYTHING #####################


basePath = "C:/Users/rainw/github/Data/SOCRATES/FinalNC/CLH-2 CWC/"
with open(basePath + "Master_SOCRATES.pickle", "rb") as file:
    data = pickle.load(file)

Aug17File = basePath + "Aug17Chamber.xlsx"
df = pandas.read_excel(Aug17File)
# print(df.dtypes.index)
data[df.dtypes.index[0]] = list(df.values[:, 0])
data[df.dtypes.index[1]] = list(df.values[:, 1])

for i, val in enumerate(data["Date"]):
    date = val.split("/")
    data["Date"][i] = jdcal.gcal2jd(date[2], date[0], date[1])

for key in data.keys():
    data[key] = np.array(data[key], dtype="float")
data["domain"] = np.array(np.arange(0, len(data["Time"])), dtype="float")

lowSpdFilter = np.where(data["TASX"] < 120.0)[0]  # Might filter at 120?


################## Loading in the new cloud ID data....################################
cloudID = Dataset("C:/Users/rainw/github/Data/SOCRATES/NCFiles/SOCRATES_phase_data.nc")
# available variables: temp, pres, utc, flight_number, phase, day, month
cloudIDTime = cloudID["utc"][0]
cloudIDFlight = cloudID["flight_number"][0]
cloudIDPhase = np.array(cloudID["phase"][0])

################## LIST OF NC VARIABLES FOR REFERENCE #################################

# ['Time', 'FlightNum', 'Date', 'GGLAT', 'GGLON', 'ATTACK', 'ATX', 'PALT', 'PSXC', 'QCXC', 'TASX', 'THETA', 'THETAE', 'RICE', 'DBAR1DC_RWOI', 'DBARD_RWIO', 'DBARPIP_RWII', 'DBARU_CVIU', 'DBARU_LWII', 'DPXC', 'DP_DPL', 'DP_DPR', 'DP_VXL', 'VMR_VXL', 'PLWC1DC_RWOI', 'PLWCC', 'PLWCD_RWIO', 'CONCD_RWIO', 'PLWCPIP_RWII', 'TCNTD_RWIO', 'TCNTU_LWII', 'UFLAG_CVIU', 'CVCFACTC', 'CVCFACTTDL', 'CVCWCC', 'CVIFLAG', 'CVCFACT', 'CVF1', 'CVFX0', 'CVFX2', 'CVFX3', 'CVFX4', 'CVFX5', 'CVFXFLOWS', 'CVINLET', 'CVPCN', 'CVRAD', 'CVTAI', 'CVTCN', 'CVTP', 'CVTS', 'CVTT', 'CLHCWC', ' temp1', ' tbody', ' temp2', ' press', ' MFC', ' staticppmv', 'Flow factor', 'corMFC', 'rsq_CVIU_UHSAS', 'amp_CVIU_UHSAS', 'mu_CVIU_UHSAS', 'sig_CVIU_UHSAS', 'fitPeak_CVIU_UHSAS', 'obsPeak_CVIU_UHSAS', 'obsMu_CVIU_UHSAS', 'PM1_CVIU_UHSAS', 'tCounts_CVIU_UHSAS', 'rsq_NCAR_UHSAS', 'amp_NCAR_UHSAS', 'mu_NCAR_UHSAS', 'sig_NCAR_UHSAS', 'fitPeak_NCAR_UHSAS', 'obsPeak_NCAR_UHSAS', 'obsMu_NCAR_UHSAS', 'PM1_NCAR_UHSAS', 'tCounts_NCAR_UHSAS', 'domain'])

xlKeys = [
    " temp1",
    " tbody",
    " temp2",
    " press",
    " MFC",
    " staticppmv",
    "Flow factor",
    "corMFC",
]
cviKeys = [
    "CVCFACTC",
    "CVCFACTTDL",
    "CVCWCC",
    "CVIFLAG",
    "CVCFACT",
    "CVF1",
    "CVFX0",
    "CVFX2",
    "CVFX3",
    "CVFX4",
    "CVFX5",
    "CVFXFLOWS",
    "CVINLET",
    "CVPCN",
    "CVRAD",
    "CVTAI",
    "CVTCN",
    "CVTP",
    "CVTS",
    "CVTT",
]


################ RECONSTRUCT CLH-2 DATA BASED ON XLSX FILES ###################
newData = deepcopy(data)
# newData['FlightNum'] = np.array([np.round(x) for x in newData['FlightNum']])

redData = np.where(newData["FlightNum"] == 7)[0]
newData["Flow factor"][redData] = 1.8

newData["CLHCWC"] = newData["CLHCWC"] * 1.8 / newData["Flow factor"]
newData["CLHOld"] = newData["CLHCWC"]

####Re-derive ppmv from CLH-2...... Use original computed CWC's.....
newData["CVMR"] = (
    newData["CLHCWC"]
    / newData["Flow factor"]
    * 1000000.0
    * 0.0289
    / 18.01
    * ((273.15 + 40) * 0.602)
    / (7.25 * newData[" press"] * 0.0289)
)
newData["CVMR"] = (
    (newData["CVMR"])
    / (
        newData[" MFC"]
        * (1000.0 / 60.0)
        * (1013.25 / newData[" press"])
        * (313.15 / 298.15)
    )
    * (np.pi * 100.0 * newData["TASX"] * pow(0.2375, 2))
)
newData["CLHVMR"] = newData["CVMR"] + newData["VMR_VXL"]  # + newData['CVMR']

# p00 = 6.1907733E+02
# p01	= 9.9239550E-01
# p10	= -1.8751667E+00
# p02	= 1.6396405E-07
# p20	= 9.7924813E-04

p10 = -1.875166730441427
p01 = 0.992395497542329
p20 = 9.792481308430908e-04
p11 = -6.363554375547824e-05
p02 = 0.0
highWater = np.where(newData[" staticppmv"] > 6000)[0]

# a = -0.786468748
# b = 1.089409599
# c = -5.26702E-05
# newData['CLHVMRRev'] = newData[' press']*a + newData['CLHVMR']*b + newData['CLHVMR']*newData[' press']*c

# plt.scatter(newData['CLHVMRRev'],newData[' staticppmv'])
# plt.plot(newData['VMR_VXL'])
# plt.plot(newData[' staticppmv'])
# plt.plot(newData['CLHVMRRev'])

newData["CLHppmv"] = newData[" staticppmv"]

# newData['CLHVMR'][highWater] = p11*newData['CLHVMR'][highWater]*newData[' press'][highWater] + p01*newData['CLHVMR'][highWater] + p10*newData[' press'][highWater] + p02*newData['CLHVMR'][highWater]**2 + p20*newData[' press'][highWater]**2



############# ALIGN DATA ACCORDING TO VARIOUS LAGS ##########################


# Positive value indicates CLH-2 data appears earlier than normal
CLH2LagArray = [0, -1, 0, 0, -1, -1, 429, -1, -1, -1, -1, 633, 711, -1, 679]
#Changed RF07 lag from 427 to 429
#CLH-2 and CVI appear to be 1 second ahead on RF07
for i, lag in enumerate(CLH2LagArray):
    flightRange = np.where(newData["FlightNum"] == i + 1)[0]
    newData["CLHCWC"][flightRange] = np.roll(newData["CLHCWC"][flightRange], lag)
    if lag < 0:
        newData["CLHCWC"][
            np.max(flightRange) + lag + 1 : np.max(flightRange) + 1
        ] = np.nan
    elif lag > 0:
        newData["CLHCWC"][np.min(flightRange) : np.min(flightRange) + lag + 1] = np.nan

# CLH2 from xlsx files is 1 second ahead of vxl soooo...
for i in range(15):
    lag = 1
    flightRange = np.where(newData["FlightNum"] == i + 1)[0]
    for key in xlKeys:
        newData[key][flightRange] = np.roll(newData[key][flightRange], lag)
        if lag < 0:
            newData[key][np.max(flightRange) + lag + 1 : np.max(flightRange) + 1] = np.nan
        elif lag > 0:
            newData[key][np.min(flightRange) : np.min(flightRange) + lag + 1] = np.nan

CVILags = [0] * 15
for i, lag in enumerate(CVILags):
    flightRange = np.where(newData["FlightNum"] == i + 1)[0]
    for key in cviKeys:
        newData[key][flightRange] = np.roll(newData[key][flightRange], lag)
        if lag < 0:
            newData[key][np.max(flightRange) + lag + 1 : np.max(flightRange) + 1] = np.nan
        elif lag > 0:
            newData[key][np.min(flightRange) : np.min(flightRange) + lag + 1] = np.nan


# Create new variables for cloudIDs
newData["cloudIDPhase"] = np.array([np.nan] * len(newData["Time"][:]))
data["cloudIDPhase"] = np.array([np.nan] * len(newData["Time"][:]))

# newData["cloudIDPhase"][:] = np.nan
# cloud ID Lags
# Assert cloudID data to be of the same size as master dictionary
cloudIDLags = [0] * 15
for i, lag in enumerate(cloudIDLags):
    flightRange = np.where(newData["FlightNum"] == i + 1)[0]
    cloudIDRange = np.where(cloudIDFlight == i + 1)[0]
    # print(newData["Time"][flightRange], cloudIDTime[cloudIDRange])
    # exit()
    # newData["CLHCWC"][flightRange] = np.roll(newData["CLHCWC"][flightRange], lag)
    # timeDif = newData["Time"][flightRange][0] < cloudIDTime[cloudIDRange][0]
    # Align the start times of each of the arrays for matching
    # print(cloudIDRange, flightRange)
    while newData["Time"][flightRange][0] < cloudIDTime[cloudIDRange][0]:
        flightRange = flightRange[1:]
    while cloudIDTime[cloudIDRange][0] < newData["Time"][flightRange][0]:
        cloudIDRange = cloudIDRange[1:]
    # print(cloudIDRange, flightRange)
    # Once aligned, check to see if one is longer than the other.
    lenDif = len(flightRange) - len(cloudIDRange)
    # If destination array is bigger, reduce destination arrays
    if lenDif > 0:
        flightRange = flightRange[0:-lenDif]
    # If destination array is smaller, reduce input arrays
    if lenDif < 0:
        cloudIDRange = cloudIDRange[0:lenDif]

    # Finally copy arrays over
    # print(newData["cloudIDPhase"][flightRange], cloudIDPhase[cloudIDRange])
    newData["cloudIDPhase"][flightRange] = cloudIDPhase[cloudIDRange]
    data["cloudIDPhase"][flightRange] = cloudIDPhase[cloudIDRange]

    # data["cloudIDPhase"][data["cloudIDPhase"] == 0] = np.nan
    # newData["cloudIDPhase"][newData["cloudIDPhase"] == 0] = np.nan

    # If there are more data than slots, need to reduce

    # if timeDif < 0:
    #    for timeIndex in flightRange:
    #        try: newData["cloudIDPhase"][timeIndex] = cloudIDPhase[cloudIDRange]
    #        except: continue
    """
    for timeIndex in flightRange:
        # print(timeIndex)
        if newData["Time"][timeIndex] in cloudIDTime[cloudIDRange]:
            newData["cloudIDPhase"][timeIndex] = cloudIDPhase[
                np.where(cloudIDTime[cloudIDRange] == newData["Time"][timeIndex])[0]
            ]
    """
# plt.figure()
# plt.scatter(newData["cloudIDPhase"], newData["CLHCWC"])
# plt.show()
# exit()
# if lag < 0:
#    newData["CLHCWC"][
#        np.max(flightRange) + lag + 1 : np.max(flightRange) + 1
#    ] = np.nan
# elif lag > 0:
#    newData["CLHCWC"][np.min(flightRange) : np.min(flightRange) + lag + 1] = np.nan

# PIP is 1 second ahead of everything else:
# RF9 PIP is 3 seconds behind everything
for i in range(0, 15):
    lag = 2  # -1
    flightRange = np.where(newData["FlightNum"] == i + 1)[0]
    for key in newData.keys():
        if "PIP" not in key:
            continue
        newData[key][flightRange] = np.roll(newData[key][flightRange], lag)
        if lag < 0:
            newData[key][np.max(flightRange) + lag + 1 : np.max(flightRange) + 1] = np.nan
        elif lag > 0:
            newData[key][np.min(flightRange) : np.min(flightRange) + lag + 1] = np.nan

for key in data.keys():
    if (
        "Time" not in key
        and "domain" not in key
        and "FlightNum" not in key
        and "Date" not in key
    ):
        nanFilter = np.where(np.isnan(newData[key]))[0]
        newData[key][nanFilter] = np.nan  # -9999.0
        badFilter = np.where(newData[key] == -9999.0)[0]
        newData[key][badFilter] = np.nan

for key in newData.keys():
    # print(key)
    if (
        key != "Date"
        and key != "CONCD_RWIO"
        and key != "FlightNum"
        and "cloudID" not in key
        # and key != "cloudIDPhase"
        # and key != "PLWCC"
        # and key != "PLWCD_RWIO"
    ):
        avgTime = 3  # 30
        newData[key] = np.convolve(
            newData[key], np.ones((avgTime,)) / avgTime, mode="same"
        )
    # if key == 'RICE':
    #    for i in range(100):
    #        newData[key] = np.convolve(newData[key],np.ones((3,))/3, mode = 'same')
    newData[key] = np.ma.masked_invalid(newData[key])  # .filled(fill_value=-9999)


# plt.plot(newData['TASX'])

keys = ["CLHCWC", "CVCWCC", "VMR_VXL", "PLWCC", "PLWCD_RWIO", "RICE"]
for key in keys:
    tmp = newData[key][np.where(newData["TASX"] > 110)[0]]
    # print('Max Data: ',len(tmp))
    # print(key,' Valid: ',100 - len(tmp[np.where(np.isnan(tmp))[0]])/len(tmp)*100)
# print(len(tmp))

for key in newData.keys():
    newData[key] = np.array(newData[key])

"""
for i in range(15):
    plt.figure()
    redData = np.where(data["FlightNum"] == i + 1)[0]
    plt.scatter(data[" temp1"][redData], data[" temp2"][redData])
    plt.title(str(i + 1))
    plt.xlim(25, 50)
    plt.ylim(38, 48)
"""
# FLIGHT 6,7,10 had strange cell temperature behavior

# Various clusters
good = [2, 5, 8, 7, 9, 10, 14]
bad = [12, 13]
ugly = [3, 4, 6, 11]
worst = [1, 15]

redData = np.where(np.in1d(newData["FlightNum"], good))[0]  # Relatively good data
redData = np.where(np.in1d(newData["FlightNum"], bad))[0]  # Divergent high values
redData = np.where(np.in1d(newData["FlightNum"], ugly))[
    0
]  # Strongly variable (i.e. CVI high)
redData = np.where(np.in1d(newData["FlightNum"], worst))[0]  # Missing or chaotic

from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap

# Add alpha channel alongside existing colormap
cmap = plt.cm.Blues  # RdBu
my_blues = cmap(np.arange(cmap.N))
my_blues[:, -1] = np.linspace(0, 1, cmap.N)
my_blues = ListedColormap(my_blues)

cmap = plt.cm.Reds
my_reds = cmap(np.arange(cmap.N))
my_reds[:, -1] = np.linspace(0, 0.5, cmap.N)
my_reds = ListedColormap(my_reds)

cmap = plt.cm.Greens
my_greens = cmap(np.arange(cmap.N))
my_greens[:, -1] = np.linspace(0, 0.25, cmap.N)
my_greens = ListedColormap(my_greens)

cmap = plt.cm.Purples
my_purps = cmap(np.arange(cmap.N))
my_purps[:, -1] = np.linspace(0, 1, cmap.N)
my_purps = ListedColormap(my_purps)

cmap = plt.cm.Greys
my_grays = cmap(np.arange(cmap.N))
my_grays[:, -1] = np.linspace(0, 1, cmap.N)
my_grays = ListedColormap(my_grays)


# newData["CLHTotal"] = newData["CLHOld"]


redData = np.where(
    (newData["FlightNum"] == 14)
    # * (newData["PLWCC"] > newData["PLWCD_RWIO"] + 0.01)
    # * (newData["PLWCPIP_RWII"] > 1)
    # * (newData["PLWCC"] < newData["PLWCD_RWIO"] )
)[0]

#  (PLWCD * 0.072)*TASX

# plt.figure()
# plt.scatter(newData["PLWCD_RWIO"], newData["CLHCWC"], c=newData["cloudIDPhase"], s=1)
# plt.show()
# exit()

# plt.plot(
#    newData["Time"][redData],  # - 86400,
#    (newData["PLWCC"][redData] - newData["PLWCD_RWIO"][redData]),
# )
"""
plt.scatter(
    newData["FlightNum"][redData],
    newData["Time"][redData],  # - 86400,
    c=np.log(newData["PLWCC"][redData] - newData["PLWCD_RWIO"][redData]),
)
plt.scatter(
    newData["PLWCC"][redData],
    (newData["PLWCD_RWIO"][redData] * 0.072) * newData["TASX"][redData],
    c=np.log10(
        newData["PLWCPIP_RWII"][redData]
    ),  # (newData["PLWCC"][redData] - newData["PLWCD_RWIO"][redData]),
    s=1,
)

plt.scatter(
    newData["CLHOld"][redData],
    newData["PLWCD_RWIO"][redData],
    c=(
        (newData["PLWCD_RWIO"][redData] * 0.072) * newData["TASX"][redData]
    ),  # (newData["PLWCC"][redData] - newData["PLWCD_RWIO"][redData]),
    s=1,
)
"""
# plt.plot(newData["ATX"][redData])
# plt.scatter(
#    newData["PLWCC"][redData],
#    newData["PLWCD_RWIO"][redData],
#    c=newData["ATX"][redData],
#    s=3,
#    lw=0,
# )


# lt.plot(dates, df.Price)
# plt.colorbar()
# plt.show()
# exit()

# STEPS FOR POSTER
# *. Show Correlation of VMR's
# *. Demonstrate poor correlation between all data.
# *. Demonstrate purely precipitation environment. Filter data accordingly. PLWCPIP_RWII < 1 (when CONCD_RWIO == 0)
# *. Create correction of Water contents based on CONCD_RWIO
# *. Separate Pure water, pure ice, mixed phase environment.

# Excel file 7 is corrupted...
# Showing correlation of VMR's
"""
plt.figure(figsize=(12, 9))
plt.loglog(
    newData["VMR_VXL"],
    newData["CLHVMR"],
    linestyle="",
    marker=".",
    markersize=1,
    alpha=0.2,
)
plt.loglog(
    data["CLHCal"], data["CVICal"], linestyle="", marker=".", markersize=1, alpha=1
)
plt.loglog([0, 100000], [0, 100000])
plt.xlabel("CLH-2 (ppmv)", fontsize=24, fontweight="bold")  # ,fs,30)
plt.ylabel("Volume Mixing Ratio (ppmv)", fontsize=24, fontweight="bold")
plt.tick_params(axis="x", labelsize=20)
plt.tick_params(axis="y", labelsize=20)
plt.ylim(50, 80000)
plt.xlim(50, 80000)
plt.gca().legend(
    ["CLH-2 vs VCSEL", "CLH-2 vs CVI"],
    fontsize=24,
    markerscale=20,
    scatterpoints=1,
    loc="lower right",
)
plt.title("Mixing ratio Intercomparisons", fontsize=28, fontweight="bold")
plt.tight_layout()  #
plt.savefig(
    basePath + "PNG/Poster/CalIntercomparison.png",
    dpi=600,
    bbox_inches="tight",
    transparent=True,
)
plt.savefig(
    basePath + "PNG/Poster/CalIntercomparison.eps",
    dpi=600,
    bbox_inches="tight",
    transparent=True,
)
"""

"""
# SHOW ALL DATA
high = 0.8
max = 20
redData = np.where(newData["FlightNum"] > 0)[0]
plt.figure(figsize=(12, 9))
plt.hexbin(
    newData["CLHOld"][redData],
    newData["CVCWCC"][redData],
    vmax=max,
    cmap=my_blues,
    extent=(0, high, 0, high),
)  # plt.cm.jet)
plt.hexbin(
    newData["CLHOld"][redData],
    newData["PLWCC"][redData],
    vmax=max,
    cmap=my_reds,
    extent=(0, high, 0, high),
)
plt.hexbin(
    newData["CLHOld"][redData],
    newData["PLWCD_RWIO"][redData],
    vmax=max,
    cmap=my_greens,
    extent=(0, high, 0, high),
)
plt.hexbin(
    newData["CLHOld"][redData],
    newData["PLWCPIP_RWII"][redData] * 0.01,
    vmax=max,
    cmap=my_purps,
    extent=(0, high, 0, high),
)

# plt.hexbin(newData['CLHOld'][redData],newData['RICE'][redData],vmax=max,cmap = my_grays,extent=(0,high,0,high))
plt.plot([0, high], [0, high], color="black", lw=5)
plt.xlabel("CLH-2 (g/m^3)", fontsize=24, fontweight="bold")  # ,fs,30)
plt.ylabel("Water Contents (g/m^3)", fontsize=24, fontweight="bold")
plt.tick_params(axis="x", labelsize=20)
plt.tick_params(axis="y", labelsize=20)
legend_elements = [
    Line2D([0], [0], marker="o", label="CVI TDL (g/m^3)", markerfacecolor="b"),
    Line2D([0], [0], marker="o", label="King (g/m^3)", markerfacecolor="r"),
    Line2D([0], [0], marker="o", label="CDP (g/m^3)", markerfacecolor="g"),
    Line2D([0], [0], marker="o", label="PIP (g/m^3)", markerfacecolor="purple"),
]
plt.gca().legend(handles=legend_elements, loc="lower right", fontsize=24, markerscale=3)
plt.title("Mixing ratio Intercomparisons", fontsize=28, fontweight="bold")
plt.tight_layout()  #
# plt.savefig(
#    basePath + "PNG/Poster/AllData.png", dpi=600, bbox_inches="tight", transparent=True
# )
# plt.savefig(
#    basePath + "PNG/Poster/AllData.eps", dpi=600, bbox_inches="tight", transparent=True
# )
plt.show()
exit()
"""

# Calculation of cumulative water contents for CLH-2, CVI, CDP, King
# Create zero array of the same size as all data combined
# Increment values across cloud encounters (i.e. first cloud will be 1's for duration of cloud)
#   0's when the cloud ends, 2's for the second cloud.....
newData["CloudIndex"] = newData["CLHCWC"] * 0.0

# Create time array that searches for a large jump of "No cloud" to iterated
newData["CloudTime"] = newData["Time"] + newData["FlightNum"] * 2e5




################## FOR PLOTTING ALL DATA TO FIND CLOUD INDICES ###################
#plt.plot(newData['CLHCWC'])
#plt.plot(newData['PLWCC'])
#plt.show()
#exit()











# Read in cloud encouter index from .xlsx file
cloudIndexFile = "C:/Users/rainw/github/Data/SOCRATES/NCFiles/cloudEncounterIndices.xlsx"
#cloudIndexFile = "C:/Users/rainw/github/Data/SOCRATES/NCFiles/cloudEncounterExpanded.xlsx"
cloudReanalysisFile = (
    "C:/Users/rainw/github/Data/SOCRATES/NCFiles/CloudReanalysisFile.xlsx"
)
df = pandas.read_excel(cloudIndexFile)

################# EXPAND CLOUD ENCOUNTER INDEX FILE TO INCLUDE JULIAN TIMES ######################
'''
#df['jul_start'] = df['start'][:]
df['sec_start'] = newData['Time'][df['Start']]
df['sec_end'] = newData['Time'][df['End']]
df['time_start'] = (df['sec_start'][:])
df['time_end'] = (df['sec_end'][:])
for i, (start, end) in enumerate(zip(df['time_start'],df['time_end'])):
    df['time_start'][i] = time.strftime("%H:%M:%S", time.gmtime(start))
    df['time_end'][i] = time.strftime("%H:%M:%S", time.gmtime(end))
#df['time_start'] = time.strftime("%H:%M:%S", time.gmtime(df['sec_start']))
#df['time_end'] = time.strftime("%H:%M:%S", time.gmtime(newData['sec_start']))
#df['time_start'] = str(datetime.timedelta(seconds = df['sec_start']))
#pandas.
#print(df['jul_start'])#

# Create a Pandas Excel writer using XlsxWriter as the engine.
pdwriter = pandas.ExcelWriter('pandas_simple.xlsx')#, engine='Xlsxwriter')

# Convert the dataframe to an XlsxWriter Excel object.
df.to_excel(pdwriter, sheet_name='Sheet1')

# Close the Pandas Excel writer and output the Excel file.
pdwriter.save()
'''



cloudEncKeys = []
cloudEncDict = {}
for i in range(3):
    cloudEncKeys.append(df.dtypes.index[i])
    cloudEncDict[df.dtypes.index[i]] = list(df.values[:, i])

cloudEncKeys = [
    "CLHCWC",
    "CVCWCC",
    "PLWCD_RWIO",
    "PLWCC",
    "PLWCPIP_RWII",
    "RICE",
    "CONCD_RWIO",
    "TCNTD_RWIO",
    "DBARD_RWIO",
    "ATX",
    "cloudIDPhase",
]

cloudQualIndex = {}
cloudQualIndexKeys = [
    "flightNum",  # Flight number.
    "startTime(Jul)",  # starting in julian seconds from beginning of flight
    "endTime(Jul)",
    "startUTC(hhmmss)",  # starting UTC time for cloud encounter
    "endUTC(hhmmss)",
    "avgATX",  # Average air temperature outside of the aircraft
    "minATX",  # Min air temperature for the spanDiff
    "maxATX",  # max air temp for the span.
]

numInstruments = 11
numQualIndicators = 7
numQualOffset = 8
for key in cloudEncKeys:  # ["CLHCWC", "CVCWCC", "PLWCC", "PLWCPIP_RWII", "cloudIDPhase"]:
    for qualIndicator in ["Offset", "Scale", "Skew", "Kurt", "chisqr", "chisqrp", "std"]:
        cloudQualIndexKeys.append(key + "-" + qualIndicator)
    # cloudQualIndexKeys.append(key + "-Scale")
    # cloudQualIndexKeys.append(key + "-Skew")

# Initialize system to hold proper
for key in cloudQualIndexKeys:
    if "UTC" in key:
        cloudQualIndex[key] = np.zeros(len(cloudEncDict["Start"]), dtype="U6")
    else:
        cloudQualIndex[key] = np.zeros(len(cloudEncDict["Start"]), dtype="float")


# Correction for Precipitation based on one plot
# newData["CLHCWC"] -= newData["PLWCPIP_RWII"] * (1.0 / 450.0)
# newData["CVCWCC"] -= newData["PLWCPIP_RWII"] * (4.0 / 100.0)

# Attempted changes to match CDP
# newData["CLHOld"] -= newData["PLWCPIP_RWII"] * (0.5 / 100.0)
# newData["CVCWCC"] -= newData["PLWCPIP_RWII"] * (1.0 / 200.0)

# CDP Concentration correction to CLH2, CVICal

# newData["CLHCWC"] += (1.0 / 2000.0) * newData["CONCD_RWIO"]
# newData["CVCWCC"] += (1.0 / 2000.0) * newData["CONCD_RWIO"]

# print(cloudQualIndex[cloudQualIndexKeys[4]][5])
# exit()

cloudEncColor = ["black", "red", "green", "blue", "purple", "orange", "yellow", "brown"]

# cloudEncMeanKeys = ['CONCD_RWIO','DBARD_RWIO','ATX','']

# cloudEncDict["PLWCPIP_RWII"][start:end] /= 200  # Suppressing pip signal


for key in cloudEncKeys:
    cloudEncDict[key] = newData["CLHCWC"] * 0.0


for i, (start, end) in enumerate(zip(cloudEncDict["Start"], cloudEncDict["End"])):
    newData["CloudIndex"][start:end] = i + 1
    for key in cloudEncKeys:
        # ADDED THIS CONDITION TO BRING NEGATIVE CLH VALUES UP
        '''
        if "CLH" in key:
            if np.nanmin(newData[key][start:end]) < 0:
                # print(np.nanmin(newData[key][start:end]))
                newData[key][start:end] += np.abs(np.nanmin(newData[key][start:end]))
                # Corrections applied to CLH2 DATA for precip
                newData[key][start:end] -= (
                    newData["PLWCPIP_RWII"][start:end] * 1.0 / 200.0
                )
                # newData[key][start:end] += newData["CONCD_RWIO"][start:end] * (
                #    1.0 / 2000.0
                # )
        '''
        cloudEncDict[key][start:end] = np.nancumsum(newData[key][start:end])


accumulator = np.array([[0.00] * len(cloudEncDict["Start"])] * 6, dtype="float")
finalVals = (
    {}
)  # np.array([[0.00]*len(cloudEncDict['Start'])]*len(cloudEncKeys), dtype = 'float')
for key in cloudEncKeys:
    finalVals[key] = np.zeros(len(cloudEncDict["Start"]), dtype="float")
    for i, (flight, start, end) in enumerate(
        zip(cloudEncDict["Flight"], cloudEncDict["Start"], cloudEncDict["End"])
    ):
        finalVals[key][i] = cloudEncDict[key][end - 1]

cloudEncMeans = {}
for key in cloudEncKeys:
    cloudEncMeans[key] = np.zeros(len(cloudEncDict["Start"]), dtype="float")
    for i, (flight, start, end) in enumerate(
        zip(cloudEncDict["Flight"], cloudEncDict["Start"], cloudEncDict["End"])
    ):
        cloudEncMeans[key][i] = np.nanmean(newData[key][start:end])

len(newData["CloudIndex"][newData["CloudIndex"] != 0]) / 3600

"""
ax = plt.gca()
# ax.scatter(data['o_value'] ,data['time_diff_day'] , c='blue', alpha=0.05, edgecolors='none')

ax.scatter(finalVals["CLHOld"], finalVals["CVCWCC"])
ax.scatter(
    finalVals["CLHOld"],
    finalVals["PLWCD_RWIO"],
    c=np.log(cloudEncMeans["PLWCPIP_RWII"]),
    marker=".",
    cmap="magma",
    alpha=1,
)
# ax.set_yscale("log")
# ax.set_xscale("log")


plt.show()

exit()
"""
newData["PLWCPIP_RWII"] /= 200.0
cloudEncDict["PLWCPIP_RWII"] /= 200.0


for i, (flight, start, end) in enumerate(
    zip(cloudEncDict["Flight"], cloudEncDict["Start"], cloudEncDict["End"])
):
    accumulator[0, i] = (
        cloudEncDict["CLHCWC"][end - 1] / cloudEncDict["PLWCD_RWIO"][end - 1]
    )  # /cloudEncDict['CLHOld'][end-1]
    accumulator[1, i] = (
        cloudEncDict["CVCWCC"][end - 1] / cloudEncDict["PLWCD_RWIO"][end - 1]
    )
    accumulator[2, i] = (
        cloudEncDict["PLWCC"][end - 1] / cloudEncDict["PLWCD_RWIO"][end - 1]
    )
    accumulator[3, i] = cloudEncDict["CONCD_RWIO"][end - 1]
    accumulator[4, i] = cloudEncDict["PLWCPIP_RWII"][
        end - 1
    ]  # cloudEncDict['PLWCPIP_RWIO'][end-1]
    accumulator[5, i] = np.nanmean(np.diff(cloudEncDict["ATX"][start:end]))

# plt.scatter(accumulator[4, :], accumulator[3, :])

# plt.figure()
# redData = np.where((newData["PLWCPIP_RWII"] > 1) * (newData["CONCD_RWIO"] == 0))[0]

# plt.scatter(
#    newData["PLWCPIP_RWII"][redData],
#    newData["CVCWCC"][redData] - newData["PLWCD_RWIO"][redData],
# )

# plt.plot(accumulator[4, :])
for i in range(6):
    accumulator[i, accumulator[4, :] > 1] = np.nan

"""
plt.scatter(accumulator[2, :], accumulator[5, :])
plt.scatter(
    accumulator[0, :],
    accumulator[2, :],
    c=accumulator[1, :],
    marker=".",
    cmap="magma",
    alpha=1,
)
"""
# plt.figure()
for i, (flight, start, end) in enumerate(
    zip(cloudEncDict["Flight"], cloudEncDict["Start"], cloudEncDict["End"])
):

    # Routine to populate the cloudQualIndex array.
    # Always done before isolating any whatever in the field.]
    cloudQualIndex[cloudQualIndexKeys[0]][i] = int(flight)
    cloudQualIndex[cloudQualIndexKeys[1]][i] = newData["Time"][start]
    cloudQualIndex[cloudQualIndexKeys[2]][i] = newData["Time"][end]

    timeFrom = int(newData["Time"][start])
    if timeFrom >= 86400:
        offset = 86400
    else:
        offset = 0
    # if timeFrom <= 0:
    #    offset = -86400
    hrFrom = (timeFrom - offset) / 3600
    minFrom = (hrFrom - np.floor(hrFrom)) * 60
    secFrom = (minFrom - np.floor(minFrom)) * 60
    cloudQualIndex[cloudQualIndexKeys[3]][i] = (
        "{:02d}".format(int(np.floor(hrFrom)))
        + "{:02d}".format(int(np.floor(minFrom)))
        + "{:02d}".format(int(np.floor(secFrom)))
    )

    timeTil = int(newData["Time"][end - 1])
    if timeTil >= 86400:
        offset = 86400
    else:
        offset = 0
    # if timeTil <= 0:
    #    offset = -86400
    hrTil = (timeTil - offset) / 3600
    minTil = (hrTil - np.floor(hrTil)) * 60
    secTil = (minTil - np.floor(minTil)) * 60
    # print(hrTil, minTil, secTil)
    cloudQualIndex[cloudQualIndexKeys[4]][i] = (
        "{:02d}".format(int(np.floor(hrTil)))
        + "{:02d}".format(int(np.floor(minTil)))
        + "{:02d}".format(int(np.floor(secTil)))
    )

    # numQualIndicators = 4
    cloudQualIndex[cloudQualIndexKeys[5]][i] = np.nanmean(newData["ATX"][start:end])
    cloudQualIndex[cloudQualIndexKeys[6]][i] = np.nanmin(newData["ATX"][start:end])
    cloudQualIndex[cloudQualIndexKeys[7]][i] = np.nanmax(newData["ATX"][start:end])

    # ["Offset", "Scale", "Skew", "Kurt", "chisqr", "chisqrp"] offset from 7
    # numQualIndicators = 6
    # numQualOffset = 8
    for j in range(
        numInstruments
    ):  # 4):  # Four instruments that will have indices compared to CDP
        instrument = cloudQualIndexKeys[numQualOffset + j * numQualIndicators].split("-")[
            0
        ]
        cdpTrace = cloudEncDict["PLWCD_RWIO"][start:end]
        insTrace = cloudEncDict[instrument][start:end]
        cloudQualIndex[cloudQualIndexKeys[numQualOffset + j * numQualIndicators]][i] = (
            insTrace[-1] - cdpTrace[-1]
        )
        cloudQualIndex[cloudQualIndexKeys[numQualOffset + 1 + j * numQualIndicators]][
            i
        ] = (insTrace[-1] / cdpTrace[-1])
        # Need to add the r^2 parameter.
        insTrace = cdpTrace - insTrace * (
            1.0
            / cloudQualIndex[cloudQualIndexKeys[numQualOffset + j * numQualIndicators]][i]
        )

        cdpTrace = newData["PLWCD_RWIO"][start:end]

        insTrace = cdpTrace - newData[instrument][start:end] * (
            1.0
            / cloudQualIndex[
                cloudQualIndexKeys[numQualOffset + 1 + j * numQualIndicators]
            ][i]
        )

        # I can either calculate the instrument trace based on cumulative or real time?
        # insTrace = cdpTrace / newData[instrument][start:end]

        insTrace = (
           cloudEncDict["PLWCD_RWIO"][start:end] - cloudEncDict[instrument][start:end]
        )

        '''
        if (
            cloudEncMeans["cloudIDPhase"][i] > 1 and "PLWCC" in instrument
        ):  # and cloudEncMeans["cloudIDPhase"][i] > 0:
            plt.figure()
            plt.plot(newData["PLWCD_RWIO"][start:end])
            plt.plot(newData["PLWCC"][start:end])
            # plt.plot(newData["CLHCWC"][start:end])
            """
            plt.plot(
                newData[instrument][start:end]
                * (
                    1.0
                    / cloudQualIndex[
                        cloudQualIndexKeys[numQualOffset + 1 + j * numQualIndicators]
                    ][i]
                )
            )
            """
            plt.title(instrument)
            plt.figure()
            try:
                plt.hist(insTrace)
            except:
                pass
            plt.show()
        '''

        # This is the proof of the pudding.
        cloudQualIndex[cloudQualIndexKeys[numQualOffset + 2 + j * numQualIndicators]][
            i
        ] = scps.skew(
            insTrace
        )  # / (np.sqrt(end - start))
        # Skewness may need to be scaled to the mean loss (i.e. final value)

        cloudQualIndex[cloudQualIndexKeys[numQualOffset + 3 + j * numQualIndicators]][
            i
        ] = scps.kurtosis(insTrace) / (
            1#np.sqrt(end - start)
        )  # tstd(insTrace)
        # scps.kurtosis(insTrace)
        # print(cloudQualIndexKeys[10 + j * numQualIndicators])

        cloudQualIndex[cloudQualIndexKeys[numQualOffset + 4 + j * numQualIndicators]][
            i
        ] = scps.chisquare(insTrace)[0]
        cloudQualIndex[cloudQualIndexKeys[numQualOffset + 5 + j * numQualIndicators]][
            i
        ] = scps.chisquare(insTrace)[1]

        if "cloud" not in instrument:
            instrace = newData[instrument][start:end]
        else:
            instrace = data[instrument][start:end]
        cloudQualIndex[cloudQualIndexKeys[numQualOffset + 6 + j * numQualIndicators]][
            i
        ] = scps.tstd(instrace[~np.isnan(instrace)])

        # print(instrument)
        # if "cloud" in instrument:
        #    print(newData[instrument][start:end])
        #    print(scps.tstd(newData[instrument][start:end])[0])

    # print(flight)

    # Attempt a normalization to the CLH-2 data
    """
    for j in range(1, 5):
        cloudEncDict[cloudEncKeys[j]][start:end] *= (
            cloudEncDict[cloudEncKeys[0]][end - 1]
        ) / (cloudEncDict[cloudEncKeys[j]][end - 1])
    """
    # for j in range(0, 5):
    #    cloudEncDict[cloudEncKeys[j]][start:end] /= cloudEncDict[cloudEncKeys[j]][end - 1]
    # if end - start < 300: continue
    # if cloudEncDict['PLWCD_RWIO'][end-1]>1: continue

    # RF11 case studies
    #   3:30:00 to 3:45:00  #Emphasize pass 3:41:48 for 30 seconds, clean changeover liquid to ice
    #   4:07:00 to 4:34:00  #Multiple cloud encounters, another transition
    #       4:21:05 - 4:21:50 AND 4:32:15 - 4:33:00

    # RF12 case studies:
    #   4:25:00 to 4:43:20  #Long pass minor icing. Strange end behavior
    #   5:10:20 to 5:14:00  #Two passes, ascent and descent

    # RF9 case studies
    #   3:00:00 - 3:15:00 #Blockage
    #   4:10:00 - 4:25:00 #Blockage
    #   4:36:00 - 4:38:00 (IDEAL ICE ONLY REGION)

    # RF13 (strong CDP CVI agreement)
    # 100831 s to 100904
    # 4:41:00 (large droplet sizes?)

    # RF 14 Case study (supercooled?)
    #   3:21:24 - 3:23:55
    #   2:22:33 - 2:54:38 (best case for icing?)

    # RF08
    # 12:22:54 - 12:58:19 - Address loss of big ice crystals?
    # 3:03:41 - 3:58:40 - Med/Heav icing?

    # Latent head calculation...
    #
    
    
    ######################### RF07 AND RF09 FROM ZHAO PAPER #############################
    # rf07 20180131 4:44:20–4:45:47 and rf09 20180205 4:57:00–4:59:10
    focusFlight = 7
    time1 = 4*60*60 + 44*60 + 20
    time2 = 4*60*60 + 45*60 + 47
    
    #focusFlight = 9
    #time1 = 4*60*60 + 57*60 + 0
    #time2 = 4*60*60 + 59*60 + 10

    #focusFlight = 9
    if focusFlight == 9: offset = 86400
    else: offset = 0

    #offset = 86400
    if np.min(newData["Time"][np.where(newData["FlightNum"] == focusFlight)[0]]) > 86400:
        offset = 86400
        
    time1 += offset
    time2 += offset

    #time1 = 4 * 60 * 60 + 10 * 60 + 0 + offset
    #time2 = 4 * 60 * 60 + 25 * 60 + 0 + offset

    if flight != focusFlight:
        continue

    focusTime = np.arange(time1, time2, dtype="int")
    # print(list(np.round(newData["Time"][start:end])))


    #print(focusTime)

    check = any(
        item in list(np.round(newData["Time"][start:end])) for item in list(focusTime)
    )
    if not check:
        continue

    # if 10900 + 86400 not in np.round(newData["Time"][start:end]):
    #    continue

    # if cloudEncDict['PLWCD_RWIO'][end-1] < 100: continue
    # plt.figure()
    # plt.scatter(cloudEncDict['PLWCC'][end-1]/cloudEncDict['PLWCD_RWIO'][end-1],(np.nanmean(newData['ATX'][start:end])))#,marker='.',cmap='magma',alpha=0.2)#,marker='s')
    # cloudEncDict["cloudIDPhase"] /= 4.0
    # plt.figure(figsize=(16, 9))
    legend_elements = []
    for key, color in zip(cloudEncKeys[:-3], cloudEncColor[:-3]):
        # plt.plot(
        #    range(0, end - start), newData[key][start:end], c=color
        # )  # cloudEncDict[key][start:end], c=color)
        plt.plot(range(0, end - start), newData[key][start:end], c=color)
        #plt.plot(range(0, end - start), cloudEncDict[key][start:end], c=color)
        legend_elements.append(Line2D([0], [0], marker="_", label=key, color=color))

    # Added to overplot zones of water
    #plt.plot(range(0, end - start), newData["cloudIDPhase"][start:end] * 50, c="y")
    plt.plot(range(0, end - start), newData["cloudIDPhase"][start:end], c="y")

    timeFrom = int(newData["Time"][start])
    hrFrom = (timeFrom - offset) / 3600
    minFrom = (hrFrom - np.floor(hrFrom)) * 60
    secFrom = (minFrom - np.floor(minFrom)) * 60
    plt.title(
        "Time elapsed from: "
        + str(timeFrom)
        + " ("
        + "{:02d}".format(int(np.floor(hrFrom)))
        + ":"
        + "{:02d}".format(int(np.floor(minFrom)))
        + ":"
        + "{:02d}".format(int(np.floor(secFrom)))
        + "), Kurtosis: "
        + str(cloudQualIndex["CLHCWC-Kurt"][i]),
        fontsize=28,
        fontweight="bold",
    )

    # plt.figure()
    # plt.scatter(newData["PSXC"][start:end], newData[cloudEncKeys[0]][start:end])
    # plt.scatter(newData["PSXC"][start:end], newData[cloudEncKeys[1]][start:end])
    # plt.scatter(newData["PSXC"][start:end], newData[cloudEncKeys[2]][start:end])

    #    plt.scatter(cloudEncDict['PLWCD_RWIO'][end-1]/cloudEncDict['PLWCC'][end-1],cloudEncDict['PLWCD_RWIO'][end-1]/cloudEncDict[key][end-1],c=color,marker='o')
    # plt.scatter(np.nanmean(np.diff(cloudEncDict['ATX'][start:end])),cloudEncDict['PLWCD_RWIO'][end-1]/cloudEncDict[key][end-1],c=color)
    # plt.scatter(cloudEncDict['PLWCPIP_RWII'][end-1]/cloudEncDict['PLWCD_RWIO'][end-1], cloudEncDict['PLWCD_RWIO'][end-1]/cloudEncDict['CLHOld'][end-1])
    # plt.scatter(cloudEncDict['PLWCPIP_RWII'][end-1]/(end-start),(cloudEncDict['CVCWCC'][end-1]/cloudEncDict['CLHOld'][end-1]),c='black')
    # plt.scatter(np.nanmean(newData[' temp1'][start:end]-newData[' temp2'][start:end]),(cloudEncDict['CVCWCC'][end-1]/cloudEncDict['CLHOld'][end-1]),c='black')
    # plt.scatter(cloudEncDict['CONCD_RWIO'][end-1],cloudEncDict['PLWCD_RWIO'][end-1]-cloudEncDict['CVCWCC'][end-1],c='red')
    # if i == 10: break
#plt.show()
#exit()

plt.gca().autoscale(enable=True, tight=True)  # axis="x", tight=True)
plt.xlabel("Time(s)", fontsize=24, fontweight="bold")  # ,fs,30)
plt.ylabel("Water Contents (g/m^3)", fontsize=24, fontweight="bold")
plt.tick_params(axis="x", labelsize=20)
plt.tick_params(axis="y", labelsize=20)
# plt.gca().legend(handles=legend_elements, loc="upper right", fontsize=24, markerscale=3)
plt.gca().legend(handles=legend_elements, loc="upper left", fontsize=24, markerscale=3)
# plt.title("Water Content Intercomparisons", fontsize=28, fontweight="bold")
plt.tight_layout()
# plt.savefig(
#    basePath + "PNG/Poster/TESTY.png", dpi=600, bbox_inches="tight", transparent=True
# )
plt.show()
exit()

"""
cloudEncKeys = [
    "CLHOld",
    "CVCWCC",
    "PLWCD_RWIO",
    "PLWCC",
    "PLWCPIP_RWII",
    "RICE",
    "CONCD_RWIO",
    "DBARD_RWIO",
    "ATX",
]
cloudEncColor = ["black", "red", "green", "blue", "purple", "orange", "yellow", "brown"]
"""
redData = np.where(cloudQualIndex["PLWCC-chisqr"] < 0.1)[0]
"""
for i, index in enumerate(redData):
    print(
        "RF"
        + str(cloudQualIndex["flightNum"][index])
        + "\t, Start: "
        + cloudQualIndex["startUTC(hhmmss)"][index]
        + "\t, End: "
        + cloudQualIndex["endUTC(hhmmss)"][index]
    )
"""


# Only liquid cloud, where ATX does not fall below 0..... min(ATX) > 0
endVals = np.array(cloudEncDict["End"]) - 1

redDataQual = np.where(
    (cloudQualIndex["flightNum"] > 4)
    * (cloudQualIndex["avgATX"] > -100)
    # * (cloudEncDict["PLWCPIP_RWII"][endVals] < 1)
    # * (cloudEncDict["CONCD_RWIO"][endVals] <= 1)
)[0]
redData = endVals[redDataQual]
# redData = cloudQualIndex["End"][redData]
# plt.figure()
# plt.scatter(
#    cloudEncDict["CLHCWC"][redData] - cloudEncDict["PLWCD_RWIO"][redData],
#    cloudEncDict["PLWCPIP_RWII"][redData],
#    c=cloudQualIndex["avgATX"][redDataQual],
#    # c=cloudEncDict["PLWCC"][redData] - cloudEncDict["PLWCD_RWIO"][redData]
#    # c=cloudQualIndex["minATX"],
# )
# plt.colorbar()
# plt.show()
# exit()

# plt.figure()

# plt.scatter(
#    cloudEncDict["PLWCC"][endVals] - cloudEncDict["PLWCD_RWIO"][endVals],
#    cloudEncDict["PLWCPIP_RWII"][endVals],
#    c=(cloudQualIndex["avgATX"]),
# )
# plt.colorbar()
# plt.scatter(cloudEncDict["TCNTD_RWIO"][endVals], cloudEncDict["CONCD_RWIO"][endVals])
# plt.show()
# exit()

# plt.figure()
# plt.scatter(cloudQualIndex["avgATX"], cloudQualIndex["CLHCWC-Kurt"], color="black")
# plt.scatter(cloudQualIndex["avgATX"], cloudQualIndex["CLHCWC-Skew"], color="red")
# plt.scatter(cloudQualIndex["avgATX"], cloudQualIndex["CLHCWC-Scale"], color="green")
# plt.show()

for key in cloudQualIndexKeys:
    if "CVCWCC" in key or "PLWCC" in key or "CLHCWC" in key:
        if "Kurt" not in key and "Skew" not in key:
            continue
        instrument = key.split("-")[0]
        plt.figure(figsize=(12, 12))
        # print(cloudQualIndex["cloudIDPhase-std"][redDataQual])
        plt.scatter(
            # cloudQualIndex["avgATX"][redDataQual],  # cloudEncDict["ATX"][endVals],
            cloudQualIndex[key][redDataQual],
            # cloudEncDict["PLWCD_RWIO"][endVals[redDataQual]]
            # - cloudEncDict["CLHCWC"][endVals[redDataQual]],
            cloudEncMeans["cloudIDPhase"][redDataQual],
            # cloudQualIndex[instrument + "-Scale"][redDataQual],
            # c=np.log(np.log(cloudQualIndex[instrument + "-Scale"][redDataQual])),
            c=cloudQualIndex["cloudIDPhase-std"][redDataQual]
            # c=cloudEncMeans["cloudIDPhase"][
            #    redDataQual
            # ],  # (cloudQualIndex["flightNum"][redDataQual]),  # (cloudQualIndex["avgATX"]),
        )
        if "CVCWCC" in key:
            label = "CDP - CVI"
        if "CLH" in key:
            label = "CDP - CLH-2"
        if "PLWCC" in key:
            label = "CDP - KING"
        if "PLWCD" in key:
            label = "CDP - KING"

        # label += " Cloud Average"

        if "Kurt" in key:
            label = "(" + label + ") Cloud Mean Kurtosis"  # (g/m^3)"
        if "Skew" in key:
            label = "(" + label + ") Cloud Mean Skewness"  # (g/m^3)"

        plt.title(label, fontsize=28, fontweight="bold")
        # cb = plt.colorbar()  # label="Flight Number")  # , size=24, weight="bold")
        # cb.set_label(label="Flight Number", size=24, weight="bold")
        # plt.gca().autoscale(enable=True, tight=True)  # axis="x", tight=True)

        if "Kurt" in key:
            label = "Kurtosis (g/m^3)"
        if "Skew" in key:
            label = "Skewness (g/m^3)"

        plt.xlabel(label, fontsize=24, fontweight="bold")  # ,fs,30)
        plt.ylabel("Phase ID", fontsize=24, fontweight="bold")
        plt.tick_params(axis="x", labelsize=20)
        plt.tick_params(axis="y", labelsize=20)
        # plt.colorbar()
        cb = plt.colorbar()  # label="Flight Number")  # , size=24, weight="bold")
        cb.set_label(label="Cloud ID Encounter sigma", size=24, weight="bold")
        # plt.gca().legend(handles=legend_elements, loc="upper right", fontsize=24, markerscale=3)
        # plt.gca().legend(handles=legend_elements, loc="upper left", fontsize=24, markerscale=3)
        # plt.title("Water Content Intercomparisons", fontsize=28, fontweight="bold")
        plt.tight_layout()

        # plt.savefig(
        #    basePath + "PNG/Poster/" + key + ".png",
        #    dpi=600,
        #    bbox_inches="tight",
        #    transparent=True,
        # )
        # plt.savefig(
        #    basePath + "PNG/Poster/" + key + ".png",
        #    dpi=600,
        #    bbox_inches="tight",
        #    transparent=True,
        # )


# plt.figure()
# plt.plot(newData["CLHCWC"])
# plt.plot(newData["cloudIDPhase"])


plt.show()

# Plot only the events that have kurtosis greater than -0.38


# plt.plot(newData["CloudIndex"])
# plt.show()
exit()

# redData = np.where((newData['PLWCPIP_RWII']>1)*(newData['CONCD_RWIO']==0))[0]
redData = np.where((newData["TCNTD_RWIO"] > 0.5))[
    0
]  # *(newData['CONCD_RWIO']>0)*(newData['FlightNum']>1))[0]
newData["CloudIndex"][redData] = 1

plt.plot(newData["CVCWCC"], "black")
plt.plot(newData["CLHCWC"], "red")
plt.plot(newData["PLWCD_RWIO"])
plt.plot(newData["PLWCC"])
plt.plot(newData["PLWCPIP_RWII"] * 0.01)
plt.plot(newData["PSXC"] / 3000)
plt.plot(newData["FlightNum"] * 0.05)

# plt.plot(newData['CLHOld'],'r'
plt.plot(newData["CloudTime"], newData["CLHOld"])
plt.plot(newData["CloudTime"], newData["CloudIndex"], "g", linestyle="", marker="o")

# red = [218000:220000]
# [45800:47000]
for i in range(1, 16):
    plt.figure()
    redData = np.where((newData["FlightNum"] == i) * (newData["CloudIndex"] != 0))[
        0
    ]  # *(newData['PLWCPIP_RWII']<1))[0]
    plt.plot((np.nancumsum(newData["CVCWCC"][redData])), "black")
    plt.plot((np.nancumsum(newData["CLHCWC"][redData])), "red")
    # plt.scatter(np.nancumsum(newData['CLHOld'][redData])-np.nancumsum(newData['PLWCD_RWIO'][redData]),newData['ATX'][redData])# newData[' temp1'][redData]-newData[' temp2'][redData])
    # plt.scatter(newData['ATX'][redData], newData[' temp1'][redData]-newData[' temp2'][redData])
    plt.plot((np.nancumsum(newData["PLWCD_RWIO"][redData])), "blue")
    plt.plot((np.nancumsum(newData["PLWCC"][redData])), "green")
    # plt.plot(np.nancumsum(newData['PLWCPIP_RWII'][redData])*0.01,'purple')
    # plt.legend(['CVI','CLH2','CDP','King'])#,'PIP'])
plt.plot(newData["FlightNum"][redData] * 0.01)


plt.plot(newData["CONCD_RWIO"])

plt.plot(newData["TCNTD_RWIO"] * 160 / 5000)
plt.plot(newData["CONCD_RWIO"])

plt.scatter(newData["TCNTD_RWIO"], newData["CLHOld"] * 5000 / 0.3)  # *0.3/5000)

# xM,yM = np.meshgrid(xC,laserCalTable['l1Temp'])
print(data.keys())
xM, yM, zM = np.meshgrid(
    newData["TCNTD_RWIO"], newData["CLHOld"], newData["PLWCPIP_RWII"]
)
# plt.scatter(w, M, c=p, marker='s')
redData = np.where((newData["CloudIndex"] != 0) * (newData["PLWCPIP_RWII"] < 1))[
    0
]  # *(newData['CONCD_RWIO']>0)*(newData['FlightNum']>1))[0]

# GOOD DEMO of Precipitation effect between the CLH2 and CVI
plt.scatter(
    newData["CLHOld"][redData],
    newData["PLWCD_RWIO"][redData],
    c=np.log(newData["PLWCPIP_RWII"][redData]),
    marker=".",
    cmap="magma",
    alpha=0.5,
)


redData = np.where((newData["PLWCPIP_RWII"] < 0.1) * (newData["PLWCD_RWIO"] > 0.05))[0]
plt.scatter(
    newData["CLHOld"][redData],
    newData["PLWCD_RWIO"][redData],
    c=np.log(newData["CONCD_RWIO"][redData]),
    marker=".",
    cmap="jet",
    alpha=0.1,
)


plt.scatter(
    newData["PLWCC"][redData],
    newData["PLWCD_RWIO"][redData],
    c=(newData["ATX"][redData]),
    marker=".",
    cmap="inferno",
    alpha=0.2,
)  # ,marker='s')
# plt.gray()


high = 0.8
max = 7
# redData = np.where(np.logical_and(newData['PLWCPIP_RWII'] > 1,(newData['CONCD_RWIO']==0),np.in1d(newData['FlightNum'],good+bad+ugly+[15])))[0]
redData = np.where((newData["PLWCPIP_RWII"] > 1) * (newData["CONCD_RWIO"] == 0))[0]
plt.figure(figsize=(12, 9))
plt.hexbin(
    newData["CLHOld"][redData],
    newData["CVCWCC"][redData],
    vmax=max,
    cmap=my_blues,
    extent=(0, high, 0, high),
)  # plt.cm.jet)
plt.hexbin(
    newData["CLHOld"][redData],
    newData["PLWCC"][redData],
    vmax=max,
    cmap=my_reds,
    extent=(0, high, 0, high),
)
plt.hexbin(
    newData["CLHOld"][redData],
    newData["PLWCD_RWIO"][redData],
    vmax=max,
    cmap=my_greens,
    extent=(0, high, 0, high),
)
plt.hexbin(
    newData["CLHOld"][redData],
    newData["PLWCPIP_RWII"][redData] * 0.01,
    vmax=max,
    cmap=my_purps,
    extent=(0, high, 0, high),
)
# plt.hexbin(newData['CLHOld'][redData],newData['RICE'][redData],vmax=max,cmap = my_grays,extent=(0,high,0,high))
plt.plot([0, high], [0, high], color="black", lw=5)
plt.xlabel("CLH-2 (g/m^3)", fontsize=24, fontweight="bold")  # ,fs,30)
plt.ylabel("Water Contents (g/m^3)", fontsize=24, fontweight="bold")
plt.tick_params(axis="x", labelsize=20)
plt.tick_params(axis="y", labelsize=20)
# plt.scatter(0,0,color='blue'); plt.scatter(0,0,color='red'); plt.scatter(0,0,color='green'); plt.scatter(0,0,color='purple')
legend_elements = [
    Line2D([0], [0], marker="o", label="CVI TDL (g/m^3)", markerfacecolor="b"),
    Line2D([0], [0], marker="o", label="King (g/m^3)", markerfacecolor="r"),
    Line2D([0], [0], marker="o", label="CDP (g/m^3)", markerfacecolor="g"),
    Line2D([0], [0], marker="o", label="PIP (g/m^3)", markerfacecolor="purple"),
]
plt.gca().legend(handles=legend_elements, loc="lower right", fontsize=24, markerscale=3)
plt.title("Water Content Intercomparisons", fontsize=28, fontweight="bold")
plt.tight_layout()  #
plt.savefig(
    basePath + "PNG/Poster/NoCloudPrecip.png",
    dpi=600,
    bbox_inches="tight",
    transparent=True,
)
plt.savefig(
    basePath + "PNG/Poster/NoCloudPrecip.eps",
    dpi=600,
    bbox_inches="tight",
    transparent=True,
)


# Data filtered in clouds and out of precip
high = 0.8
max = 10
# redData = np.where(np.logical_and(newData['PLWCPIP_RWII'] == 0,(newData['CONCD_RWIO']>0),np.in1d(newData['FlightNum'],good+bad+ugly+[15])))[0]
redData = np.where(
    (newData["PLWCPIP_RWII"] < 1)
    * (newData["CONCD_RWIO"] > 0)
    * (newData["FlightNum"] > 1)
)[0]
plt.figure(figsize=(12, 9))
plt.hexbin(
    newData["CLHOld"][redData],
    newData["CVCWCC"][redData],
    vmax=max,
    cmap=my_blues,
    extent=(0, high, 0, high),
)  # plt.cm.jet)
plt.hexbin(
    newData["CLHOld"][redData],
    newData["PLWCC"][redData],
    vmax=max,
    cmap=my_reds,
    extent=(0, high, 0, high),
)
plt.hexbin(
    newData["CLHOld"][redData],
    newData["PLWCD_RWIO"][redData],
    vmax=max,
    cmap=my_greens,
    extent=(0, high, 0, high),
)
# plt.hexbin(newData['CLHOld'][redData],newData['RICE'][redData]/10 - 0.1,vmax=max,cmap = my_purps,extent=(0,high,0,high))
# plt.hexbin(newData['CLHOld'][redData],newData['RICE'][redData],vmax=max,cmap = my_grays,extent=(0,high,0,high))
plt.plot([0, high], [0, high], color="black", lw=5)
plt.xlabel("CLH-2 (g/m^3)", fontsize=24, fontweight="bold")  # ,fs,30)
plt.ylabel("Water Contents (g/m^3)", fontsize=24, fontweight="bold")
plt.tick_params(axis="x", labelsize=20)
plt.tick_params(axis="y", labelsize=20)
# plt.scatter(0,0,color='blue'); plt.scatter(0,0,color='red'); plt.scatter(0,0,color='green'); plt.scatter(0,0,color='purple')
legend_elements = [
    Line2D([0], [0], marker="o", label="CVI TDL (g/m^3)", markerfacecolor="b"),
    Line2D([0], [0], marker="o", label="King (g/m^3)", markerfacecolor="r"),
    Line2D([0], [0], marker="o", label="CDP (g/m^3)", markerfacecolor="g"),
]  # ,\
# Line2D([0],[0],marker='o',label='PIP (g/m^3)',markerfacecolor='purple')]
plt.gca().legend(handles=legend_elements, loc="lower right", fontsize=24, markerscale=3)
plt.title("Water Content Intercomparisons", fontsize=28, fontweight="bold")
plt.tight_layout()  #
plt.savefig(
    basePath + "PNG/Poster/NoPrecip.png", dpi=600, bbox_inches="tight", transparent=True
)
plt.savefig(
    basePath + "PNG/Poster/NoPrecip.eps", dpi=600, bbox_inches="tight", transparent=True
)


# Showing CDP correlations based on difference to CONCD
high = 0.5
max = 15
# redData = np.where(np.logical_and(newData['PLWCPIP_RWII'] == 1,(newData['CONCD_RWIO']>0),np.in1d(newData['FlightNum'],good+bad+ugly+[15])))[0]
redData = np.where(
    (newData["PLWCPIP_RWII"] < 1)
    * (newData["CONCD_RWIO"] > 0)
    * (newData["FlightNum"] > 1)
)[0]
plt.figure(figsize=(12, 9))
# plt.hexbin(newData['CLHOld'][redData] - newData['CVCWCC'][redData],newData['CONCD_RWIO'][redData],vmax=max,cmap=my_blues,extent=(-0.2,0.1,0,300))#plt.cm.jet)
plt.hexbin(
    newData["CLHOld"][redData] - newData["PLWCD_RWIO"][redData],
    newData["CONCD_RWIO"][redData],
    vmax=max,
    cmap=my_blues,
    extent=(-0.15, 0.05, 0, 300),
)
plt.hexbin(
    newData["CVCWCC"][redData] - newData["PLWCD_RWIO"][redData],
    newData["CONCD_RWIO"][redData],
    vmax=max * 1.5,
    cmap=my_reds,
    extent=(-0.15, 0.05, 0, 300),
)
# plt.hexbin(newData['PLWCC'][redData] - newData['PLWCD_RWIO'][redData]/10 - 0.1,newData['CONCD_RWIO'][redData],vmax=max,cmap = my_purps,extent=(-0.2,0.1,0,300))
# plt.hexbin(newData['RICE'][redData],newData['PLWCD_RWIO'][redData],vmax=max,cmap = my_grays,extent=(0,high,0,high))
plt.plot([0, -0.066], [0, 300], color="black", lw=5)
plt.xlabel("Delta Water Content (g/m^3)", fontsize=24, fontweight="bold")  # ,fs,30)
plt.ylabel("CDP Number Concentration (#/cc)", fontsize=24, fontweight="bold")
plt.tick_params(axis="x", labelsize=20)
plt.tick_params(axis="y", labelsize=20)
# plt.scatter(0,0,color='blue'); plt.scatter(0,0,color='red'); plt.scatter(0,0,color='green'); plt.scatter(0,0,color='purple')
legend_elements = [
    Line2D([0], [0], marker="o", label="CLH-2 (g/m^3)", markerfacecolor="b"),
    Line2D([0], [0], marker="o", label="CVI (g/m^3)", markerfacecolor="r"),
]  # ,\
# Line2D([0],[0],marker='o',label='King (g/m^3)',markerfacecolor='g')]#,\
# Line2D([0],[0],marker='o',label='PIP (g/m^3)',markerfacecolor='purple')]
plt.gca().legend(handles=legend_elements, loc="upper right", fontsize=24, markerscale=3)
plt.title("Difference from CDP vs CDP #/cc", fontsize=28, fontweight="bold")
plt.tight_layout()  #
plt.savefig(
    basePath + "PNG/Poster/CONCDvsCWCError.png",
    dpi=600,
    bbox_inches="tight",
    transparent=True,
)
plt.savefig(
    basePath + "PNG/Poster/CONCDvsCWCError.eps",
    dpi=600,
    bbox_inches="tight",
    transparent=True,
)


# Data filtered in clouds and out of precip
high = 0.8
max = 10
# redData = np.where(np.logical_and(np.logical_and(newData['PLWCPIP_RWII'] <= 1,newData['CONCD_RWIO']>0),newData['FlightNum']>4))[0]#np.in1d(newData['FlightNum'],range(5,16))))[0]
redData = np.where(
    (newData["PLWCPIP_RWII"] <= 1)
    * (newData["CONCD_RWIO"] > 0)
    * (newData["FlightNum"] > 4)
)[
    0
]  # *(newData['CWCIceFrac']>=-100))[0])
plt.figure(figsize=(12, 9))
plt.hexbin(
    newData["CLHOld"][redData] + (1 / 2000) * newData["CONCD_RWIO"][redData],
    newData["CVCWCC"][redData] + (1 / 2000) * newData["CONCD_RWIO"][redData],
    vmax=max,
    cmap=my_blues,
    extent=(0, high, 0, high),
)  # plt.cm.jet)
plt.hexbin(
    newData["CLHOld"][redData] + (1 / 2000) * newData["CONCD_RWIO"][redData],
    newData["PLWCC"][redData],
    vmax=max,
    cmap=my_reds,
    extent=(0, high, 0, high),
)
plt.hexbin(
    newData["CLHOld"][redData] + (1 / 2000) * newData["CONCD_RWIO"][redData],
    newData["PLWCD_RWIO"][redData],
    vmax=max,
    cmap=my_greens,
    extent=(0, high, 0, high),
)
# plt.hexbin(newData['CLHOld'][redData] + (1/2000)*newData['CONCD_RWIO'][redData],newData['RICE'][redData]/10 - 0.1,vmax=max,cmap = my_purps,extent=(0,high,0,high))
# plt.hexbin(newData['CLHOld'][redData],newData['RICE'][redData],vmax=max,cmap = my_grays,extent=(0,high,0,high))
plt.plot([0, high], [0, high], color="black", lw=5)
plt.xlabel("CLH-2 (g/m^3)", fontsize=24, fontweight="bold")  # ,fs,30)
plt.ylabel("Water Contents (g/m^3)", fontsize=24, fontweight="bold")
plt.tick_params(axis="x", labelsize=20)
plt.tick_params(axis="y", labelsize=20)
plt.set_xscale = "log"
plt.set_yscale = "log"
# plt.scatter(0,0,color='blue'); plt.scatter(0,0,color='red'); plt.scatter(0,0,color='green'); plt.scatter(0,0,color='purple')
legend_elements = [
    Line2D([0], [0], marker="o", label="CVI TDL (g/m^3)", markerfacecolor="b"),
    Line2D([0], [0], marker="o", label="King (g/m^3)", markerfacecolor="r"),
    Line2D([0], [0], marker="o", label="CDP (g/m^3)", markerfacecolor="g"),
]  # ,\
# Line2D([0],[0],marker='o',label='PIP (g/m^3)',markerfacecolor='purple')]
plt.gca().legend(handles=legend_elements, loc="lower right", fontsize=24, markerscale=3)
plt.title("Water Content Intercomparisons", fontsize=28, fontweight="bold")
plt.tight_layout()  #
plt.savefig(
    basePath + "PNG/Poster/CDPCorr.png", dpi=600, bbox_inches="tight", transparent=True
)
plt.savefig(
    basePath + "PNG/Poster/CDPCorr.eps", dpi=600, bbox_inches="tight", transparent=True
)


plt.loglog(
    newData["CLHOld"][redData] + (1 / 2000) * newData["CONCD_RWIO"][redData],
    newData["CVCWCC"][redData] + (1 / 2000) * newData["CONCD_RWIO"][redData],
    linestyle="",
    marker="o",
    markersize=1,
    alpha=0.1,
)
plt.xlim(0.01, 1)
plt.ylim(0.01, 1)


# Data corrected for CONCD and where PLWCC == 0
high = 0.5
max = 2
# redData = np.where(np.logical_and(np.logical_and(np.logical_and(newData['PLWCC']<0.02,newData['PLWCPIP_RWII'] <= 1)\
#    ,newData['CONCD_RWIO']>0),newData['FlightNum']>=5))[0]#np.in1d(newData['FlightNum'],good+bad+ugly+[15])))[0]
redData = np.where(
    (newData["PLWCC"] == 0)
    * (newData["PLWCPIP_RWII"] <= 1)
    * (newData["CONCD_RWIO"] > 0)
    * (newData["FlightNum"] > 1)
)[
    0
]  # *(newData['CWCIceFrac']>=-100))[0])
plt.figure(figsize=(12, 9))
plt.hexbin(
    newData["CLHOld"][redData] + (1 / 2000) * newData["CONCD_RWIO"][redData],
    newData["CVCWCC"][redData] + (1 / 2000) * newData["CONCD_RWIO"][redData],
    vmax=max,
    cmap=my_blues,
    extent=(0, high, 0, high),
)  # plt.cm.jet)
plt.hexbin(
    newData["CLHOld"][redData] + (1 / 2000) * newData["CONCD_RWIO"][redData],
    newData["PLWCC"][redData],
    vmax=max,
    cmap=my_reds,
    extent=(0, high, 0, high),
)
plt.hexbin(
    newData["CLHOld"][redData] + (1 / 2000) * newData["CONCD_RWIO"][redData],
    newData["PLWCD_RWIO"][redData],
    vmax=max,
    cmap=my_greens,
    extent=(0, high, 0, high),
)
# plt.hexbin(newData['CLHOld'][redData] + (1/2000)*newData['CONCD_RWIO'][redData],newData['RICE_s'][redData]/5 - 0.12,vmax=max,cmap = my_purps,extent=(0,high,0,high))
# plt.hexbin(newData['CLHOld'][redData],newData['RICE'][redData],vmax=max,cmap = my_grays,extent=(0,high,0,high))
plt.plot([0, high], [0, high], color="black", lw=5)
plt.xlabel("CLH-2 (g/m^3)", fontsize=24, fontweight="bold")  # ,fs,30)
plt.ylabel("Water Contents (g/m^3)", fontsize=24, fontweight="bold")
plt.tick_params(axis="x", labelsize=20)
plt.tick_params(axis="y", labelsize=20)
# plt.scatter(0,0,color='blue'); plt.scatter(0,0,color='red'); plt.scatter(0,0,color='green'); plt.scatter(0,0,color='purple')
legend_elements = [
    Line2D([0], [0], marker="o", label="CVI TDL (g/m^3)", markerfacecolor="b"),
    Line2D([0], [0], marker="o", label="King (g/m^3)", markerfacecolor="r"),
    Line2D([0], [0], marker="o", label="CDP (g/m^3)", markerfacecolor="g"),
]  # ,\
# Line2D([0],[0],marker='o',label='PIP (g/m^3)',markerfacecolor='purple')]
plt.gca().legend(handles=legend_elements, loc="lower right", fontsize=24, markerscale=3)
plt.title("Ice Content Intercomparisons", fontsize=28, fontweight="bold")
plt.tight_layout()  #
plt.savefig(
    basePath + "PNG/Poster/IceCloud.png", dpi=600, bbox_inches="tight", transparent=True
)
plt.savefig(
    basePath + "PNG/Poster/IceCloud.eps", dpi=600, bbox_inches="tight", transparent=True
)


newData["CWCIceFrac"] = (
    newData["PLWCD_RWIO"] - newData["PLWCC"]
)  # newData['CLHOld']-newData['PLWCC']
newData["CWCCVIvCLH"] = newData["CLHCWC"] - newData["CLHOld"]


plt.scatter(
    newData["CWCIceFrac"][redData], newData["ATTACK"][redData]
)  # ,vmax=10,cmap = my_blues)#,extent=(-2.5,2.5,0,200000))
plt.hexbin(
    np.arange(0, len(redData)), newData["CWCIceFrac"][redData], vmax=50
)  # ,linestyle='',marker='o',markersize=1)
plt.plot(
    np.arange(0, len(redData)),
    newData["CWCIceFrac"][redData],
    linestyle="",
    marker="o",
    markersize=1,
)

plt.figure()
plt.plot(
    np.arange(0, len(redData)),
    newData["CWCIceFrac"][redData],
    linestyle="",
    marker="o",
    markersize=1,
)

redData = np.where(
    (newData["PLWCC"] > 0)
    * (newData["PLWCPIP_RWII"] <= 1)
    * (newData["CONCD_RWIO"] > 0)
    * (newData["FlightNum"] > 4)
    * (newData["CWCIceFrac"] >= -9999)
)[0]
plt.figure()
plt.plot(newData["tCounts_CVIU_UHSAS"][redData])


boundScale = 3
# plt.plot(newData['FlightNum'])
newData["CWCIceFrac"] = (
    newData["PLWCD_RWIO"] - newData["PLWCC"]
)  # newData['CLHOld']-newData['PLWCC']
newData["CWCCVIvCLH"] = newData["CLHCWC"] - newData["CLHOld"]
high = 0.8
max = 10
redData = np.where(
    (newData["PLWCC"] > 0)
    * (newData["PLWCPIP_RWII"] <= 1)
    * (newData["CONCD_RWIO"] > 0)
    * (newData["FlightNum"] > 4)
    * np.logical_and(
        newData["CWCIceFrac"] >= -0.01 - 0.01 * boundScale,
        newData["CWCIceFrac"] <= -0.01 + 0.0002 + 0.01 * boundScale,
    )
)[0]
plt.figure(figsize=(12, 9))
plt.hexbin(
    newData["CLHOld"][redData] + (1 / 2000) * newData["CONCD_RWIO"][redData],
    newData["CVCWCC"][redData] + (1 / 2000) * newData["CONCD_RWIO"][redData],
    vmax=max,
    cmap=my_blues,
    extent=(0, high, 0, high),
)  # plt.cm.jet)
plt.hexbin(
    newData["CLHOld"][redData] + (1 / 2000) * newData["CONCD_RWIO"][redData],
    newData["PLWCC"][redData],
    vmax=max,
    cmap=my_reds,
    extent=(0, high, 0, high),
)
plt.hexbin(
    newData["CLHOld"][redData] + (1 / 2000) * newData["CONCD_RWIO"][redData],
    newData["PLWCD_RWIO"][redData],
    vmax=max,
    cmap=my_greens,
    extent=(0, high, 0, high),
)
# plt.hexbin(newData['CLHOld'][redData] + (1/2000)*newData['CONCD_RWIO'][redData],newData['RICE_s'][redData]/10-0.14,vmax=max,cmap = my_purps,extent=(0,high,0,high))
# plt.hexbin(newData['CLHOld'][redData],newData['RICE'][redData],vmax=max,cmap = my_grays,extent=(0,high,0,high))
plt.plot([0, high], [0, high], color="black", lw=5)
plt.xlabel("CLH-2 (g/m^3)", fontsize=24, fontweight="bold")  # ,fs,30)
plt.ylabel("Water Contents (g/m^3)", fontsize=24, fontweight="bold")
plt.tick_params(axis="x", labelsize=20)
plt.tick_params(axis="y", labelsize=20)
# plt.scatter(0,0,color='blue'); plt.scatter(0,0,color='red'); plt.scatter(0,0,color='green'); plt.scatter(0,0,color='purple')
legend_elements = [
    Line2D([0], [0], marker="o", label="CVI TDL (g/m^3)", markerfacecolor="b"),
    Line2D([0], [0], marker="o", label="King (g/m^3)", markerfacecolor="r"),
    Line2D([0], [0], marker="o", label="CDP (g/m^3)", markerfacecolor="g"),
]  # ,\
# Line2D([0],[0],marker='o',label='PIP (g/m^3)',markerfacecolor='purple')]
plt.gca().legend(handles=legend_elements, loc="lower right", fontsize=24, markerscale=3)
plt.title("Liquid Water Intercomparisons", fontsize=28, fontweight="bold")
plt.tight_layout()  #
plt.savefig(
    basePath + "PNG/Poster/LiquidCloud.png",
    dpi=600,
    bbox_inches="tight",
    transparent=True,
)
plt.savefig(
    basePath + "PNG/Poster/LiquidCloud.eps",
    dpi=600,
    bbox_inches="tight",
    transparent=True,
)


high = 0.8
max = 10
redData = np.where(
    (newData["PLWCC"] > 0)
    * (newData["PLWCPIP_RWII"] <= 1)
    * (newData["CONCD_RWIO"] > 0)
    * (newData["FlightNum"] > 4)
    * ~np.logical_and(
        newData["CWCIceFrac"] >= -0.01 - 0.01 * boundScale,
        newData["CWCIceFrac"] <= -0.01 + 0.0002 + 0.01 * boundScale,
    )
)[0]
plt.figure(figsize=(12, 9))
plt.hexbin(
    newData["CLHOld"][redData],
    newData["CVCWCC"][redData],
    vmax=max,
    cmap=my_blues,
    extent=(0, high, 0, high),
)  # plt.cm.jet)
plt.hexbin(
    newData["CLHOld"][redData],
    newData["PLWCC"][redData],
    vmax=max,
    cmap=my_reds,
    extent=(0, high, 0, high),
)
plt.hexbin(
    newData["CLHOld"][redData],
    newData["PLWCD_RWIO"][redData],
    vmax=max,
    cmap=my_greens,
    extent=(0, high, 0, high),
)
# plt.hexbin(newData['CLHOld'][redData] + (1/2000)*newData['CONCD_RWIO'][redData],newData['RICE_s'][redData]/10-0.14,vmax=max,cmap = my_purps,extent=(0,high,0,high))
# plt.hexbin(newData['CLHOld'][redData],newData['RICE'][redData],vmax=max,cmap = my_grays,extent=(0,high,0,high))
plt.plot([0, high], [0, high], color="black", lw=5)
plt.xlabel("CLH-2 (g/m^3)", fontsize=24, fontweight="bold")  # ,fs,30)
plt.ylabel("Water Contents (g/m^3)", fontsize=24, fontweight="bold")
plt.tick_params(axis="x", labelsize=20)
plt.tick_params(axis="y", labelsize=20)
# plt.scatter(0,0,color='blue'); plt.scatter(0,0,color='red'); plt.scatter(0,0,color='green'); plt.scatter(0,0,color='purple')
legend_elements = [
    Line2D([0], [0], marker="o", label="CVI TDL (g/m^3)", markerfacecolor="b"),
    Line2D([0], [0], marker="o", label="King (g/m^3)", markerfacecolor="r"),
    Line2D([0], [0], marker="o", label="CDP (g/m^3)", markerfacecolor="g"),
]  # ,\
# Line2D([0],[0],marker='o',label='PIP (g/m^3)',markerfacecolor='purple')]
plt.gca().legend(handles=legend_elements, loc="lower right", fontsize=24, markerscale=3)
plt.title("Mixed Phase Intercomparisons", fontsize=28, fontweight="bold")
plt.tight_layout()  #
plt.savefig(
    basePath + "PNG/Poster/MixedPhaseCloud.png",
    dpi=600,
    bbox_inches="tight",
    transparent=True,
)
plt.savefig(
    basePath + "PNG/Poster/MixedPhaseCloud.eps",
    dpi=600,
    bbox_inches="tight",
    transparent=True,
)


# Create the figure
fig, ax = plt.subplots()
ax.legend(handles=legend_elements, loc="center")


redData = np.where(newData["FlightNum"] == 6)[0]
plt.plot(newData["Flow factor"][redData])


plt.scatter(newData["CLHCWC"][233000:236000], newData["PLWCPIP_RWII"][233000:236000])


plt.plot(newData["CLHVMR"])
plt.plot(newData["VMR_VXL"])
plt.xlim(0)
plt.ylim(0, 75000)
plt.plot(newData[" staticppmv"])

plt.plot(newData["CVCWCC"])
plt.plot(newData["FlightNum"] * 0.1)
plt.plot(newData["CLHCWC"])

for i in range(6, 8):
    plt.figure()
    redData = np.where(newData["FlightNum"] == (i + 1))[0]
    # print(redData)
    # plt.plot(newData['CVCWCC'][redData],newData['CLHCWC'][redData],linestyle='', marker='o', markersize=4, alpha=0.2)
    plt.plot(
        newData["CVCWCC"][redData],
        newData["CLHCWC"][redData] * 1.8 / newData["Flow factor"][redData],
        linestyle="",
        marker="o",
        markersize=4,
        alpha=0.2,
    )
    plt.plot([0, 1], [0, 1])
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.title(str(i + 1))


# IF PIP is > 0.0001, I am assuming there is some level of drizzle/precip (useful check)
redData = np.where(newData["PLWCPIP_RWII"] > 0.01)[0]

# Style sheets
plt.style.use("dark_background")  # ,'seaborn-colorblind','ggplot'])
plt.style.use("seaborn-darkgrid")
plt.style.use("seaborn-poster")

# sns.regplot(x=newData['VMR_VXL'], y=newData[' staticppmv'], fit_reg=False, marker = "+", line_kws={"color":"r","alpha":0.5,"s":1})
redData = np.where(np.logical_and(newData["FlightNum"] > 1, newData["CVINLET"] == 0))[0]

redData = np.where(newData["FlightNum"] > 1)[0]
plt.scatter(
    newData["CLHCWC"] * 1.8 / newData["Flow factor"] / newData["CVCWCC"],
    newData["PLWCPIP_RWII"],
    s=1,
)


# plt.plot(newData['PLWCPIP_RWII'])
plt.scatter(newData["TCNTD_RWIO"], newData["CONCD_RWIO"])
domain = np.array(np.arange(0, len(data["domain"][redData])), dtype="float")
plt.plot(newData["domain"][redData], newData["CLHCWC"][redData])
plt.plot(newData["domain"][redData], newData["CVCWCC"][redData])
plt.plot(newData["domain"][redData], newData["PLWCC"][redData])
plt.plot(newData["domain"][redData], newData["PLWCD_RWIO"][redData] * 0.01)
plt.plot(newData["domain"][redData], newData["FlightNum"][redData] * 0.1)
plt.legend(["CLH", "CVI", "King", "CDP"])

plt.figure(figsize=(12, 9))
redData = np.where(
    np.logical_and(
        (newData["CONCD_RWIO"] > 0), np.in1d(newData["FlightNum"], good + bad + ugly)
    )
)[0]
# plt.hexbin(newData['CLHCWC'][redData],newData['CVCWCC'][redData] + 1/(3000)*newData['CONCD_RWIO'][redData],vmax=30,extent = (0,1,0,1),cmap=plt.cm.Reds)#,vmax=50,cmap=plt.cm.magma)
# plt.hexbin(newData['CVCWCC'][redData],newData['CLHCWC'][redData],vmax=50,extent = (0,1,0,1),cmap=plt.cm.Greens)#,vmax=50,cmap=plt.cm.magma)
# plt.hexbin(newData['CVCWCC'][redData],newData['CLHCWC'][redData]*1.8/newData['Flow factor'][redData],vmax=50,extent = (0,1,0,1),cmap=plt.cm.Greens)#,vmax=50,cmap=plt.cm.magma)
plt.hexbin(
    (newData["CVCWCC"][redData]) - newData["PLWCD_RWIO"][redData],
    newData["CONCD_RWIO"][redData],
    vmax=10,
    extent=(-0.5, 0.2, 0, 300),
    cmap=plt.cm.Greens,
)  # ,vmax=50,cmap=plt.cm.magma)

plt.xlabel("CLH-2 (g/m^3)", fontsize=18, fontweight="bold")  # ,fs,30)
plt.ylabel("CVI TDL (g/m^3)", fontsize=18, fontweight="bold")
plt.tick_params(axis="x", labelsize=16)
plt.tick_params(axis="y", labelsize=16)
# plt.ylim(30,80000)
# plt.xlim(30,80000)
# lgnd = plt.gca().legend(['CLH-2 vs VCSEL','CLH-2 vs CVI'],fontsize=20,markerscale=5,scatterpoints=1,loc="lower right")
plt.title("Water Content when CDP measures 0 #/cc", fontsize=22, fontweight="bold")
plt.colorbar()
plt.tight_layout()  #
plt.savefig(
    basePath + "PNG/CVIvsCONCD.png", dpi=200, bbox_inches="tight", transparent=True
)


# PLOTTING routine for saving all the flight individually
for flight in np.unique(newData["FlightNum"]):
    redData = np.where(newData["FlightNum"] == flight)[0]
    plt.figure(figsize=(16, 9))
    plt.plot(
        newData["CLHCWC"][redData],
        newData["CVCWCC"][redData],
        linestyle="",
        marker="o",
        markersize=1.0,
        alpha=0.7,
    )
    plt.plot(
        newData["CLHCWC"][redData],
        newData["PLWCC"][redData],
        linestyle="",
        marker="o",
        markersize=1.0,
        alpha=0.7,
    )
    plt.plot(
        newData["CLHCWC"][redData],
        newData["PLWCD_RWIO"][redData],
        linestyle="",
        marker="o",
        markersize=1.0,
        alpha=0.7,
    )
    # plt.plot(newData['CLHCWC'][redData],newData['PLWCPIP_RWII'][redData],color='red',linestyle='', marker='o', markersize=1.0, alpha=0.3)
    plt.plot([0, 2], [0, 2], lw=2)  # ,'r')
    plt.xlabel("CLH-2 CWC (g/m^3)", fontsize=24, fontweight="bold")  # ,fs,30)
    plt.ylabel("CWC (g/m^3)", fontsize=24, fontweight="bold")
    plt.tick_params(axis="x", labelsize=20)
    plt.tick_params(axis="y", labelsize=20)
    plt.ylim(0, 0.6)
    plt.xlim(0, 0.6)
    plt.gca().legend(
        ["CVI", "King", "CDP", "1-1"],
        fontsize=24,
        markerscale=24,
        scatterpoints=1,
        loc="lower right",
    )
    plt.title("CLH2 vs CDP/CVI", fontsize=28, fontweight="bold")
    plt.tight_layout()  #
    plt.savefig(
        basePath + "PNG/Corr_CWCScatter_Flight" + str(int(flight)) + ".png",
        dpi=200,
        bbox_inches="tight",
    )
    plt.close

sizeBoost = 10
plt.figure(figsize=(16, 9))
# plt.plot(newData['CLHCWC'][redData]*1.8/newData['Flow factor'][redData],newData['CVCWCC'][redData],linestyle='', marker='o', markersize=1, alpha=0.5)
plt.plot(
    newData["CLHCWC"][redData] * 1.8 / newData["Flow factor"][redData],
    newData["CVCWCC"][redData],
    linestyle="",
    marker="o",
    markersize=1,
    alpha=1,
)
# plt.plot(newData['CLHCWC'][redData]*1.8/newData['Flow factor'][redData],newData['PLWCC'][redData],linestyle='', marker='o', markersize=1, alpha=0.3)
# plt.plot(newData['CLHCWC'][redData]*1.8/newData['Flow factor'][redData],newData['PLWCD_RWIO'][redData],linestyle='', marker='o', markersize=1, alpha=0.3)
plt.plot([0, 2], [0, 2], lw=2)  # ,'r')
plt.xlabel("CLH-2 CWC (g/m^3)", fontsize=24 + sizeBoost, fontweight="bold")  # ,fs,30)
plt.ylabel("WC (g/m^3)", fontsize=24 + sizeBoost, fontweight="bold")
plt.tick_params(axis="x", labelsize=20 + sizeBoost)
plt.tick_params(axis="y", labelsize=20 + sizeBoost)
plt.ylim(0, 0.8)
plt.xlim(0, 0.6)
plt.gca().legend(
    ["CVI TDL", "King", "CDP", "1-1"],
    fontsize=24 + sizeBoost,
    markerscale=20,
    scatterpoints=1,
    loc="lower right",
)
plt.title("CLH2 vs CVI/King/CDP", fontsize=28 + sizeBoost, fontweight="bold")
plt.tight_layout()  #
plt.savefig(basePath + "PNG/CWCScatter_Skewed.png", dpi=200, bbox_inches="tight")
# plt.close

plt.figure()
plt.hexbin(
    newData["CLHCWC"][redData] * 1.8 / newData["Flow factor"][redData],
    newData["CVCWCC"][redData] + (1 / 2000) * newData["CONCD_RWIO"][redData],
    vmax=2,
    cmap=plt.cm.jet,
)

newData["RICE_s"] = deepcopy(newData["RICE"])
for i in range(25):
    newData["RICE_s"] = np.convolve(newData["RICE_s"], np.ones((15,)) / 15, mode="same")

redData = np.where(newData["FlightNum"] == 9)[0]
domain = newData["Time"][
    redData
]  # np.array(np.arange(0,len(data['domain'][redData])),dtype='float')
domain = newData["domain"][redData]
plt.figure(figsize=(12, 9))
plt.plot(
    domain, newData["CLHOld"][redData] + (1 / 2000) * newData["CONCD_RWIO"][redData]
)  # *1.8/newData['Flow factor'][redData])
plt.plot(domain, newData["PLWCC"][redData])
plt.plot(domain, newData["PLWCD_RWIO"][redData])
plt.plot(domain, newData["CVCWCC"][redData] + (1 / 2000) * newData["CONCD_RWIO"][redData])
plt.plot(domain, newData["FlightNum"][redData] * 0.1, lw=2)
plt.plot(domain, newData["ATTACK"][redData] * 0.1, lw=2)
plt.plot(domain, newData["PLWCPIP_RWII"][redData] * 0.01)  # ,color='white')
plt.plot(domain, newData["RICE"][redData] / 10, lw=3)  # ,marker='+',linestyle='')
plt.plot(domain, newData["RICE_s"][redData] / 10, lw=3)
plt.xlabel("Domain", fontsize=18, fontweight="bold")  # ,fs,30)
plt.ylabel("CWC (g/m^3)", fontsize=18, fontweight="bold")
plt.tick_params(axis="x", labelsize=16)
plt.tick_params(axis="y", labelsize=16)
plt.ylim(0, 2.0)
plt.gca().legend(
    ["CLH-2", "King", "CDP", "CVI", "FlightNum", "Attack", "PIP", "RICE", "RICE_s"],
    fontsize=20,
    markerscale=20,
    scatterpoints=1,
    loc="upper right",
)
plt.title("VCSEL vs CLH-2 Mixing Ratios", fontsize=22, fontweight="bold")
plt.tight_layout()  #
plt.savefig(basePath + "PNG/TimeComparison.png", dpi=200, bbox_inches="tight")


plt.figure(figsize=(16, 9))
plt.plot(
    data[" staticppmv"],
    data["VMR_VXL"],
    "r",
    color="white",
    linestyle="",
    marker="o",
    markersize=0.3,
)  # , alpha=0.3)
plt.plot([0, 20000], [0, 20000], "b", lw=2)
plt.xlabel("CLH-2 VMR (ppmv)", fontsize=24, fontweight="bold")  # ,fs,30)
plt.ylabel("VCSEL VMR (ppmv)", fontsize=24, fontweight="bold")
plt.tick_params(axis="x", labelsize=20)
plt.tick_params(axis="y", labelsize=20)
plt.xlim([0, 50000])
plt.ylim([0, 20000])
plt.title("CLH-2 vs VCSEL Mixing Ratios", fontsize=28, fontweight="bold")
plt.tight_layout()  #
plt.savefig(basePath + "PNG/CLH2vVCSEL.png", dpi=200, bbox_inches="tight")


# METHOD for density plots
redData = np.where(np.in1d(newData["FlightNum"], [2, 5, 8, 9, 10, 14]))[
    0
]  # Relatively good data
redData = np.where(newData["FlightNum"] > 0)[0]
plt.hexbin(
    newData["PLWCD_RWIO"][redData],
    newData["CLHCWC"][redData],
    mincnt=1,
    vmax=10,
    gridsize=(300, 300),
    cmap=plt.cm.jet,
    extent=(0.005, 0.5, 0.005, 0.5),
)  # ,cmap=plt.cm.jet)
plt.hexbin(
    newData[" staticppmv"],
    newData["VMR_VXL"],
    vmax=40,
    gridsize=(200, 200),
    cmap=plt.cm.magma,
)

# redData = np.where(np.logical_and(newData['PLWCPIP_RWII']>0.001,newData['FlightNum']>4))[0]
plt.hexbin(
    newData["CVCWCC"][redData],
    newData["CLHCWC"][redData] * 1.8 / newData["Flow factor"][redData],
    vmax=100,
    gridsize=(200, 200),
    extent=(-0.5, 0.2, -1, 1),
    cmap=plt.cm.jet,
)

plt.hexbin(
    newData["CVCWCC"][redData]
    + 1 / (3000) * newData["CONCD_RWIO"][redData]
    - newData["PLWCD_RWIO"][redData],
    newData["CONCD_RWIO"][redData],
    vmax=30,
    extent=(-0.2, 0.2, 0, 400),
    cmap=plt.cm.magma,
)

# Potential slope is -0.5 g/m^3 per 1000 #/cc
# So correction looks like
plt.plot(
    newData["CLHCWC"][redData],
    newData["CVCWCC"][redData] + 1 / (3000) * newData["CONCD_RWIO"][redData],
    linestyle="",
    marker="+",
    markersize=1,
    alpha=0.5,
)  # ,vmax=50,cmap=plt.cm.magma)
plt.plot(
    newData["CLHCWC"][redData],
    newData["CVCWCC"][redData],
    color="white",
    linestyle="",
    marker="+",
    markersize=1,
    alpha=0.5,
)  # ,vmax=50,cmap=plt.cm.magma)


plt.ylim(0, 0.5)
plt.xlim(0, 0.5)

redData = np.where(newData["FlightNum"] > 0)[0]

redData = np.where(np.logical_and(newData["CONCD_RWIO"] > 0, newData["FlightNum"] == 15))[
    0
]
redData = np.where(
    np.logical_and(
        (newData["CONCD_RWIO"] > 0), np.in1d(newData["FlightNum"], good + ugly + bad)
    )
)[0]
plt.hexbin(
    newData["CLHCWC"][redData],
    newData["CVCWCC"][redData] + 1 / (3000) * newData["CONCD_RWIO"][redData],
    vmax=500,
    extent=(0, 1, 0, 1),
    cmap=plt.cm.Reds,
)  # ,vmax=50,cmap=plt.cm.magma)
plt.hexbin(newData["CLHCWC"][redData], newData["RICE"][redData], vmax=50, cmap=plt.cm.jet)


plt.plot(
    newData["PLWCD_RWIO"][redData],
    newData["CVCWCC"][redData],
    linestyle="",
    marker="+",
    markersize=1,
    alpha=0.5,
)
plt.plot(
    newData["CLHCWC"][redData] * 1.8 / newData["Flow factor"][redData],
    newData["CVCWCC"][redData],
    linestyle="",
    marker="+",
    markersize=1,
    alpha=0.5,
)

plt.plot(
    newData["CLHCWC"][redData],
    newData["PLWCC"][redData],
    linestyle="",
    marker="+",
    markersize=1,
    alpha=0.5,
)
plt.plot(
    newData["CLHCWC"][redData] * 1.8 / newData["Flow factor"][redData],
    newData["PLWCC"][redData],
    linestyle="",
    marker="+",
    markersize=1,
    alpha=0.5,
)

plt.plot(
    newData["CLHCWC"][redData],
    newData["PLWCD_RWIO"][redData],
    linestyle="",
    marker="+",
    markersize=1,
    alpha=0.5,
)
plt.plot(
    newData["CLHCWC"][redData] * 1.8 / newData["Flow factor"][redData],
    newData["PLWCD_RWIO"][redData],
    linestyle="",
    marker="+",
    markersize=1,
    alpha=0.5,
)

plt.plot(
    newData["CVCWCC"][redData] - newData["PLWCD_RWIO"][redData],
    newData["CONCD_RWIO"][redData],
    linestyle="",
    marker="+",
    markersize=1,
    alpha=0.5,
)

plt.plot(
    newData["CLHCWC"][redData],
    newData["PLWCC"][redData],
    linestyle="",
    marker="o",
    markersize=1,
    alpha=0.5,
)


print(data.keys())
# redData = np.where(np.in1d(newData['FlightNum'],[2,5,8,9,10,14]))[0] #Relatively good data
sizeBoost = 0  # 10
plt.figure(figsize=(16, 9))
plt.plot(
    100 * (newData["CVCWCC"][redData] - newData["PLWCC"][redData]),
    newData["PLWCD_RWIO"][redData],
    linestyle="",
    marker="o",
    markersize=1,
    alpha=0.5,
)
# plt.plot([0,2],[0,2], lw=2)#,'r')
plt.xlabel(
    "CVI/CDP Difference (g/m^3)", fontsize=24 + sizeBoost, fontweight="bold"
)  # ,fs,30)
plt.ylabel("CDP Concentraiton  (#/cc)", fontsize=24 + sizeBoost, fontweight="bold")
plt.tick_params(axis="x", labelsize=20 + sizeBoost)
plt.tick_params(axis="y", labelsize=20 + sizeBoost)
# plt.ylim(0,150)
# plt.ylim(0)
# plt.xlim(0,2)
# plt.gca().legend(['CVCWCC','CLH2Corr','CLH2Orig'],fontsize=24+sizeBoost,markerscale=20,scatterpoints=1,loc="lower right")
plt.title("CLH2 vs CVI/King/CDP", fontsize=28 + sizeBoost, fontweight="bold")
plt.tight_layout()  #
# plt.savefig(basePath + 'PNG/CWCScatter_Skewed.png', dpi=200, bbox_inches='tight')
# plt.close
