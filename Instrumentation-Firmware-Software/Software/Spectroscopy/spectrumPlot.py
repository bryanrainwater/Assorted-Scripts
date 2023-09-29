from common.libraryImports import *

# from fileProcessing import *
from common.spectralModule import *

# from hapi import *
wd = "C:/Users/rainw/Desktop/github/spectroscopy/"#SpectralProcessing/"
# wd = 'C:/Users/rainw/Desktop/SpectralPlot/'

'''
wvMin = 1368.58  # 1368.53#1368.0#1372.0
wvMax = 1368.60  # 1368.67#1369.0#1373.0
domain = np.linspace(10000000.0 / wvMin, 10000000.0 / wvMax, 1000)
masterHitranKeys = loadHitranKeys()
fullLines = [10000000 / (wvMin), 10000000 / (wvMax)]

domain = np.linspace(10000000.0 / 1368.2, 10000000.0 / 1369.0, 100000)
'''

wvMax = 10000000 / 7306.2  # .0#7312.0#7300.5#7310.0
wvMin = 10000000 / 7307.2  # 7309.0#7306.0#12.0#7297.5#7312.0

# wvMin = 10000000/7312
# wvMax = 10000000/7310
domain = np.linspace(10000000.0 / wvMin, 10000000.0 / wvMax, 1000)

molecularInfoDict = loadHitranKeys()
fullLines = [10000000 / (wvMin), 10000000 / (wvMax)]


# readHitran last two args are a rolloff filter outside of window
#   and a slope#
hitran = readHitran(
    molecularInfoDict, fullLines, 1, np.inf
)  # np.inf, np.inf)# 0.0)#, 0.0)

hitran = readHitran(molecularInfoDict, fullLines, 8e3, 1e4)

# print(list(hitran[:,4]))
# exit()
# hitran = hitran[2:4,:]

print(len(hitran))
# spectrum = singleSpectrum(domain, hitran[0,:], masterHitranKeys, p = 400, t = 300, q = 10000, path = 60, model = 'wofz')

pres = 700
temp = 313

"""

#Quick spectral fit (inputs: approximate range of fit in wavelength, peak wavelength, and data)
nmMin = 1368.0
nmMax = 1369.0
nmPeak = 1368.59

#linesSubset = [10000000/(wvMin), 10000000/(wvMax)]
#hitran = readHitran(masterHitranKeys, lineSubset, np.inf, np.inf)# 0.0)#, 0.0)

#dataread xlsx


pars = fitParsInit()

#wd = 'C:/Users/rainw/Desktop/Data/2019-June-5_CLH-2/'
dataFile = 'C:/Users/rainw/Desktop/Data/2019-June-5_CLH-2/CLH2-350mb_10200ppm.xlsx'
#dataFile = 'C:/Users/rainw/Desktop/Data/2019-June-5_CLH-2/CLH2-653mb_10500ppm.xlsx'
#dataFile = 'C:/Users/rainw/Desktop/Data/2019-June-5_CLH-2/CLH2-944mb_7500ppm.xlsx'
#dataFile = 'C:/Users/rainw/Desktop/Data/2019-June-5_CLH-2/CLH2-1050mbar_7500ppm_314K.xlsx'

#Pressure correction taking in June 2019 for CLH-2
p = (350 - 3)/1.075

pars['p'].set(value = p,vary = False)#True)#False)#944)#653, vary = False)#True)#944)#1050)
pars['q'].set(value = 10200,vary = True)#False)#True)#False)#7500, vary = True)#False)#min = 0, max = 1e6)
#Range is 7305.5 - 7308.... so shift_c0 =

#dataFile = wd + '/CLH-2-May-2019-test.xlsx'
df = pandas.read_excel(dataFile)
#print(df.dtypes.index)
powerCurve = np.array(df.values[:,0])
spectra1 = np.array(df.values[:,1])
spectra2 = np.array(df.values[:,2])

#print(powerCurve)
powerCurve = np.arange(len(spectra1))
#exit()


pars['shift_c0'].set(value = 7307.2789)
pars['shift_c1'].set(value = -.00185429*600.0/len(spectra1)) #Range of wavenumbers/range of bits
pars['back_c0'].set(value = spectra1[50]*1.2)#0.275)
pars['back_c1'].set(value = (max(spectra1)-spectra1[50])/len(spectra1))# -0.00859466)

pars['shift_c2'].set(vary = False)


#spectrumFitFeeder(pars, x, hitran, masterHitranKeys, raw = False, prefix = None, data = None, modelType = 'wofz',current=None):
#powerCurve = np.arange(len(spectra1))
scan = spectra1
left = 100#int(130*len(spectra1)/512)
right = 250#int(20*len(spectra1)/512)

print(pars)

#plt.plot(spectra2)
#plt.show()
#exit()

#print(spectra1)

out = minimize(spectrumFitFeeder, pars, args = (powerCurve[left:-right][::1],),\
	kws = {'masterHitranKeys':masterHitranKeys,'data':scan[left:-right][::1],\
    'hitran':hitran, 'QTDict': tipsQ(np.inf),'modelType': 'wofz'},
	scale_covar = True, method = 'leastsq')#,\

pars = out.params

fitSpectrum = 1 - (spectrumFitFeeder(pars, powerCurve[left:-right],\
    hitran,masterHitranKeys,raw=False,modelType='wofz')/\
    (laserBackground(pars,powerCurve[left:-right])))

rawSpectrum = 1 - ((scan[left:-right]/\
    (laserBackground(pars, powerCurve[left:-right]))))

#print(fitSpectrum)
plt.plot(10000000/domainShift(pars,powerCurve[left:-right]), fitSpectrum)# rawSpectrum)
plt.plot(10000000/domainShift(pars,powerCurve[left:-right]), rawSpectrum)
plt.show()

print(fit_report(pars))#pars))


#out = minimize(spectrumFitFeeder, pars, args = (powerCurve[left:-right][::1],),\
#	kws = {'masterHitranKeys':masterHitranKeys,'data':scan[left:-right][::1],\
#    'hitran':hitranTable, 'QTDict': tipsQ(np.inf),'modelType': 'wofz','current': powerDomain[left:-right]},
#	scale_covar = True, method = meth)#,\


#exit()

exit()
"""
# time1 = time.time()
# spectrum = multiSpectrum(domain, hitran, masterHitranKeys, p = 200, t = temp, q = 10000., path = 60, modelType = 'wofz')
# print(time.time() - time1)

# time1 = time.time()
# spectrum2 = multiSpectrum(domain, hitran, masterHitranKeys, p = pres, t = temp, q = 10000., path = 60, modelType = 'wofz')
# print(time.time() - time1)

time1 = time.time()
spectrumAlt = multiSpectrum(
    domain, hitran, molecularInfoDict, p=pres, t=temp, q=70000, path=60, modelType="wofz"#"rautian"
)
print(time.time() - time1)

hitran = readHitran(
    molecularInfoDict, fullLines, 1e8, 1e2
)  # np.inf, np.inf)# 0.0)#, 0.0)


time1 = time.time()
spectrumAlt = multiSpectrum(
    domain, hitran, molecularInfoDict, p=pres, t=temp, q=70000, path=60, modelType="wofz"#"rautian"
)
print(time.time() - time1)

hitran = readHitran(
    molecularInfoDict, fullLines, 7e3, 1e7
)  # np.inf, np.inf)# 0.0)#, 0.0)


pres = 300
time1 = time.time()
spec1 = transmissionSpectrum(
    domain, multiSpectrum(
    domain, hitran, molecularInfoDict, p=pres, t=temp, q=15000, path=30, modelType="wofz"
    ), p=pres, t=temp, q=15000, path=30
    )

spec1 += transmissionSpectrum(
    domain, multiSpectrum(
    domain, hitran, molecularInfoDict, p=pres, t=temp, q=25000, path=30, modelType="wofz"
    ), p=pres, t=temp, q=25000, path=30
    )
    
spec1 /= 2
    
plt.plot(domain, spec1 )

spec2 = transmissionSpectrum(
    domain, multiSpectrum(
    domain, hitran, molecularInfoDict, p=pres, t=temp, q=20000, path=30, modelType="wofz"
    ), p=pres, t=temp, q=20000, path=30
    )

plt.plot(domain, spec2 ,'red')

plt.figure()
plt.plot(spec1 - spec2)
plt.show()
exit()



spectrumApprox[:] = 0
for i in range(0,10):
    spectrumApprox += multiSpectrum(
    domain, hitran, molecularInfoDict, p=pres, t=temp, q=70000, path=60, modelType="hapi"
)


print(time.time() - time1)

plt.plot(domain, spectrumApprox)
#plt.plot(domain, spectrumAlt,'red')


# print(np.trapz(spectrum)/np.trapz(spectrum2))
plt.show()
exit()


###########ANIMATION ROUTINE#####################
# First set up the figure, the axis, and the plot element we want to animate
fig = plt.figure(figsize=(9, 6))
ax = plt.axes(xlim=(1368.5, 1368.7), ylim=(0, 100))
line, = ax.plot([], [], lw=2, color="black")
ax.ticklabel_format(useOffset=False)
ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%.2f"))
plt.xticks(rotation=20)
plt.xlabel("Wavelength", fontsize=20, fontweight="bold")  # ,fs,30)
plt.ylabel("Absorption", fontsize=20, fontweight="bold")
plt.tick_params(axis="x", labelsize=16)
plt.tick_params(axis="y", labelsize=16)

# fig.patch.set_alpha(0.)
# plt.set_xscale = 'log'
# plt.set_yscale = 'log'
# plt.scatter(0,0,color='blue'); plt.scatter(0,0,color='red'); plt.scatter(0,0,color='green'); plt.scatter(0,0,color='purple')
# legend_elements = [Line2D([0],[0],marker='o',label='CVI TDL (g/m^3)',markerfacecolor='b'),\
#    Line2D([0],[0],marker='o',label='King (g/m^3)',markerfacecolor='r'),\
#    Line2D([0],[0],marker='o',label='CDP (g/m^3)',markerfacecolor='g')]#,\
#    #Line2D([0],[0],marker='o',label='PIP (g/m^3)',markerfacecolor='purple')]
# plt.gca().legend(handles=legend_elements,loc='lower right',fontsize=24,markerscale=3)
plt.title("Spectral Lineshapes", fontsize=24, fontweight="bold")
plt.tight_layout()  #


temps = np.arange(270, 370, 10)
pressures = np.arange(100, 1100, 200)

# initialization function: plot the background of each frame
def init():
    line.set_data([], [])
    return (line,)


# animation function.  This is called sequentially
def animate(i):
    p = i * 15
    t = 273.15
    q = 10000
    if i > 50:
        p = 50 * 15
        t = 273.15 + (i - 51) * 2
    if i > 100:
        t = 372.15
        q = 10000 + (i - 101) * 1000
    # i is specified in Funcanimation by frames
    domain = np.linspace(10000000.0 / 1368.4, 10000000.0 / 1368.8, 10000)
    spectrumApprox = multiSpectrum(
        domain, hitran, masterHitranKeys, p=p, t=t, q=q, path=60, modelType="wofz"
    )
    spectrumApprox = 1 - transmissionSpectrum(
        domain, spectrumApprox, p=p, t=t, q=q, path=60
    )
    line.set_data(10000000 / domain, 100 * spectrumApprox)
    plt.title(
        "Press: "
        + "{:3d}".format(p)
        + "hPa, Temp: "
        + "{:3d}".format(int(t - 273.15))
        + "C, VMR: "
        + "{:.1f}".format(q / 10000)
        + "%",
        fontsize=24,
        fontweight="bold",
    )
    return (line,)


# call the animator.  blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(
    fig, animate, init_func=init, frames=182, interval=50, blit=False, repeat_delay=1000
)  # True)

# save the animation as an mp4.  This requires ffmpeg or mencoder to be
# installed.  The extra_args ensure that the x264 codec is used, so that
# the video can be embedded in html5.  You may need to adjust this for
# your system: for more information, see
# http://matplotlib.sourceforge.net/api/animation_api.html

anim.save('basic_animation.mp4', fps=10, extra_args=['-vcodec', 'libx264'], savefig_kwargs={'transparent': True, 'facecolor': 'none'})
# anim.save('basic_animation.mov', codec="png", dpi=100, bitrate=-1,savefig_kwargs={'transparent': True, 'facecolor': 'none'})
# anim.save('basic_animation.gif', writer = 'imagemagick', fps = 10)#, savefig_kwargs={'transparent': True, 'facecolor': 'none'})
# anim.save('../../files/animation.gif', writer='imagemagick', fps=60)
plt.show()


exit()


# NICE PLOT
print(hitran)
domain = np.linspace(10000000.0 / 1368.4, 10000000.0 / 1368.8, 10000)
plt.figure(figsize=(9, 6))
for temp, press in zip(temps, pressures):
    spectrumApprox = multiSpectrum(
        domain, hitran, masterHitranKeys, p=400, t=temp, q=6000, path=60, modelType="wofz"
    )
    spectrumApprox = 1 - transmissionSpectrum(
        domain, spectrumApprox, p=400, t=temp, q=6000, path=60
    )
    print(np.trapz(spectrumApprox))
    plt.plot(10000000.0 / domain, spectrumApprox, lw=3)  # color='black',
plt.xlabel("Wavelength", fontsize=24, fontweight="bold")  # ,fs,30)
plt.xlim(1368.5, 1368.7)
plt.ylabel("Amplitude", fontsize=24, fontweight="bold")
plt.tick_params(axis="x", labelsize=20)
plt.tick_params(axis="y", labelsize=20)
plt.set_xscale = "log"
plt.set_yscale = "log"
# plt.scatter(0,0,color='blue'); plt.scatter(0,0,color='red'); plt.scatter(0,0,color='green'); plt.scatter(0,0,color='purple')
# legend_elements = [Line2D([0],[0],marker='o',label='CVI TDL (g/m^3)',markerfacecolor='b'),\
#    Line2D([0],[0],marker='o',label='King (g/m^3)',markerfacecolor='r'),\
#    Line2D([0],[0],marker='o',label='CDP (g/m^3)',markerfacecolor='g')]#,\
#    #Line2D([0],[0],marker='o',label='PIP (g/m^3)',markerfacecolor='purple')]
# plt.gca().legend(handles=legend_elements,loc='lower right',fontsize=24,markerscale=3)
plt.title("Water Content Intercomparisons", fontsize=28, fontweight="bold")
plt.tight_layout()  #
#plt.show()
# plt.savefig(basePath + 'PNG/Poster/CDPCorr.png', dpi=600, bbox_inches='tight', transparent=True)
# plt.savefig(basePath + 'PNG/Poster/CDPCorr.eps', dpi=600, bbox_inches='tight', transparent=True)
#exit()


plt.plot(10000000.0 / domain, spectrum, "b")
plt.plot(10000000.0 / domain, spectrum2, "r")  # Alt, 'r')#,'alpha',0.5)
# plt.plot(10000000.0/domain, spectrumApprox, 'g')

# domain, spectrumHapi = multiSpectrum(domain, hitran, masterHitranKeys, p = pres, t = temp, q = 10000.0, path = 60, modelType = 'hapi')
# domain, spectrumHT = multiSpectrum(domain, hitran, masterHitranKeys, p = 400, t = 300, q = 10000.0, path = 60, modelType = 'hapi')

# plt.plot(10000000.0/domain, spectrumHapi, 'y')
# plt.plot(10000000.0/domain, spectrumHT-spectrumHapi)
plt.show()
