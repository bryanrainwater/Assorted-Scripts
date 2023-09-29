#Wisper analysis

import numpy as np
from matplotlib import pyplot as plt
import csv
import pickle
import pandas as pd

from scipy.signal import butter, filtfilt  # , savgol_filter
from scipy import signal

#from plotly import __version__
#from plotly.offline import download_plotlyjs, init_notebook_mode, plot,iplot
#print (__version__) # requires version >= 1.9.0
#Always run this the command before at the start of notebook
#init_notebook_mode(connected=True)
import plotly.graph_objs as go

def smoothingFunction(data, points=3, repeat=1, method="convolve"):
    # Butterworth filter works by knowing the point sampling rate and then
    #   knowing where the cutoff needs to be...i.eself.
    #   a sampling rate of ????
    cutoff = (points) / len(data)
    b, a = signal.butter(3, cutoff)  # 0.125)
    for i in range(repeat):
        if method == "butter":
            data = signal.filtfilt(b, a, data, padlen=int(len(data) / 2))  # 150)
        else:
            data = np.convolve(data, np.ones(points) / points, mode="same")
    return data


file = '.\WISPER_20200118_171552.csv'
file = '.\WISPER_20200225_201850.dat'
filelist = ['WISPER_20120101_000118.dat',
    'WISPER_20200112_171558.dat',
    'WISPER_20200118_171552.dat',
    'WISPER_20200125_173109.dat',
    'WISPER_20200205_174541.dat',
    'WISPER_20200207_132249.dat',
    'WISPER_20200213_055129.dat',
    'WISPER_20200218_170150.dat',
    'WISPER_20200220_191906.dat',
    'WISPER_20200224_173304.dat',
    'WISPER_20200225_201850.dat']

keys = ['pic0_qh2o_cal','pic0_deld_cal','pic0_delo_cal','pic1_qh2o_cal','pic1_deld_cal','pic1_delo_cal','air_pres','air_temp','cvi_enhancement','cvi_lwc','name'] 
#print(data[keys[0]])
copy = {}
flight = 4
data = pd.read_csv(filelist[flight])
data['name'][:] = flight+1
data['monotonic'] = np.linspace(flight+1, flight+2, len(data['name'][:]))
#data['monotonic'] = []
for i in range(6):
    tmp = pd.read_csv(filelist[flight+1+i])
    tmp['name'][:] = flight + i + 2
    tmp['monotonic'] = np.array(tmp['name'])
    tmp['monotonic'] = (np.linspace(flight+i+2,flight+i+3,len(tmp)))
    data = data.append(tmp, ignore_index = True)

    #data = data.append(pd.read_csv(filelist[6+i]), ignore_index = True)
   
for i in range(6):
    data[keys[i]] = np.array(data[keys[i]])
#data[keys[1]] = np.roll(data[keys[1]],-5) 
data[keys[1]] = np.roll(data[keys[1]],1) 

#data['monotonic'] = np.arange(len(data[keys[1]]))


data['air_temp'][np.where(data['air_temp'] < 0)[0]] = np.nan
data['cvi_enhancement'][np.where(data['cvi_enhancement']<0)[0]] = np.nan
data['air_pres'][np.where(data['air_pres'] < 0)[0]] = np.nan

#for i in range(3):
#    data[keys[i]] = smoothingFunction(data[keys[i]], points = 3, repeat = 1, method = 'convolve')


####### Vapor pressure calculation #############
E0 = 6.113#mb
b = 17.2694
T1 = 273.15
T2 = 35.86
e0 = E0*np.exp(b*(data['air_temp']-T1)/(data['air_temp']-T2))# and e = e0*exp(b(Td - T1)/(Td-T2))
r  = 0.622*e0/(data['air_pres']-e0) * 1000000.0
r = np.roll(r,253-102)

relHum = data[keys[3]] * (18.015/28.9645) / r

q = r/(r+1.0)

'''
plt.plot(r)#relHum)
#plt.show()
#exit()
plt.plot(data[keys[3]] * (18.015/28.9645))
plt.plot(data['air_pres']*10.0)
plt.plot(data[keys[5]]*-100)
plt.legend(['Saturation mixing ratio','GULPER ppmw','Air Pres * 10','del18'])
#plt.plot(r)
#plt.plot(data[keys[0]]* (18.015/28.9645))
#plt.show()
#exit()
'''
#data[keys[6]] *= -1/4


#exit()


##### Correct vapor phase isotopes according to general meteoric trend #########################










'''
##########CODE FOR FORMING EMPIRICAL NOISE ESTIMATES FOR PICARRO ###############
#Which precisional values are we going for..... Let's do 1000 - 20,000 in 1000 intervals.
plevels = np.arange(600,25000,200)#[14000]
#plevels = np.arange(0.2,1.6,0.2)
bestDel18P = []
bestDel2HP = []

#####Change useVap to 3 to repeat for vapor picarro
useVap = 3

for lev in plevels:
    copy = {}
    levExt = 100#0.1#12000#100
    try:
        for i in range(len(keys)-1,-1,-1):
            copy[keys[i]] = np.array(data[keys[i]][np.where((data[keys[0+useVap]] > lev - levExt)*(data[keys[0+useVap]] < lev+levExt))[0]])
            #copy[keys[i]] = np.array(data[keys[i]][np.where((data[keys[-2]] > lev - levExt)*(data[keys[-2]] < lev+levExt))[0]])
            #copy[keys[i]] = np.array(data[keys[i]][np.where((data[keys[0]] > 5900)*(data[keys[0]] < 6100))[0]])
            #data[keys[i]][data[keys[0]] < 2900.0] = np.nan
            #data[keys[i]][data[keys[0]] > 3100.0] = np.nan
        #for i in range(5,2,-1):    
        #    copy[keys[i]] = np.array(data[keys[i]][np.where((data[keys[3]] > lev - levExt)*(data[keys[3]] < lev+levExt))[0]])
        
        #plt.figure()
        del18 = copy[keys[2+useVap]] - (copy[keys[1+useVap]]-10)/8#)#)#, 's',markersize=1)#linewidth=1)
        del2H = copy[keys[1+useVap]] - (copy[keys[2+useVap]]*8 + 10)
    
        #del18 = copy[keys[5]] - (copy[keys[4]]-10)/8#)#)#, 's',markersize=1)#linewidth=1)
        #del2H = copy[keys[4]] - (copy[keys[5]]*8 + 10)
        #plt.plot(del18, 's',markersize=1)#linewidth=1)
        #plt.plot(del2H, 's',markersize=1)#linewidth=1)
        del18P = []
        del2HP = []
        stdLen = 50
        for i in range(len(del18)-stdLen):
            del18P.append(np.std(del18[i:i+stdLen]))
            del2HP.append(np.std(del2H[i:i+stdLen]))
        bestDel18P.append(min(del18P))
        bestDel2HP.append(min(del2HP))
        
        if lev == 5000:#lev:
            plt.figure()
            plt.plot([min(copy[keys[2+useVap]]),max(copy[keys[2+useVap]])], [min(copy[keys[2+useVap]])*8 + 10, max(copy[keys[2+useVap]])*8 + 10],'black',linewidth=3)
            plt.scatter(copy[keys[2+useVap]],copy[keys[1+useVap]],s=1,c=(copy[keys[0+useVap]]))#,vmin=0.2,vmax=0.6)#copy['name'])#copy[keys[0]])
            plt.colorbar(label = 'Testing')#'Flight Number')#'16O Mixing Ratio (ppmv)')
            plt.title('18O/2H Relationship around '+str(lev)+' ppmv')# 12,000 ppmv')
            plt.xlabel('del18O (permil)')
            plt.ylabel('del2H (permil)')
            #plt.show()
            #exit()
            
            #data = [go.Scatter(x=copy[keys[2]],y=copy[keys[1]])]
            #fig = go.Figure(data = data,layout = go.Layout(title='Offline Plotly Testing',width = 800,height = 500,
            #xaxis = dict(title = 'X-axis'), yaxis = dict(title = 'Y-axis')))
            #plot(fig,show_link = True)
            #fig.show()
            
            #N = 100000
            #r = np.random.uniform(0, 1, N)
            #theta = np.random.uniform(0, 2*np.pi, N)

            #fig = go.Figure(data=go.Scattergl(
            #    x = r * np.cos(theta), # non-uniform distribution
            #    y = r * np.sin(theta), # zoom to see more points at the center
            #    mode='markers',
            #    marker=dict(
            #        color=np.random.randn(N),
            #        colorscale='Viridis',
            #        line_width=1
            #    )
            #))

            #fig.show()
            #
        
    except:
        print('bing',lev)
        bestDel18P.append(np.nan)
        bestDel2HP.append(np.nan)
    
bestDel18P = np.array(bestDel18P)
bestDel2HP = np.array(bestDel2HP)
    
bestDel18P[bestDel18P <= 0.01] = np.nan
bestDel2HP[bestDel2HP <= 0.01] = np.nan    
#numpy.polyfit(numpy.log(x), y, 1)
#array([ 8.46295607,  6.61867463])

    
#curve_fit = np.polyfit(np.log(plevels), (bestDel18P), 1)
y = bestDel18P#curve_fit[0]* np.log(plevels) + curve_fit[1]
#curve_fit = np.polyfit(np.log(plevels), bestDel2HP, 1)
y2 = bestDel2HP#curve_fit[0]* np.log(plevels) + curve_fit[1]
  
#plt.figure()
#plt.plot(del18P,'s',markersize=1)
#plt.plot(del2HP,'s',markersize=1)
    
fig, ax1 = plt.subplots()

color = 'tab:red'
ax1.set_title('Picarro (Lantern) Precision Observed During IMPACTS')
ax1.set_xlabel('16O Volume Mixing Ratio (ppmv)')
ax1.set_ylabel('del18O 1-sigma Precision', color=color)
ax1.scatter(plevels, bestDel18P, color=color)
#ax1.plot(plevels, y, color = color)
ax1.tick_params(axis='y', labelcolor=color)
#plt.ylim(bottom=0)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel('del2H 1-sigma Precision', color=color)  # we already handled the x-label with ax1
ax2.scatter(plevels, bestDel2HP, color=color)
#ax2.plot(plevels,y2,color=color)
ax2.tick_params(axis='y', labelcolor=color)  
#plt.ylim(bottom=0)
plt.xlim(left=0,right=max(plevels))  
fig.tight_layout()
plt.show()
exit()   
    
    
    
#######################END BLOCK######################################################
'''
    

    
for i in range(2,-1,-1):
    data[keys[i]][data[keys[0]]< 500] = np.nan
    data[keys[i+3]][data[keys[3]] < 100] = np.nan
    #data[keys[i]] = data[keys[i]][(data[keys[3]] > 9000)*(data[keys[0]] < 11000)]


#plt.figure()
#plt.scatter(data[keys[1]],data[keys[2]],s=1,c=data['monotonic'])
#plt.show()
#exit()


    
for i in range(3,6):
    data[keys[i]] = np.roll(data[keys[i]],-43 - 368)
    #data[keys[1]] = smoothingFunction(data[keys[1]], points = 45, repeat = 1, method = 'convolve')
    #data[keys[2]] = smoothingFunction(data[keys[2]], points = 45, repeat = 1, method = 'convolve')
    #data[keys[5]] = smoothingFunction(data[keys[5]], points = 120, repeat = 1, method = 'convolve')
    
smoothMako18 = smoothingFunction(data[keys[2]], points = 120, repeat = 1, method = 'convolve')


#for i in range(6):
#    data[keys[i]] = data[keys[i]][~np.isnan(data[keys[i]])]


######################### RECONSTRUCTION OF TOTAL WATER CONTENT ##################################
######################### AND TOTAL ENHANCED WATER CONTENT      ##################################

data['totalWater'] = data[keys[0]] + data[keys[3]]

##### FOR reproducing total isotope ratios, calculate water fraction:
vaporFraction = data[keys[0]]/(data[keys[3]]+data[keys[0]])
##### THEN take vapor 
data['totald18'] = (1.0-vaporFraction) * data[keys[2]] + (vaporFraction)*data[keys[5]]
data['totald2H'] = (1.0-vaporFraction) * data[keys[1]] + (vaporFraction)*data[keys[5]]

data['enhTotalWater'] = data[keys[3]] + data[keys[0]]*data['cvi_enhancement']
enhVaporFraction = data[keys[0]]*data['cvi_enhancement']/(data[keys[3]]+data[keys[0]]*data['cvi_enhancement'])
data['enhtotald18'] = (1.0-enhVaporFraction) * data[keys[2]] + (enhVaporFraction)*data[keys[5]]
data['enhtotald2H'] = (1.0-enhVaporFraction) * data[keys[1]] + (enhVaporFraction)*data[keys[5]]

#plt.scatter(data['totalWater'], data['totald18'],s=1)
#plt.show()
#exit()





################### RAYLEIGH DISTILLATION ROUTINES ###########################

# Approach: Use delta18 vs water mising ratio









##############################################################################










###################ATTEMPT TO USE DEXCESS DERIVATIVES TO#########################
###################IDENTIFY EVAP/PRECIP OVER ENTRAINMENT#########################

dexcess1 = data[keys[1]] - data[keys[2]]*8.0
dexcess2 = data[keys[4]] - data[keys[5]]*8.0

dexcess1[dexcess1 > 100000] = np.nan

#plt.plot(dexcess1)
smoothedExcess = (smoothingFunction(dexcess1,points = 10, repeat = 5, method = 'convolve'))
#plt.plot(smoothedExcess)

#print(smoothedExcess)
diff = np.diff((smoothedExcess))


#plt.figure()
#plt.plot(diff)
#plt.plot(smoothingFunction(diff, points = 60, repeat = 5, method = 'convolve'))
#plt.show()
#exit()



'''
plt.figure()
plt.scatter(data[keys[2]],data[keys[1]],s = 2, c = data['monotonic'])#,vmin=0.5, vmax=1.5)#,cmap = 'magma')#data['monotonic'])#data[keys[0]],vmax = 10000)
plt.plot([-100,0],[-810,10],'b',linewidth=5)
plt.ylim(bottom=-375,top=10)
plt.xlim(left=-47,right=1)
plt.title('Condensed Meteoric Water Line')
plt.ylabel('del2H (permil)')
plt.xlabel('del18 (permil)')
plt.colorbar(label = 'q (ppmv)')
plt.tight_layout()
plt.savefig('figure1.png')
#plt.show()


plt.figure()
plt.scatter(data[keys[2]],data[keys[1]],s = 2, c = data[keys[5]]/data[keys[2]], vmin = 0.75, vmax = 2)
plt.plot([-100,0],[-810,10],'b',linewidth=5)
#,c=(dexcess2 - dexcess1),s=1,vmax = 500, vmin = 0)#data[keys[0]],s=1)#,vmax = 30000)
plt.ylim(bottom=-375,top=10)
plt.xlim(left=-47,right=1)
plt.title('Condensed Meteoric Water Line')
plt.ylabel('del2H (permil)')
plt.xlabel('del18 (permil)')
plt.colorbar(label = 'Ratio of Ambient/Condensed del18')
plt.tight_layout()
plt.savefig('figure2.png')
#plt.show()

diff18 = smoothMako18 - data[keys[5]]
'''
plt.figure()
#plt.scatter(data[keys[0]],data[keys[2]],s = 2, c = data[keys[6]])#, vmin = 0.75, vmax = 2)
#plt.scatter(vaporFraction,data[keys[2]],s = 1, c = data['air_pres'])#, vmin = 0.75, vmax = 2)
#plt.scatter(((data[keys[0]]+data[keys[3]])*18.015/28.9645*1.0/1000.0),data[keys[5]],s = 1, c = diff18)#pres'])#data['monotonic'])#, vmin = 0.75, vmax = 2)
tmp = ((data[keys[0]])*18.015/28.9645*1.0/1000000.0)
tmp = tmp/(1.0+tmp)
tmp *= 1000
plt.scatter(tmp,data[keys[2]],s = 1, c = data['name'])#c=data['monotonic'])#c = relHum,vmin=0.5,vmax=1.5)#data['monotonic'])#pres'])#data['monotonic'])#, vmin = 0.75, vmax = 2)
#plt.scatter(data['air_pres'],data[keys[5]],s = 1, c = data['air_pres'])#data['monotonic'])#, vmin = 0.75, vmax = 2)
#plt.scatter(vaporFraction,data[keys[2]],s = 1, c = (data[keys[3]]*18.015/28.9645)/r, vmin = 0.5, vmax = 2)
#plt.plot([-100,0],[-810,10],'b',linewidth=5)
#,c=(dexcess2 - dexcess1),s=1,vmax = 500, vmin = 0)#data[keys[0]],s=1)#,vmax = 30000)
#plt.xlim(left=-375,right=10)
plt.ylim(bottom=-47,top=1)
plt.title('Rayleigh Relationship')
plt.xlabel('del2H (permil)')
plt.ylabel('del18 (permil)')
plt.colorbar(label = 'Ratio of Ambient/Condensed del18')
plt.tight_layout()
plt.savefig('figure3.png')
#plt.show()

#plt.figure()
#plt.plot(smoothedExcess)


tmp = ((data[keys[0]])*18.015/28.9645*1.0/1000000.0)
tmp = tmp/(1.0+tmp)
tmp *= 1000

plt.figure()
#redRange = (data['monotonic'] <= 11)*(data['monotonic'] >= *3+j+flightOffset)
redRange = (data['name'] == 11)
plt.scatter(tmp[redRange],data[keys[2]][redRange],s = 1, c = data['air_pres'][redRange],vmin=650,vmax=850)# np.linspace(0,1,len(data['name'][redRange])),vmin=0.5,vmax=0.9)#c=data['monotonic'])#c = 


#plt.figure()
#plt.scatter(tmp[redRange],data[keys[2]][redRange],s = 5, c = smoothedExcess[redRange],vmin=8,vmax=15)
plt.ylim(bottom=-47,top=1)
#plt.title('Rayleigh Relationship')
plt.xlabel('q (g/kg)')
plt.ylabel('del18 (permil)')
plt.colorbar(label = 'Air Pressure')

plt.figure()
plt.plot(data['air_pres'][redRange])


'''
####MULTIPANEL FIG#######
#plt.figure()
fig, ax = plt.subplots(2, 3, sharex='col', sharey='row')
flightOffset = 6
for i in range(2):
    for j in range(3):
        redRange = (data['monotonic'] <= i*3+j+flightOffset+1)*(data['monotonic'] >= i*3+j+flightOffset)
        ax[i, j].scatter(tmp[redRange],data[keys[2]][redRange],s = 1, c = np.linspace(0,1,len(data['name'][redRange])))#c=data['monotonic'])#c = 
        ax[i, j].set_ylim(bottom=-47,top=1)
        ax[i, j].set_xlim(left=0,right=10)
        ax[i, j].set_title('Flight Number: '+str(i*3+j+flightOffset))
        #ax[i, j].set_xlabel('q (g/kg)')
        #ax[i, j].set_ylabel('del18 (permil)')
        if i == 0:
            ax[i,j].set_xlabel('q (g/kg)')
        if j == 0:
            ax[i,j].set_ylabel('del18 (permil)')
        #plt.ylim(bottom=-47,top=1)
        #plt.xlim(left=0,right=10)
        #plt.title('Flight Number: '+str(i))
        #plt.title('Rayleigh Relationship')
        #plt.xlabel('q (g/kg)')
        #plt.ylabel('del18 (permil)')
        
        
'''        
        
'''
for i in range(5, 11):
    redRange = (data['monotonic'] <= i+1)*(data['monotonic'] >= i)
    print(redRange)
    plt.subplot(2, 3, i-4)
    plt.scatter(tmp[redRange],data[keys[2]][redRange],s = 1, c = np.linspace(0,1,len(data['name'][redRange])))#c=data['monotonic'])#c = 
    plt.ylim(bottom=-47,top=1)
    plt.xlim(left=0,right=10)
    plt.title('Flight Number: '+str(i))
    #plt.title('Rayleigh Relationship')
    plt.xlabel('q (g/kg)')
    plt.ylabel('del18 (permil)')
    #plt.text(0.5, 0.5, str((2, 3, i)),
    #         fontsize=18, ha='center')
'''




'''
plt.figure()
plt.scatter(data[keys[5]],data[keys[4]],c=(data[keys[3]]),s=2, vmax = 10000)
plt.plot([-100,0],[-810,10],'b',linewidth=5)
plt.ylim(bottom=-375,top=10)
plt.xlim(left=-47,right=1)
plt.title('Vapor Meteoric Water Line')
#plt.xlim(left=-500,right=0)
#plt.ylim(bottom=-100,top=-60)
plt.colorbar()

plt.figure()
#plt.plot(data[keys[5]]/data[keys[2]])
plt.plot(data[keys[1]])
plt.plot(data[keys[2]]*8 + 10)
plt.plot(data[keys[6]])
plt.ylim(top=0,bottom = -400)
#plt.plot(dexcess1 - dexcess2)
#plt.plot(dexcess2)
#plt.xlim(left=-500,right=0)
#plt.ylim(bottom=-100,top=-60)
#plt.colorbar()
'''
plt.show()