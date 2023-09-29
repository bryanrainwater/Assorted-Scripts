#Reading .wav files for pp2f sampling from audio interface

#For importing the audio files
from scipy.io import wavfile

#For plotting
from matplotlib import pyplot as plt
import numpy as np

#For butterworth bandpass and lowpass filtering for 1f and 2f analysis
from scipy import signal
from scipy.signal import argrelextrema
from scipy import integrate, interpolate

from lmfit import fit_report, Parameters, minimize

from statsmodels.graphics.tsaplots import plot_acf

'''
from scipy import optimize
def sinusoid(x, a, b, c, d):
    return a*np.sin(b*x + c) + d
params, params_covariance = optimize.curve_fit(sinusoid, x, wave,
                                               p0=[0.1,1/3,np.pi,0])
print(params)
'''

def sinusoid(pars, x, data = None, abs = True):
    #pars = pars.valuesdict();
    if abs:
        model = np.abs(pars['amp']*np.sin(pars['freq']* (x) - pars['phase']))# + pars['offset']#+ \
        #data = np.abs(data)
    else:
        model = (pars['amp']*np.sin(pars['freq'] * (x) - pars['phase']))# + pars['offset']#+ \

    if data is None:    return model
    return (model - data)

def smoothingFunction(data, points = 3, repeat = 1,method = 'convolve'):
    #Butterworth filter works by knowing the point sampling rate and then
    #   knowing where the cutoff needs to be...i.eself.
    #   a sampling rate of ????
    cutoff = (points)/len(data)
    b, a = signal.butter(3, cutoff)# 0.125)
    for i in range(repeat):
        if method == 'butter': data = signal.filtfilt(b, a, data, padlen=int(len(data)/2))#150)
        else: data = np.convolve(data, np.ones((points,))/points, mode='same')
    return data
    #if key == 'RICE':



fs, wave = wavfile.read('./hdowave.wav')#./Audio Track.wav')
fs, output = wavfile.read('./hdooutput.wav')

fs, wave = wavfile.read('./hdowmshighmodulationfixed.wav')

fs, wave = wavfile.read('./daq1110_wms_hdo.wav')

fs, wave = wavfile.read('./dwms_160khz_2048_21p6C_10mAmod.wav')
fs = 160000
wave = wave[2180:]

packetLen = 2048

wavelen = len(wave)
wavelen = int(np.floor(wavelen/packetLen))
wave = wave[:wavelen*packetLen]
newWave = np.zeros(packetLen,dtype = 'float')

#domain = np.arange(len(wave))
#interpFunc = interpolate.interp1d(domain,wave,kind='cubic')
#xnew = np.arange(0,2048*2,0.01)
#ynew = interpFunc(xnew[:2048*2*100])

#plt.plot(xnew[:2048*2*100],ynew[:2048*2*100])
#plt.show()
#exit()


for i in range(packetLen):
    newWave[i] = np.mean(wave[i::packetLen])

plt.plot(wave)
plt.show()
exit()

#plt.plot(wave)

dark = 10
dark = (packetLen*(10/100))
dark = int(np.floor(dark/(2))*2*1)
validSpan = int(packetLen - dark)
wmsCycles = 100
synthWave = np.arange(validSpan)
synthWave = np.sin(synthWave*2*np.pi/(validSpan/wmsCycles))
synthWave = np.r_[np.zeros(dark),synthWave]
#plt.show()

#f, Pxx_den = signal.welch((synthWave*wave[:packetLen])[200:], fs, nperseg=2048)
#plt.semilogy(f, Pxx_den)
#plt.show()
#exit()



predata = synthWave*wave[:packetLen]
predata = predata[200:]
lpfreq = 60
b, a = signal.butter(1, lpfreq, 'low', fs = fs)
data = signal.filtfilt(b, a, predata, padlen=1000)#int(len(data)/2))#150)
#plt.plot(wave)
#plt.plot(sinusoid(out.params,x)[::4])

#plt.plot((wave[:]))
#plt.plot(output)
plt.plot(data)
plt.show()
exit()


#plt.plot(wave[:packetLen]*synthWave)
#plt.show()
#exit()

#f, Pxx_den = signal.welch(wave, fs, nperseg=2048)
#plt.semilogy(f, Pxx_den)
#plt.show()
#exit()

#sys.exit()




#output = wave[300:,0]
#wave = wave[300:,1]

fs = 80000

#test = (1-2*wave*wave)
#test -= np.mean(test)
#test *= output
test = wave#smoothingFunction(wave,2,10)


#lpfreq = 3
#b, a = signal.butter(3, [5800,6300], 'bandpass', fs = fs)
#wave = signal.filtfilt(b, a, wave, padlen=1000)#int(len(data)/2))#150)

test = wave*wave
test -= np.mean(test)

f, Pxx_den = signal.welch(test*output, fs, nperseg=10000)
peakFreq = np.argmax(Pxx_den)
#plt.semilogy(f, Pxx_den)
#plt.ylim([0.5e-5, 1])
#plt.show()
#print(f[peakFreq])
peakFreq = f[peakFreq]
#exit()

#b, a = signal.butter(3, [5500,6050], 'bandpass', fs = fs)
#wave = signal.filtfilt(b, a, wave)#, padlen=0)#int(len(data)/2))#150)
#b, a = signal.butter(1, 1000, 'high', fs = fs)
#wave = signal.filtfilt(b, a, wave, padlen=10000)
#wave -= np.mean(wave)

doublewave = np.zeros(len(wave),dtype = 'float')
#group = 1024
#off = 92000
#for i in range(len(wave)):
#    if i % (group + off) != 0: continue
#    try:
#        doublewave[i:i+group] = wave[i:(i+group*2):2]
#    except: pass
#exit()

#doublewave = wave[:]
print(doublewave)

pars = Parameters()
pars.add('amp',value = max(wave[10000:]), vary = False)#True)
#pars.add('freq',value = 1/5, vary = True)
pars.add('freq',value = peakFreq/192000.0*2*np.pi , vary = True)
pars.add('phase',value = 0.0, vary = True)#1.0)
pars.add('offset',value = 0.0, vary = False)#True)

x = np.arange(len(wave))
#out = minimize(sinusoid, pars, args = (x[100000:-100000],),\
#	kws = {'data': np.abs(wave[100000:-100000])},\
#    scale_covar = True, method = 'leastsq')#,\
#print(fit_report(out))
#out.params['phase'].set(value = out.params['phase'])#+np.pi/2)
#out.params['freq'].set(value = out.params['freq']*2)
doublewave = np.power(wave,2)#sinusoid(out.params,x,abs = False)
#doublewave = 100*(doublewave - np.mean(doublewave[1000:]))

#test = (1.0-2.0*wave*wave)
#wave = wave - np.mean(wave)
test = wave*wave#(wave*wave)
doublewave = (test - np.mean(test))

#plt.plot(doublewave)
#plt.show()
#exit()


#plt.plot(-4*(doublewave[1000:2000] - np.mean(doublewave)))
#plt.plot(wave[1000:2000])
#plt.show()
#exit()
#print(fit_report(out))

#Wave is about when x = 6*pi
#When x = 9*pi, sin(9*pi*freq) = 0, sin(15*pi*freq) = 0
#9*pi*freq =

#Butterworth filter works by knowing the point sampling rate and then
#   knowing where the cutoff needs to be...i.eself.
#   a sampling rate of ????

#Wn is A scalar or length-2 sequence giving the critical frequencies.
#   For a Butterworth filter, this is the point at which the gain drops to
#   1/sqrt(2) that of the passband (the “-3 dB point”).
#For digital filters, Wn is normalized from 0 to 1, where 1 is the Nyquist
#   frequency, pi radians/sample. (Wn is thus in half-cycles / sample.)
#For analog filters, Wn is an angular frequency (e.g. rad/s).

#Nyquist frequency is half of the sampling rate
nyquist = fs/2
#print(nyquist)
cutoff = (2000/nyquist)
endoff = (2100/nyquist)

#cutoff = (192000)/len(wave)
#cutoff = 11000
#b, a = signal.butter(3, [cutoff, endoff], 'bandpass')#,analog=True)# 0.125)
#b, a = signal.butter(3, [10500*2,10950*2], 'bandpass',fs=fs)# 0.125)
#for i in range(repeat):
#if method == 'butter':a
#print(wave[0:int(len(wave)/2)])

#1pi = 3.14
#data = wave[::2]*output[111003:int(len(wave)/2)+111003]
#data = wave[::2]*output[:int(len(wave)/2)]
#data = doublewave*output
#predata = np.roll(doublewave,2)*output#np.roll(doublewave,15)*output
predata = np.roll(doublewave,0)*output#np.roll(doublewave,15)*output
#predata = np.roll(wave,2)*output
#data = signal.filtfilt(b, a, data)#, padlen=10000)#int(len(data)/2))#150)

lpfreq = 100
b, a = signal.butter(1, lpfreq, 'low', fs = fs)
data = signal.filtfilt(b, a, predata, padlen=1000)#int(len(data)/2))#150)
pars.add('freq',value = peakFreq/192000.0*2*np.pi , vary = True)

#plt.plot(wave)
#plt.plot(sinusoid(out.params,x)[::4])

#plt.plot((wave[:]))
#plt.plot(output)
plt.plot(data)
plt.show()
exit()


lag = 0
min = np.inf
step = 512#128
offset = 0#20000
template = data[:fs*3]
for i in range(int(fs/2),1000000,step):
    dummy = np.sum(np.abs(data[i:i+fs*3:step]-template[::step]))
    #dummy = np.abs(np.mean(template - np.roll(template,i)))
    if dummy < min:
        min = dummy
        lag = i
print(lag)

highindex = np.argmax(data[20000:lag+20000])
highindex += 20000
print(highindex)



first16O = []
second16O = []
firstD = []
margin = 10000
#relmax = argrelextrema(data[highindex-margin + lag*i*2:highindex+lag*3+margin],np.greater)[0] + highindex - margin + lag*i*2
#relmin = argrelextrema(data[highindex-margin + lag*i*2:highindex+lag*3+margin],np.less)[0] + highindex - margin + lag*i*2
relmax = argrelextrema(data[margin:],np.greater)[0] + margin
relmin = argrelextrema(data[margin:],np.less)[0] + margin
print(list(relmax),list(relmin))

for i in range(int(len(data)/lag)+1):
    #tempmax = np.armin(np.abs(relmax-(highindex+lag*i)))
    #Finds index difference from estimated peak to actual peak.....
    idxmax = (np.abs(relmax - highindex)).argmin()
    #print(relmax[idx])

    #Find nearest minimum to the left of the idx peak for p2p measure....
    #Difference measurement of relmin - idx
    diff = np.array(relmin - relmax[idxmax], dtype = 'float')
    diff[diff >= 0] = np.inf
    diff = np.abs(diff)
    idxmin = np.argmin(diff)

    #~150k is approximately the offset to get to the D peakFreq
    dindex = highindex - 151000

    #Reset to new peak index!!!
    highindex = relmax[idxmax] + lag

    if dindex < 0: continue

    #Store peak to peak value to array
    first16O.append(data[relmax[idxmax]]-data[relmin[idxmin]])

    #repeate max minux min measurement for deuterated line
    didxmax = (np.abs(relmax - dindex)).argmin()
    diff = np.array(relmin - relmax[didxmax], dtype = 'float')
    diff[diff >= 0] = np.inf
    diff = np.abs(diff)
    didxmin = np.argmin(diff)

    #Store peak to peak value to array for deuterated line
    firstD.append(data[relmax[didxmax]]-data[relmin[didxmin]])

firstD = np.array(firstD)
first16O = np.array(first16O)
print(np.std(first16O),np.std(firstD))
ratio = firstD/first16O
ratio /= np.mean(ratio)
ratio -= 1
ratio *= 1000
print(np.std(ratio))
plt.plot(ratio)
plt.show()
#exit()



# for local maxima
#relmax = argrelextrema(data[20000:lag+20000], np.greater)
# for local minima
#relmin = argrelextrema(data[20000:lag+20000], np.less)
#print(list(relmax[0]), list(relmin[0]))
'''
for i in range(lag-step,lag+step):
    dummy = np.sum(np.abs(data[i:i+fs*3]-template))
    if dummy < min:
        min = dummy
        lag = i
'''

#print(lag)


#data2 = np.roll(data,435600)
#data2 = np.roll(data,-lag)

#print(lag)
#plt.plot(template)
#plt.plot(data[lag:lag+fs*3])
#plt.plot(np.cumsum(data))

tripderiv = data# (np.diff(data))
#tripderiv = integrate.cumtrapz(tripderiv - np.mean(tripderiv[20000:lag+20000]))
#tripderiv = integrate.cumtrapz(tripderiv - np.mean(tripderiv[20000:lag+20000]))
#tripderiv = integrate.cumtrapz(tripderiv - np.mean(tripderiv[20000:lag+20000]))


#plt.plot(integrate.cumtrapz(tripderiv - np.mean(tripderiv[20000:lag+20000])))

plt.plot(tripderiv)

#plt.plot(data2)

#series = Series.from_csv('daily-minimum-temperatures.csv', header=0)
#plot_acf(data[::2000])
plt.show()
exit()


#exit()

f, Pxx_den = signal.welch(data, fs, nperseg=1024*32)
plt.semilogy(f, Pxx_den)
#plt.ylim([0.5e-5, 1])
plt.xlabel('frequency [Hz]')
plt.ylabel('PSD [V**2/Hz]')
plt.show()

w, h = signal.freqs(b, a)
plt.plot(w*180/np.pi, 20 * np.log10(abs(h)))
plt.xscale('log')
plt.title('Butterworth filter frequency response')
plt.xlabel('Frequency')# [radians / second]')
plt.ylabel('Amplitude [dB]')
plt.margins(0, 0.1)
plt.grid(which='both', axis='both')
plt.axvline(lpfreq, color='green') # cutoff frequency
plt.show()


#plt.show()
'''
#test = wave[::2]*output[111003:int(len(wave)/2)+111003]
#test = wave - np.mean(wave)
test = doublewave#*output
f, Pxx_den = signal.welch(test, fs, nperseg=25600)
plt.semilogy(f, Pxx_den)
#plt.ylim([0.5e-5, 1])
plt.xlabel('frequency [Hz]')
plt.ylabel('PSD [V**2/Hz]')
plt.show()
'''

#print(data[:,1])
