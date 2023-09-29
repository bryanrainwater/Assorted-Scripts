from common.libraryImports import *
from common.customPlot import *


# Picarro real Intercomparisons 200 - 400 mbar
filePrefix = "../Data/03-21-19_PicarroComparison/CLIH-20190321_095900"
#filePrefix = "../Data/03-21-19_PicarroComparison/CLIH-20190321_095900_wHDO"
# data['cellTemp'] = np.ones(len(data['press']))*(22.3+3)
# data = laserFilter(data,True)

# filePrefix = "./03-29-19 Lab Tests/CLIH-20190329_120036"

# Tests involving fixed water measurements with varying isotope Ratios
#filePrefix = "../Data/03-29-19 Lab Tests/CLIH-20190329_120036"
#filePrefix = "../Data/03-29-19 Lab Tests/CLIH-20190329_120036_good_linear_withoffset_allfloating"
filePrefix = "../Data/03-29-19 Lab Tests/CLIH-20190329_120036_fixedOffset_restFloating"
#filePrefix = "../Data/03-29-19 Lab Tests/CLIH-20190329_120036_good_least_squares_woffset_allfloating"
#filePrefix = "../Data/03-29-19 Lab Tests/CLIH-20190329_120036_powerzero_700scanavg"
#filePrefix = "../Data/03-29-19 Lab Tests/CLIH-20190329_120036+bacup"
#filePrefix = "../Data/03-29-19 Lab Tests/CLIH-20190329_120036_fixedOffset_restFloating"#
#filePrefix = "../Data/03-29-19 Lab Tests/CLIH-20190329_120036_fixedOffset_bothLasers_restFloating"

# Renewed tests with fixed 16O and variable 18ORatio5pt
#filePrefix = "../Data/07-17-19_D2O_and_FixedWaterRatios/CLIH-20190717_141019"


with open(filePrefix + ".pickle", "rb") as handle:
    data = pickle.load(handle)

print(data.keys())


###### SOrting information for ramps ######
'''
up to index 4000 is 250 mbar, past that is 400 mbar
700 - 850 is 840 ppmv
920 - 1020 is 1360 ppmv
1150 - 1350 is 1780 ppmv (with slight drift)
1480 - 1600 is 2540 ppmv
1725 - 1800 is 4920 ppmv
1850 - 2100 is 9500 ppmv
2160 - 2325 is 15600 ppmv
2380 - 2500 is 20750 ppmv
2700 - 2875 is 30300 ppmv
4500 - 4600 is 880 ppmv
4700 - 4950 is 1275 ppmv
5100 - 5250 is 2280 ppmv (slight drift)
5350 - 5475 is 3775 ppmv
5600 - 5700 is 8600 ppmv
5850 - 5950 is 13200 ppmv
6000 - 6150 is 19000 ppmv
6200 - 6350 is 20000 ppmv
6650 - 6728 is ~30000 ppmv
'''

if filePrefix =="../Data/03-21-19_PicarroComparison/CLIH-20190321_095900":

    starts = [700,920,1150,1480,1725,1850,2160,2380,2700,4500,4700,5100,5350,5600,5850,6000,6200,6650]
    ends = [850,1020,1350,1600,1800,2100,2325,2500,2875,4600,4950,5250,5475,5700,5950,6150,6350,6728]
    pres = np.array([250]*18)

    pres[9:] = 400
    steps = len(starts)

    O16 = np.array([0.0]*steps)
    O16prec = np.array([0.0]*steps)
    del18= np.array([0.0]*steps)
    del18prec = np.array([0.0]*steps)

    for i in range(len(starts)):
        O16[i] = np.nanmean(data['conc_1_1_fit'][starts[i]:ends[i]])
        O16prec[i] = np.std(data['conc_1_1_fit'][starts[i]:ends[i]])
        tmp = (data["conc_1_2_fit"][starts[i]:ends[i]] / data["conc_1_1_fit"][starts[i]:ends[i]] * 1000) - 1000
        del18[i] = np.nanmean(tmp)
        del18prec[i] = np.std(tmp)
    # plt.plot(data['O18Ratio5pt'])
    #print(len(data["Time_fit"]), len(data["O18Ratio11pt_fit"]))
    # plot(data['Time'],data['del2'],labels = ['O18','Time (s)','Arbitrary'])

    plt.figure(figsize=(9, 4))
    plt.scatter(O16,del18prec, c = pres)
    #plt.show()
    
    plt.xlabel("VMR (ppmv)", fontsize=18, fontweight="bold")  # ,fs,30)
    plt.ylabel("del18O (permil)", fontsize=18, fontweight="bold")
    plt.tick_params(axis="x", labelsize=16)
    plt.tick_params(axis="y", labelsize=16)
    plt.ylim(0,4)
    # plt.xlim(30,80000)
    #lgnd = plt.gca().legend(['Pressure [mbar]'],fontsize=20,markerscale=5,scatterpoints=1,loc="lower right")
    plt.title("del18O Precision vs VMR", fontsize=22, fontweight="bold")
    plt.colorbar(label="Pressure")#,size=18)
    plt.tight_layout()  #
    plt.savefig("./testy1.png", dpi=200, bbox_inches="tight", transparent=True
    )



plt.plot(data["press"])
plt.plot(data["press_fit"])
plt.show()

#ydat = (data["conc_1_2_fit"] / data["conc_1_1_fit"] * 1000) - 1000
ydat = (data["conc_1_2_fit"] / data["conc_1_1_fit"] * 1000) - 1000

#np.savetxt('testout.csv', np.c_[data["Time_fit"],data["conc_1_1_fit"],ydat], delimiter=',')
#ydat = data["conc_1_1_fit"]
# ydat = data["shift_c0_fit"]
#plot(data["Time_fit"], ydat, labels=["H2O", "Time (s)", "ppmv"])
#plot(np.arange(len(ydat)),data['conc_1_1_fit'], labels=["H2O", "Time (s)", "ppmv"])
#plot(np.arange(len(ydat)),data['press_fit'],labels = ["Pressure","time","mbar"])
# plot(data["Time_fit"], data["offset_fit"])  # , labels=["Offset"])



# plt.show()
