from common.libraryImports import *
from common.spectralModule import *
from common.fileProcessing import *

# def h218oPars(pars):

# def hd16oPars(pars):


def loadFiles(baseFile, newer=False):
    if "TEMPSCAN" in baseFile:
        [HK, SC] = readTempScan(baseFile + ".csv")
        data = {**HK, **SC}
        return data

    filePath = baseFile  #'./Apr25FixWatIsoChge/CLIH-20180425_1957'
    files = [filePath + "_HK.csv", filePath + "_SC.csv"]

    SC = readSC(files[1], True)  # newer)
    HK = readHK(files[0], True)  # newer)
    HK = HK[0]
    SC = SC[0]

    HK["juldate"] = fixjuldate(HK["juldate"])
    SC["juldate"] = fixjuldate(SC["juldate"])

    # for i in range(SC['scans'].shape[0]):
    #    tmpmax = np.argmax(np.abs(SC['scans'][i,:]));

    if 1 == 1:  # try:
        [HK, SC], startText, endText = averageData(
            HK, SC, 1, int(1)
        )  # 5.0)#5.0)#5.0)#1.0/5.0)#30.0)#1.0/60.0)#0.01)#5.0)#10.0)
        # print("successful average")
        logging.debug("Successful average")
    # except:
    #    pass
    data = {**HK, **SC}
    return data


def readTempScan(file):
    # print("reading temp file")
    logging.debug("Reading temp file")
    fileRaw = []
    lineCnt = 0
    # data = pd.read_csv(file,header=None,skiprows=[0,1])
    with open(file) as f:
        buf = csv.reader(f)
        next(buf)
        next(buf)
        data = np.array(list(buf)).astype(np.float)

        # print(data[:,0])
        # 0 time, 1 milli, 2 scansavd

    HK = {
        "juldate": data[:, 0],
        "numAvg": data[:, 2],
        "tempSet": data[:, 3],
        "settleTime": data[:, 4],
        "lPstart": data[:, 5],
        "lPend": data[:, 6],
        "dataRate": data[:, 7],
        "dark": data[:, 8],
        "l1Temp": data[:, 9],
        "l2Temp": data[:, 10],
        "cellTemp": data[:, 11],
        "press": data[:, 12],
    }
    SC = {"juldate": data[0, :], "scans": data[:, 17:]}

    return (HK, SC)


wd = "C:/Users/rainw/Desktop/Hitran Plotting/"

# Hitran plotting and fitting process.
# Steps to operation

# Read in isotope data dictionary....

# data = loadFiles("../Data/Apr24Intercomp/CLIH-20180424_1956")  # Time 1951 also available
# normalData = loadFiles('./Apr25FixWatIsoChge/CLIH-20180425_1957')
# data = loadFiles('./May8/CLIH-20180508_2050')
# data = loadFiles('./May7QuickTest/CLIH-20180507_2315')

# data = loadFiles('./TEMPSCAN-20181229_211857')
# data = loadFiles('./TEMPSCAN-20181231_153415')


# data = loadFiles('./Apr25FixWatIsoChge/CLIH-20180425_1957')
# filePrefix = "../Data/Apr25FixWatIsoChge/CLIH-20180425_1957"

# Picarro pre-comparisons
# data = loadFiles("./03-20-19_PicarroPreComparison/CLIH-20190320_154240", True)

# Picarro real Intercomparisons 200 - 400 mbar
filePrefix = "../Data/03-21-19_PicarroComparison/CLIH-20190321_095900"
# 0.0026 is the offset for the entire file
# data["cellTemp"] = np.ones(len(data["press"])) * (22.3 + 3)
# data = laserFilter(data,True)
firstScan = 100
lastScan = 100000


# Secondary picarro 400 mbar comparisons
# filePrefix = "./config/03-21-19_PicarroComparison/CLIH-20190321_131551"
# data["cellTemp"] = np.ones(len(data["press"])) * (21.9 + 3)

# Tests involving fixed water measurements with varying isotope Ratios
# filePrefix = "../Data/03-29-19 Lab Tests/CLIH-20190329_120036"
# Values used for original isoshift tests
# firstScan = 2000  # 2500 * 2  # 50  # 2500*2#2700*2
# lastScan = 13000  # 3000 * 2  # 150000  # 6400*2 + 20#2200*2#4800*2

# Water vapor ramp at ~700 mbar with temp sensor
# filePrefix = "../Data/03-29-19 Lab Tests/CLIH-20190328_131940"

# Dual laser for comparison with individual lasers
# filePrefix = "../Data/03-28-19 Lab Tests/CLIH-20190328_160628"
# data = laserFilter(data, True)

# Single laser 1
# filePrefix = "../Data/03-28-19 Lab Tests/CLIH-20190328_160812"
# data = laserFilter(data, False, 1)

# Single Laser 2
# filePrefix = "./03-28-19 Lab Tests/CLIH-20190328_160947"
# data = laserFilter(data, False, 2)

# Wider wavelength test Laser 1 (20.6deg, 65mA -> 100 mA)
# filePrefix = "./03-28-19 Lab Tests/CLIH-20190328-161122"

# Wider wavelength test Laser 2 (20.4deg, 65mA -> 100 mA)
# filePrefix = "./03-28-19 Lab Tests/CLIH-20190328-161649"

# Wider wavelength test Dual Mode (above temps 65 mA -> 100 mA)
# filePrefix = "./03-28-19 Lab Tests/CLIH-20190328-161808"

# Even narrower laser 1 20.2deg (90mA -> 100 mA)
# filePrefix = "./03-28-19 Lab Tests/CLIH-20190328-162054"

# Even narrower laser 2 (90mA -> 100 mA)
# filePrefix = "./03-28-19 Lab Tests/CLIH-20190328-162318"

# Even narrower dual (90 mA -> 100mA)
# filePrefix = "./03-28-19 Lab Tests/CLIH-20190328-162736"


""" July 17th Tests
    have fixed water isotope shifts and D2O experiments"""
# ~9kppmv back and forth from file 20190717_141019
# filePrefix = "../Data/07-17-19_D2O_and_FixedWaterRatios/CLIH-20190717_141019"
# filePrefix = "../Data/07-17-19_D2O_and_FixedWaterRatios/CLIH-20190717_145342"
# filePrefix = "../Data/07-17-19_D2O_and_FixedWaterRatios/CLIH-20190717_150127"
# filePrefix = "../Data/07-17-19_D2O_and_FixedWaterRatios/CLIH-20190717_150250"
# filePrefix = "../Data/07-17-19_D2O_and_FixedWaterRatios/CLIH-20190717_151455"
# filePrefix = "../Data/07-17-19_D2O_and_FixedWaterRatios/CLIH-20190717_152414"
# filePrefix = "../Data/07-17-19_D2O_and_FixedWaterRatios/CLIH-20190717_152727"
# firstScan = 10
# lastScan = 100000

# data = loadFiles(filePrefix)


try:
    raise FileNotFoundError()
    with open(filePrefix + ".pickle", "rb") as handle:
        data = pickle.load(handle)
    # Store configuration file values
except FileNotFoundError:
    # Keep preset values
    data = loadFiles(filePrefix, True)
    data = laserFilter(data, True)  # False,1)
    data["cellTemp"] = np.ones(len(data["press"])) * (22.3 + 3)

dateString = dateFromFileName(filePrefix)
seconds = np.round(jd2secs(data["juldate"], dateString), 3)

data["juldate"] = seconds
"""
plt.plot(np.nanmean(data["scan1"][:, :], axis=0))
plt.plot(np.nanmean(data["scan2"][:, :], axis=0))
plt.show()
exit()
"""

# data = loadFiles(filePrefix, True)
# data = laserFilter(data, True)

# Tests showing backgrounds with fringes at varying pressures.
"""
Routine averages all of the backgrounds of a certain file and subtracts it off
of each spectra after being scaled to the current scan.
The backgrounds are then binned and plotted against pressure.

backgroundData = loadFiles("./03-28-19 Lab Tests/CLIH-20190328_121244", True)
backgroundData = laserFilter(backgroundData,'True')
with open('./18OBackground.csv','w',newline='') as file:
    #f = open(path_to_file, 'w', newline='')
    writer = csv.writer(file)
    for i in range(1,100):#len(data['scans'][4800*2:6400*2,0])):
        writer.writerow(np.r_[backgroundData['scans'][i,:]])

with open('./2HBackground.csv','w',newline='') as file:
    #f = open(path_to_file, 'w', newline='')
    writer = csv.writer(file)
    for i in range(1,100):#len(data['scans'][4800*2:6400*2,0])):
        writer.writerow(np.r_[backgroundData['scan2'][i,:]])
#    csv.writerow()
"""


"""
start = 100
xAxis = np.arange(len(backgroundData['scan1'][0,:]))[start:]
#backgroundData['press'] = np.round(backgroundData['press']/10)*10
fringeAverage = np.nanmean(backgroundData['scan1'][np.where(data['press']==250)[0],start:],axis=0)

linePars = Parameters()
linePars.add('back_c0',value = 0.0, vary = True)
linePars.add('back_c1',value = 1/max(xAxis), vary = True)
linePars.add('shift_c2',value = 0, vary = True)
linePars.add('amp',value = 0.1,vary = True)
linePars.add('freq',value = 0.1, vary = True)
linePars.add('phase',value = 0,vary = True)

lineOut =  minimize(laserBackground, linePars, args = (xAxis,),\
        	kws = {'data': fringeAverage}, \
        	scale_covar = True, method = 'leastsq')#,\

%matplotlib qt
yTuple = ()
colorTuple = ()
legendTuple = ()
alphaTuple = ()
#lt.plot([1,2],[1,2],'gray')
pressures = [300,250,300,350,400,450,500,550,600,650,700]
colors = ['black','violet','blue','green','yellow','orange','red','magenta','cyan','gray']
#colors = backgroundData['juldate']
labels = ["{:3d}".format(x) for x in pressures]
#alphas = [1.0 for x in pressures]
alphas = [1.0,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1]

minIndices = []
press = []

for j,color,legend,alpha in zip(pressures,colors,labels,alphas):
    for i, array in enumerate(backgroundData['scan1'][:,start:]):
        if i < 10 or i > 2000 != 0: continue
        #if backgroundData['press'][i] != j: continue
        if np.round(backgroundData['press'][i]/10)*10 != j: continue
        #fringe = (array/(fringeAverage*(np.mean(array)/np.mean(fringeAverage)))))[60:]
        #backFringe = array/laserBackground(lineOut.params,xAxis)
        #yTuple += (array,)
        #if i > 100: continue
        test = (smoothingFunction(array, 10, 5,'butter'))
        test = np.gradient(test)# - #/(1/500*xAxis)
        test -= np.mean(test)
        test /= np.linspace(1,4,len(xAxis))
        test /= np.abs(min(test))

        #print(np.argmin(test))
        minIndices.append(np.argmin(test))
        press.append(backgroundData['press'][i])
        #lineOut =  minimize(backgroundWithFringe, linePars, args = (xAxis,),\
        #	kws = {'data': test}, \
        #    scale_covar = True, method = 'leastsq')#,\
        #test = array/backgroundWithFringe(lineOut.params,xAxis)
        #yTuple += (array/backgroundWithFringe(lineOut.params,xAxis),)
        yTuple += (test,)
        colorTuple += (color,)
        legendTuple += (legend,)
        alphaTuple += (alpha,)
        #    data[key] = smoothingFunction(data[key], 400, 20,'butter')
            #data[key] = smoothingFunction(data[key], 3, 20)
        #print(fit_report(lineOut))

print(minIndices)
plt.figure()
plt.scatter(np.arange(len(minIndices)),minIndices, c = press)
plt.show()
    #plt.plot(backgroundData['press'][10:2000])
plot(xAxis,yTuple,colorTuple,legendTuple = legendTuple, alphaTuple = None, \
    labels = ["Fringe as a function of pressure", "Bit Number", "Arbitrary"])

    #displayLegend = False)# alphaTuple)#, plotStyle = 'colorScatter')

plt.plot(xAxis, np.gradient(backgroundData['scan1'][100,start:]),'b',\
    xAxis, np.gradient(smoothingFunction(backgroundData['scan1'][100,start:], 10, 5, 'butter')),'r')

histx = []
histy = []
for tuple in yTuple:
    histx.extend(xAxis)
    histy.extend(tuple)
plt.hexbin(histx,histy,cmap = 'magma')
plt.show()
plt.legend()

"""
"""
#File 1
#data = loadFiles("./03-21-19_PicarroComparison/CLIH-20190321_095900", True)

#File 2
#data = loadFiles("./03-21-19_PicarroComparison/CLIH-20190321_131551",True)


#data = loadFiles('./Apr25FixWatIsoChge/CLIH-20180425_1957')
#data['lNum'] = np.ones(len(data['press']))*1
#data['dark'] = np.ones(len(data['press']))*25


#data1372 = loadFiles("./Spectral Scans/TEMPSCAN-20190102_204950")

#Best temp scan at 1372
#data1372 = loadFiles("./Spectral Scans/TEMPSCAN-20190103_131230_l1_highq")

#data1372 = data
#data1389 = loadFiles("./Spectral Scans/TEMPSCAN-20190102_215937_l2_lowq")

#Best temp scan at 1389
#data1389 = loadFiles("./Spectral Scans/TEMPSCAN-20190103_135427_l2_highq")

#Picarro March 20th pre-comparison
#CLIH-20190320_144411_HK.csv
"""

"""
dataMix = loadFiles(wd + "/Spectral Scans/TEMPSCAN-20190103_145958_mix_lowq")
dataMix['scan1'] = dataMix['scans'][:,0:1024]
dataMix['scan2'] = dataMix['scans'][:,1024:]
for i in range(512):
    dataMix['scan1'][:,i] = np.mean(dataMix['scans'][:,i*2:(i+1)*2],axis=1)
    dataMix['scan2'][:,i] = np.mean(dataMix['scans'][:,i*2+1024:(i+1)*2+1024],axis=1)
dataMix['scan1'] = dataMix['scan1'][:,:512]
dataMix['scan2'] = dataMix['scan2'][:,:512]

#plt.plot(dataMix['scan1'][0,:])

#plt.plot(data1389['scans'][10,:])

dataMix['lNum'] = np.ones(len(dataMix['press']))*3
#data1372['lNum'] = np.ones(len(data1372['press']))
#data1389['lNum'] = np.ones(len(data1389['press']))*2
"""


"""

#First 18O Data
new18OData = loadFiles("./Stable Scans/CLIH-20190103_232446",True)
new18OData['lNum'] = np.ones(len(new18OData['press']))

#Better? 18O Data
new18OData = loadFiles("./Stable Scans/CLIH-20190104_005258",True)
new18OData['lNum'] = np.ones(len(new18OData['press']))

#First HDO Data
newHDOData = loadFiles("./Stable Scans/CLIH-20190103_195112",True)
newHDOData['lNum'] = np.ones(len(newHDOData['press']))*2

#Better HDO Data?
newHDOData = loadFiles("./Stable Scans/CLIH-20190104_001442",True)
newHDOData['lNum'] = np.ones(len(newHDOData['press']))*2
"""

# dataCombined = {}
# for key in data1372.keys():
#    dataCombined[key] = np.concatenate([data1372[key],data1389[key]])#,dataMix[key])
# dataCombined = data1372 + data1389#{**data1372, **data1389}
"""

plt.plot(dataCombined['lNum'])
data = loadFiles('./CLIH-20190102_0058',True)
#plt.plot(normalData['scans'][0,:])
#plt.plot(normalData['temp2'])

    HK = {'juldate':data[:,0],
        'numAvg':data[:,2],
        'tempSet':data[:,3],
        'settleTime':data[:,4],
        'lPstart':data[:,5],
        'lPend':data[:,6],
        'dataRate':data[:,7],
        'dark':data[:,8],
        'l1Temp':data[:,9],
        'l2Temp':data[:,10],
        'cellTemp':data[:,11],
        'press':data[:,12] }
    SC = {'juldate':data[0,:],
        'scans': data[:,17:]}
"""

# Read hitran identification information
molecularInfoDict = loadHitranKeys()


# fullLines = [10000000/1368, 10000000/1395]

# fullLines = [10000000/2647, 10000000/2651]

# hitranFullTable = readHitran(masterHitranKeys, fullLines, 5e10, 0.0)#, 0.0)
lines18O = [7286.050850, 7285.770300, 7285.667100]
hitran18OTable = readHitran(molecularInfoDict, lines18O, 5e3, 2e3)
lines2H = [7196.8, 7198.128]  # [7197.35, 7198.128]
hitran2HTable = readHitran(molecularInfoDict, lines2H, 1e4, 2e3)

try:
    data["scans"] = data["scan1"]
    # data['scans'] = data['scan2']
except:
    pass

scans = copy.deepcopy(data["scans"])

if data["lNum"][0] == 3:
    data["dark"][0] = 50  # 25

originalData = copy.deepcopy(data)

# powerDark = np.mean(scans[:,int(0.2*data['dark'][0]):int(0.8*data['dark'][0])],axis=1)
powerDark = np.mean(
    scans[:, int(0.7 * data["dark"][0]) : int(0.9 * data["dark"][0])], axis=0
)

scans = scans[:, int(data["dark"][0]) :]

powerDomain = np.linspace(40, 100, len(data["scans"][0, :]))

if data["lNum"][0] < 3:
    left = 10
    right = 10
else:
    left = 150
    right = 20

extras = [
    "Time",
    "NumAvg",
    "avgTime",
    "lCurve_l0",
    "lCurve_l1",
    "lCurve_l2",
    "O18Dark",
    "O18Ratio1pt",
    "O18Ratio11pt",
    "O18Ratio25pt",
    "floater",
]

pars = fitParsInit(
    3, 2, ["1_1", "1_2", "1_4"], extras
)  # , [backgroundPolyOrder], [uniqueIDs]
pars.add("amp", value=0.0025, vary=True)  # -0.01, vary = True)
# pars.add('amp2',value = 0.0, vary = True)
# pars.add('amp3',value = 0.0, vary = True)
# pars.add('freq',value = 5.0, vary = True)
pars.add("freq", value=0.5, vary=True)
# pars.add('freq2',value = 0.0, vary = True)
# pars.add('freq3',value = 0.0, vary = True)
pars.add("phase", value=0.0, vary=True)
# pars.add('phase2',value = 0.0, vary = True)
# pars.add('phase3',value = 0.0, vary = True)

pars.add("offset", value=0.0, vary=True)

pars["path"].set(value=7200)

dels = []
del18 = []
del2H = []

# PARAMETERS TO SMOOTH
smoothKeys = []  # "l1Temp", "l2Temp", "cellTemp", "press"]  # 'press','cellTemp']
# print(data["cellTemp"])
# exit()

for key in smoothKeys:
    #    # data, points, repeat
    # print(len(data[key]))
    data[key] = smoothingFunction(data[key], 100, 1, "butter")
    # data[key] = smoothingFunction(data[key], 3, 20)
    # data[key][0:20] = data[key][21]

# data['press'] = np.round(data['press']/10)*10

if data["lNum"][0] == 3:
    scanHop = 2
else:
    scanHop = 1

# seconds = (data["juldate"] - np.floor(data["juldate"][0])) * 3600.0 * 24.0

"""
with open('./18OScans15kppm.csv','w',newline='') as file:
    #f = open(path_to_file, 'w', newline='')
    writer = csv.writer(file)
    for i in range(4800*2,6400*2):#len(data['scans'][4800*2:6400*2,0])):
        writer.writerow(np.r_[data['scans'][i,:]])

with open('./2HScans15kppm.csv','w',newline='') as file:
    #f = open(path_to_file, 'w', newline='')
    writer = csv.writer(file)
    for i in range(4800*2,6400*2):#len(data['scans'][4800*2:6400*2,0])):
        writer.writerow(np.r_[data['scan2'][i,:]])
#    csv.writerow()
"""

"""


presWeird = []
tempWeird = []
presWeird = smoothingFunction(data['press'][4800*2:6400*2], 50, 1,'butter')
tempWeird = smoothingFunction(data['cellTemp'][4800*2:6400*2]+273.15 - 3.0, 50, 1, 'butter')


for i in range(4800*2,6400*2):
    try:
        presWeird.append((np.mean(data['press'][i:i+30])-1.0))
        tempWeird.append((np.mean(data['cellTemp'][i:i+30])+273.15 - 3.0))
    except: pass

onePoint = []
fivePoint = []
tenPoint = []
twentyPoint = []
backgroundPoint = []

for i,scan in enumerate(data['scans']):
    for j in range(scanHop):
        #16O is at 158.5
        #18O is at 239.75
        #dark at 340
        #Scan 2
        #D is at 219
        #16O at 316
        #16O at 366
        #dark at 250

        if j == 0:
            scan = data['scans'][i,int(data['dark'][0]):]
            index1 = 240; index2 = 158; indexDark = 340
        else:
            scan = data['scan2'][i,int(data['dark'][0]):]
            index1 = 316; index2 = 366; indexDark = 340
        if data['avgNum'][i] < 35: continue
        onePoint.append(scan[index2]/scan[index1])
        fivePoint.append(np.mean(scan[index2-2:index2+3])/np.mean(scan[index1-2:index1+3]))
        tenPoint.append(np.mean(scan[index2-5:index2+6])/np.mean(scan[index1-5:index1+6]))
        twentyPoint.append(np.mean(scan[index2-12:index2+13])/np.mean(scan[index1-12:index1+13]))
%matplotlib qt
plt.plot(onePoint[0::2])
plt.plot(fivePoint[0::2])
plt.plot(tenPoint[0::2])
plt.plot(twentyPoint[0::2])
plt.show()

plt.hist(data['avgNum'],bins = 200)

plt.plot(data['press'])
plt.plot(smoothingFunction(data['press'],15,1))
"""

# plt.plot(data['press'])
# plt.show()

runAvg = 0
avgThresh = 150  # 1000  # 2000

# Figure initialization
plt.figure(figsize=(12, 6))
plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)

"""
This loop organizes fit between two different fit types 18O and 2H.
indexer i denotes scan number, index j = 0 is 18O fit, j = 1 is 2H fit.
"""

powerZero = np.nanmean(data["scans"][:, 20:45])

powerZero = 0.0026

# print(powerZero)
logging.debug(powerZero)

for i, scan in enumerate(scans):
    # Set parameter time as julian seconds from start of day
    pars["Time"].set(value=data["juldate"][i])

    # Creates an adaptive running average to ensure adequate averaging
    runAvg = 1
    try:
        while np.sum(data["avgNum"][i : i + runAvg]) < avgThresh:  # 2000:
            dummy = data["juldate"][i + runAvg]
            runAvg += 1
    except:
        pass

    # print(runAvg)
    pars["avgTime"].set(value=data["juldate"][i + runAvg - 1] - data["juldate"][i])
    pars["NumAvg"].set(value=np.sum(data["avgNum"][i : i + runAvg]))

    for j in range(scanHop):
        # break
        # if i == 0: bax = brokenaxes(xlims=((1371,1373),(1388,1390)))
        # plt.plot(scan)
        if i == 0 and j == 0:
            initial = True
            dels = []

            laserCalTable = {}  # []
            header = []
            # extraHeader = ['lNum','l2Temp','lPstart','lPend','dark']
            # header.extend(extraHeader)
            # for key in pars.keys():
            #    header.append(key)#+'_i')
            for key in pars.keys():
                header.append(key + "_fit")

            for key in header:
                laserCalTable[key] = []

        try:
            lNum = data["lNum"][i]
        except:
            lNum = 1
        # if lNum == 1: continue
        try:
            if j == 0:
                scan = np.mean(
                    data["scans"][i : i + runAvg, int(data["dark"][0]) :], axis=0
                )
                powerDomain = np.linspace(
                    int(data["lPstart"][i]), int(data["lPend"][i]), len(scan)
                )
                zeroPower = np.mean(
                    data["scans"][
                        i, int(0.7 * data["dark"][0]) : int(0.9 * data["dark"][0])
                    ]
                )
            else:
                # scan = data['scan2'][i,int(data['dark'][0]):]
                scan = np.mean(
                    data["scan2"][i : i + runAvg, int(data["dark"][0]) :], axis=0
                )
                powerDomain = np.linspace(
                    int(data["lPstart"][i]), int(data["lPend"][i]), len(scan)
                )
                zeroPower = np.mean(
                    data["scan2"][
                        i, int(0.7 * data["dark"][0]) : int(0.9 * data["dark"][0])
                    ]
                )
            # scan = smoothingFunction(scan,80,1,'butter')
        except:
            scan = data["scans"][:, int(data["dark"][0])]
            powerDomain = np.linspace(
                40, 90, len(data["scans"][i, int(data["dark"][0]) :])
            )

        # Used to determine which scans to fit and how often
        if i % 1 != 0 or i < firstScan or i > lastScan:
            continue

        # scan -= zeroPower

        # Coefficients for lasers
        if lNum == 1 or (lNum == 3 and j == 0):
            a = -2.769337e-04
            b = 2.895673e-01
            c = -2.016873e00
            pars["lCurve_l0"].set(value=-2.016873e00, vary=False)
            pars["lCurve_l1"].set(value=2.895673e-01, vary=False)
            pars["lCurve_l2"].set(value=-2.769337e-04, vary=False)
        elif lNum == 2 or (lNum == 3 and j == 1):
            a = -4.403939e-04
            b = 3.177965e-01
            c = -1.830577e00
            pars["lCurve_l0"].set(value=-1.830577e00, vary=False)
            pars["lCurve_l1"].set(value=3.177965e-01, vary=False)
            pars["lCurve_l2"].set(value=-4.403939e-04, vary=False)

        powerCurve = a * np.power(powerDomain, 2) + b * powerDomain + c

        powerRange = max(powerDomain) - min(powerDomain)

        try:
            if data["press"][i] < 300:
                newpres = 250.0
            else:
                newpres = 400.0
            # pars['press'].set(value = newpres, vary = False)#data['press'][i], vary = False)#True)
            # pars['press'].set(value = np.round((np.mean(data['press'][i:i+30])-1.0)/5.0)*5.0, vary = False)#True)
            pars["press"].set(
                value=(np.mean(data["press"][i : i + runAvg])) - 1, vary=False
            )  # True)

            # pars['press'].set(value = 250.0, vary = False)#
            # pars['temp'].set(value=data['temp1'][i]+273.15, vary = False)
            pars["temp"].set(
                value=np.mean(data["cellTemp"][i : i + runAvg]) - 2.5, vary=False
            )  # True)
        except:
            pars["press"].set(value=data["press"][i] + 17.0, vary=False)
            # pars['temp'].set(value=data['temp1'][i]+273.15, vary = False)
            pars["temp"].set(value=data["temp1"][i], vary=False)  # True)# False)

        # pars["offset"].set(value=0.005, vary=False)  # zeroPower, vary = True)#False)

        pars["offset"].set(value=powerZero, vary=False)
        if lNum == 1 or (lNum == 3 and j == 0):
            refLaserWvlngth = 1372.82  # 1372.92#1372.82
            pars["back_c1"].set(
                value=0.1, vary=True
            )  # 105, vary = True)#12, vary = True) #Was .105
            pars["back_c0"].set(value=0.0, vary=False)  # 0.3,vary = True)
            try:
                wvlngthAt20mW = refLaserWvlngth - (25.0 - float(data["l1Temp"][i])) * 0.1
            except:
                wvlngthAt20mW = refLaserWvlngth - (25.0 - float(21.0)) * 0.1
            wvSlope = -0.011  # -0.011# -0.090
            wvIntercept = (
                10000000.0 / (wvlngthAt20mW - (20.0 - min(powerCurve)) * 0.0175) - 0.85
            )  # 19)#1719)
            # pars['shift_c0'].set(value = wvIntercept)
            # pars['shift_c1'].set(value = wvSlope)
            # pars['shift_c2'].set(value = -0.0021,vary = True)#False)#-0.0005)

            pars["shift_c0"].set(
                value=-0.513796 * data["l1Temp"][i] + 7297.876512, vary=True
            )  # False)
            pars["shift_c1"].set(
                value=-6.05402e-04 * data["l1Temp"][i] - 0.014, vary=True
            )
            pars["shift_c2"].set(
                value=-6.65082e-06 * data["l1Temp"][i] - 1.93116e-03, vary=True
            )

            pars["shift_c0"].set(
                value=-0.513796 * data["l1Temp"][i] + 7297.876512 + 0.18, vary=True
            )  # False)
            pars["shift_c1"].set(
                value=-6.05402e-04 * data["l1Temp"][i] - 0.014 - 0.010, vary=True
            )
            pars["shift_c2"].set(
                value=-6.65082e-06 * data["l1Temp"][i] - 1.93116e-03, vary=True
            )

            # Used for injection current based ajustment ot wavelength
            pars["shift_c0"].set(
                value=7286.986, vary=True, min=7286, max=7288
            )  # 7287.281022 + 0.2,vary=True)#False)
            pars["shift_c1"].set(value=-0.01288744, vary=True)  # -0.02585291,vary=True)
            pars["shift_c2"].set(value=-8.22012e-05, vary=True)  # 0.0,vary=True)

            # shift_c0:     7286.987 (fixed)
            # shift_c1:    -0.01288135 (fixed)
            # shift_c2:    -8.222605e-05 (fixed)

            # pars['shift_c3'].set(value = 0, vary = False)
            pars["back_c2"].set(vary=False)  # True)##
            hitran = hitran18OTable

            # pars['del2'].set(vary = True)
            # pars['del4'].set(vary = False)#True)

            pars["conc_1_1"].set(vary=True)
            pars["conc_1_2"].set(vary=True)
            pars["conc_1_4"].set(vary=False)  # True)  # =False)

            # pars['amp'].set(value = -0.001951682, vary = True)#False)
            # pars['freq'].set(value = 0.49154825, vary = True)#False)
            # pars['phase'].set(value = 0.76077161, vary = True)#False)

            # PARAMETERS FOR A INJECTION CURRENT DEPENDENT FRINGE
            # pars['amp'].set(value = -0.01156, vary = True)#False)
            # pars['freq'].set(value = 10*0.74232559, vary = True)
            # pars['phase'].set(value = 3.97800870, vary = True)#False)

            # PARAMETERS FOR A WAVELENGTH DEPENDENT FRINGE
            pars["amp"].set(value=-0.01156, vary=True)  # False)
            pars["freq"].set(value=10 * 0.74232559, vary=True)  # )#False)
            pars["phase"].set(value=3.97800870, vary=True)  # False)
            # amp:         -0.01115111 +/- 0.00116232 (10.42%) (init = -0.01072533)
            # freq:         7.52310259 +/- 0.03491175 (0.46%) (init = 7.586996)
            # phase:        734.139180

            # pars['voigt0_ppmv'].set(vary = True)

            # Bad temp overwrite
            # pars['temp'].set(value = 22.3 + 273.15, vary = False)#True)
            pars["press"].set(vary=False)  # True)  # False)
            pars["temp"].set(vary=False)  # True)

            # pars["offset"].set(value=0.005, vary=False)  # True)

            left = 75  # 100  # 15
            right = 10

            try:
                pars["shift_c0"].set(value=pars18["shift_c0"].value, vary=True)
                pars["shift_c1"].set(value=pars18["shift_c1"].value, vary=True)
                pars["shift_c2"].set(value=pars18["shift_c2"].value, vary=True)
                pars["amp"].set(value=pars18["amp"].value, vary=True)
                pars["freq"].set(value=pars18["freq"].value, vary=True)
                pars["phase"].set(value=pars18["phase"].value, vary=True)
                if (
                    i >= firstScan + 50 and pars18["conc_1_1"].value > 1000
                ):  # or out.params['voigt0_ppmv'].value < 1000:
                    pars["shift_c0"].set(vary=True)  # False)
                    pars["shift_c1"].set(vary=False)
                    pars["shift_c2"].set(vary=False)
                    pars["amp"].set(vary=False)  # True)
                    pars["freq"].set(vary=False)  # True)
                    pars["phase"].set(vary=False)  # True)
                if pars18["conc_1_1"].value < 1000:
                    pars["amp"].set(vary=True)
                    pars["freq"].set(vary=True)
                    pars["phase"].set(vary=True)
                # pars['shift_c3'].set(value = pars18['shift_c3'].value, vary = False)#True)
                pars["back_c1"].set(value=pars18["back_c1"].value)
                pars["conc_1_1"].set(value=pars18["conc_1_1"].value, vary=True)
                pars["conc_1_2"].set(value=pars18["conc_1_2"].value, vary=True)
                # pars["conc_1_4"].set(value=pars2H["conc_1_4"].value)
                frac = (pars18["conc_1_2"] / pars18["conc_1_1"] - 1.0) * 8.0
                pars["conc_1_4"].set(value=pars18["conc_1_1"].value * (1 + frac))
                pars["conc_1_4"].set(value=pars18["conc_1_1"].value)
                # pars["conc_1_4"].set(value=pars18["conc_1_2"].value)
            except:
                pass
            # pars['phase'].set(value = pars18O['phase'].value,vary=True)
            # pass
            # pars['shift_c0'].set(value = pars18['shift_c0'].value)

        elif lNum == 2 or (lNum == 3 and j == 1):
            continue
            # continue
            refLaserWvlngth = 1389.68
            # pars['back_c1'].set(value = 0.07,vary = True)#105, vary = True)#12, vary = True) #Was .105
            pars["back_c1"].set(
                value=0.13, vary=True
            )  # 105, vary = True)#12, vary = True) #Was .105
            # pars['back_c1'].set(value = l2Back[0], vary = True)
            # pars['back_c1'].set(value = 0.11,vary = True)#105, vary = True)#12, vary = True) #Was .105
            pars["back_c0"].set(value=0, vary=True)
            wvlngthAt20mW = refLaserWvlngth - (25.0 - float(data["l2Temp"][i])) * 0.1
            wvSlope = -0.015
            wvIntercept = (
                10000000.0 / (wvlngthAt20mW - (20.0 - min(powerDomain)) * 0.03) - 0.75
            )  # 19)#1719)
            # pars['shift_c0'].set(value = wvIntercept)
            # pars['shift_c1'].set(value = wvSlope)
            # pars['shift_c2'].set(value = -0.0024,vary = True)#False)#-0.0005)
            pars["shift_c0"].set(
                value=-0.514144 * data["l2Temp"][i] + 7209.892662, vary=True
            )  # False)
            pars["shift_c1"].set(value=-0.007, max=0, vary=True)
            pars["shift_c2"].set(value=-0.0027, vary=True)

            pars["shift_c0"].set(
                value=-0.514144 * data["l2Temp"][i] + 7209.892662 + 0.15, vary=True
            )  # False)
            pars["shift_c1"].set(value=-0.01, max=0, vary=True)
            pars["shift_c2"].set(value=-0.0027, vary=True)

            # Parameters for injection current dependent waveength
            pars["shift_c0"].set(
                value=7198.93, vary=True, min=7198, max=7200
            )  # 7199.0, vary = True)#-0.514144 * data['l2Temp'][i] + 7209.892662 + 0.15, vary = True)#7287.281022 + 0.2,vary=True)#False)
            pars["shift_c1"].set(
                value=-0.00698216, vary=True
            )  # -0.008, vary = True)#-0.02585291,vary=True)
            pars["shift_c2"].set(
                value=-1.3758e-4, vary=True
            )  # -1.22012e-04, vary = True)#0.0,vary=True)

            # pars['shift_c3'].set(value = 0.00, vary = False)# True)
            pars["back_c2"].set(vary=False)  # True)

            # pars['amp'].set(value = l2Back[1], vary = True)#False)# -0.00155, vary = False)#True)
            # pars['freq'].set(value = l2Back[2], vary = True)#False)#0.71787109, vary = False)
            # pars['phase'].set(value = l2Back[3], vary = True)#False)# -1.90279602, vary =  False)#True)

            # pars['amp'].set(value =  -0.00155, vary = True)
            # pars['freq'].set(value = 0.71787109, vary = True)# False)
            # pars['phase'].set(value = -1.90279602, vary =  True)

            pars["amp"].set(value=-0.01250609, vary=True)
            pars["freq"].set(value=10 * 0.78956509, vary=True)  # False)
            pars["phase"].set(value=1.61075935, vary=True)  # False)#True)

            # pars["offset"].set(vary=False)  # True)

            hitran = hitran2HTable

            # if j == 1:
            #    pars['voigt0_ppmv'].set(value = out.params['voigt0_ppmv'].value,vary = False)
            #    pars['temp'].set(vary = False)
            #    pars['press'].set(vary = False)

            left = 75  # 200  # *3#15
            right = 10  # 40  # *3

            pars["conc_1_2"].set(vary=False)  # True)
            pars["conc_1_4"].set(value=pars["conc_1_2"].value, vary=True)

            # Bad temp overwrite
            # pars['temp'].set(value = 22.3 + 273.15, vary = False)# True)

            try:
                pars["shift_c0"].set(value=pars2H["shift_c0"].value, vary=True)
                pars["shift_c1"].set(value=pars2H["shift_c1"].value, vary=True)
                pars["shift_c2"].set(value=pars2H["shift_c2"].value, vary=True)

                pars["amp"].set(value=out.params["amp"].value, vary=True)
                pars["freq"].set(value=out.params["freq"].value, vary=True)
                pars["phase"].set(value=out.params["phase"].value, vary=True)

                if i > firstScan + 50 or out.params["conc_1_1"].value < 2000:
                    pars["shift_c0"].set(vary=True)
                    pars["shift_c1"].set(vary=False)
                    pars["shift_c2"].set(vary=False)
                    pars["amp"].set(value=pars2H["amp"].value, vary=False)  # True)#False)
                    pars["freq"].set(value=pars2H["freq"].value, vary=False)
                    pars["phase"].set(value=pars2H["phase"].value, vary=False)  # True)

                # pars['shift_c3'].set(value = pars2H['shift_c3'].value)
                pars["back_c1"].set(value=pars2H["back_c1"].value)

            except:
                pass
            try:
                if scanHop == 2:
                    pars["conc_1_1"].set(value=pars18["conc_1_1"].value, vary=False)
                    pars["press"].set(value=pars18["press"].value, vary=False)
                    pars["temp"].set(value=pars18["temp"].value, vary=False)
                    pars["conc_1_2"].set(value=pars18["conc_1_2"].value, vary=False)
                else:
                    pars["conc_1_1"].set(value=pars2H["conc_1_1"].value, vary=True)
            except:  # ass
                # pars['voigt0_ppmv'].set(value = out.params['voigt0_ppmv'].value, vary = False)#True)#False)#pass
                pars["conc_1_1"].set(vary=False)  # True)  # True)#False)#pass

        # scan = scan - powerDark[i]#normalData['scans'][i,:]
        # print(len(scan))
        # smoothed = smoothingFunction(scan,300,50)
        smoothed = scan  # smoothingFunction(scan,200,50)
        meth = "leastsq"  # "trust-exact"  # "leastsq"  #

        if initial:
            initial = False
        #'jac' = '2-point'
        #'ftol' = 1e-7, 'xtol' = 1e-7, 'max_nfev' = 1000

        # From clh2processv2
        pars["shift_c3"].set(value=0, vary=False)
        out = minimize(
            spectralWrapper,
            pars,
            args=(powerCurve[left:-right][::1],),
            kws={
                "molecularInfoDict": molecularInfoDict,
                "data": scan[left:-right][::1],
                "hitran": hitran,
                "modelType": "wofz",
                "current": powerDomain[left:-right],
            },
            scale_covar=True,
            method=meth,  # "leastsq",
        )  # ,\

        # print((out.params["conc_1_2"] / out.params["conc_1_1"] - 1) * 1000)
        logging.debug((out.params["conc_1_2"] / out.params["conc_1_1"] - 1) * 1000)

        try:
            if j == 0:
                if out.params["conc_1_1"].value > 1000:
                    pars18 = copy.deepcopy(out.params)
                else:
                    pars18["conc_1_1"].set(value=out.params["conc_1_1"].value)
            else:
                if out.params["conc_1_1"].value > 2000:
                    pars2H = copy.deepcopy(out.params)
        except:
            if j == 0:
                pars18 = copy.deepcopy(out.params)
            else:
                pars2H = copy.deepcopy(out.params)

        if j == 0:
            # 16O is at 158.5
            # 18O is at 239.75
            # dark at 340
            # Scan 2
            # D is at 219
            # 16O at 316
            # 16O at 366
            # dark at 250
            # scan = data['scans'][i,int(data['dark'][0]):]
            index1 = 240
            index2 = 158
            indexDark = 340
            # onePoint.append(scan[index2]/scan[index1])
        else:
            index1 = 240
            index2 = 158
            indexDark = 340

        domain = domainShift(out.params, powerDomain)
        wvFringe = fringe(out.params, domain)
        test = 1 - scan / (laserBackground(out.params, powerCurve) * (1 + wvFringe))
        out.params["O18Dark"].set(value=test[indexDark])
        out.params["O18Ratio1pt"].set(value=test[index2] / test[index1])
        out.params["O18Ratio11pt"].set(
            value=(
                np.mean(test[index2 - 5 : index2 + 6])
                / np.mean(test[index1 - 5 : index1 + 6])
            )
        )
        out.params["O18Ratio25pt"].set(
            value=(
                np.mean(test[index2 - 12 : index2 + 13])
                / np.mean(test[index1 - 12 : index1 + 13])
            )
        )
        # twentyPoint.append(np.mean(scan[index2-12:index2+13])/np.mean(scan[index1-12:index1+13]))

        # out.params['18ORatio5pt'].set(value = data['scans'][i,int(data)]
        # pars.add('18ORatio11pt', value = 0.0, vary = False)

        # maxfev = 3000)
        # )#, tr_solver = 'exact', max_nfev = 1000)#max_nfev = 1000)# True)#, method = 'trust-constr')#'trust-exact')#, reduce_fcn = 'None')

        # print(fit_report(pars))
        # print(fit_report(out.params))
        logging.debug(fit_report(out.params))

        # print("Now printing index", i)
        logging.debug("Now printing index: " + str(i))

        # for key in pars.keys():
        # if 'back' in key or 'shift' in key or 'del' in key or 'ppmv' in key or 'press' in key:
        #    print('key (old, new): ', key, ', ', pars[key].value, ', ', out.params[key].value)

        # dels.append(out.params['del4'].value)

        if j == 0:
            del18.append(out.params["conc_1_2"].value)
        else:
            del2H.append(out.params["conc_1_4"].value)

        # plt.figure()

        tmp = np.linspace(3, 50, 10000)
        """
        #plt.plot(scan[left+100:right-120])
        plt.plot(10000000/domainShift(out.params, powerDomain[left:-right]),\
            1-(scan[left:-right]/(laserBackground(out.params, powerDomain[left:-right]) + \
            fringe(out.params,domainShift(out.params,powerDomain[left:-right])))),linewidth=3)#(np.power(powerDomain[left:-right],2)*out.params['backScale2'] + \
        plt.plot(10000000/domainShift(out.params,powerDomain),\
            1- spectrum(out.params, powerDomain,hitranTable,masterHitranKeys,raw=False)/ \
            (laserBackground(out.params,powerDomain) + fringe(out.params,domainShift(out.params,powerDomain))), \
            'black',linestyle = '--',linewidth=2)#\
        """
        """
        domain = domainShift(out.params, powerDomain[left:-right])
        wvFringe = fringe(out.params, domain)
        # domain = np.arange(len(scan))[left:-right]
        # domain = np.linspace(int(data['lPstart'][i]), \
        #    int(data['lPend'][i]),len(scan))
        # domain = 10000000.0/powerDomain[left:-right]
        # wvFringe = fringe(out.params, powerDomain)
        fitSpectrum = 1 - (
            spectralWrapper(
                out.params,
                powerCurve[left:-right],
                hitran,
                molecularInfoDict,
                raw=False,
                modelType="wofz",
                current=powerDomain[left:-right],
            )
            / (laserBackground(out.params, powerCurve[left:-right]) * (1 + wvFringe))
        )
        plt.plot(10000000.0 / domain, fitSpectrum, "black", linestyle="--", linewidth=2)

        # domain = domainShift(out.params, powerDomain[left:-right])
        # wvFringe = fringe(out.params, domain)
        # wvFringe = fringe(out.params, powerDomain[left:-right])

        rawSpectrum = 1 - (
            (
                scan[left:-right]
                / (laserBackground(out.params, powerCurve[left:-right]) * (1 + wvFringe))
            )
        )

        plt.plot(
            10000000.0 / domain, rawSpectrum, linewidth=3
        )  # (np.power(powerDomain[left:-right],2)*out.params['backScale2'] + \
        plt.plot(
            10000000 / domain,
            1
            - (
                scan[left:-right]
                / (laserBackground(out.params, powerDomain[left:-right]))
            ),
            linewidth=2,
            linestyle=":",
        )  # (np.power(powerDomain[left:-right],2)*out.params['backScale2'] + \

        plt.show()
        # exit()
        """
        """
        domain = domainShift(pars, powerDomain)
        plt.plot(10000000/domain,\
            1- spectrum(pars, powerDomain,hitranTable,masterHitranKeys,raw=False)/ \
            (laserBackground(pars,powerDomain) * (1 + fringe(pars,powerDomain))), \
            'black',linestyle = '--',linewidth=2)#\
        domain = domainShift(pars, powerDomain[left:-right])
        plt.plot(10000000/domain,\
            1-(scan[left:-right]/((laserBackground(pars, powerDomain[left:-right]))*\
            (1 + fringe(pars, powerDomain[left:-right])))),linewidth=3)#(np.power(powerDomain[left:-right],2)*out.params['backScale2'] + \
        """

        # Residual Plotting
        # plt.plot(10000000/domainShift(out.params,powerDomain[left+100:-right]),\
        #    1-(scan[left+100:-right]/laserBackground(out.params,powerDomain[left+100:-right])) - \
        #    (1- spectrum(out.params, powerDomain[left+100:-right],hitranTable,masterHitranKeys,raw=False)/laserBackground(out.params,powerDomain[left+100:-right])),\
        #    'black',linestyle = '--',linewidth=3)#\

        # plt.figure()
        """
        plt.plot(10000000/domainShift(pars,powerDomain[left+150:-right]),\
            1-(scan[left+150:-right]/laserBackground(pars,powerDomain[left+150:-right])),'r',linewidth=3)#(np.power(powerDomain[left:-right],2)*out.params['backScale2'] + \
        plt.plot(10000000/domainShift(pars,powerDomain),\
            1- spectrum(pars, powerDomain,hitranTable,masterHitranKeys,raw=False)/laserBackground(pars,powerDomain),\
            'black',linestyle = '--',linewidth=2)#\
        """

        for key in pars.keys():
            laserCalTable[key + "_fit"].append(out.params[key].value)
            # outArr.append(out.params[key].value)

winsound.Beep(1500, 4000)

# for i in range(0, 3):
#    winsound.Beep(2000, 100)
#    winsound.Beep(40,10)
#    for i in range(0, 3):
#        winsound.Beep(2000, 400)
#        winsound.Beep(40,10)
#        for i in range(0, 3):
#            winsound.Beep(2000, 100)
#            winsound.Beep(40, 10)

# plt.show()


# print(laserCalTable.keys())

for key in laserCalTable.keys():
    laserCalTable[key] = np.array(laserCalTable[key][1:])

# data = {**HK, **SC}
# Order of the {**data1,**data2} method important, data2 overwrites any duplicates in 1
with open(filePrefix + ".pickle", "wb") as handle:
    pickle.dump(
        {**originalData, **laserCalTable}, handle
    )  # , protocol=pickle.HIGHEST_PROTOCOL)


plt.plot(laserCalTable["Time_fit"], laserCalTable["conc_1_1_fit"])  # [::2])
plt.plot(laserCalTable["Time_fit"], laserCalTable["conc_1_2_fit"])
plt.plot(laserCalTable["Time_fit"], laserCalTable["conc_1_4_fit"])


plt.show()

# with open('filename.pickle', 'rb') as handle:
#    b = pickle.load(handle)


# plt.plot(del18)
# plt.show()

# plt.plot(del2H)
# plt.show()
