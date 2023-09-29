from common.libraryImports import *

from scipy.signal import savgol_filter

from hapi import *

###Spectral Module###

# mol_id = ['1 = H2O', '2 = CO2', '3 = O3', '4 = N2O', '5 = CO',\
# 	'6 = CH4', '7 = O2', '8 = NO', '9 = SO2', '10 = NO2', 11 = NH3',\
# 	'12 = HNO3', 13 = OH', '14 = HF', '15 = HCl', '16 = HBr', 17 = HI',\
# 	'18 = ClO', '19 = OCS', '20 = H2CO', '21 = HOCl', '22 = N2',\
# 	'23 = HCN', '24 = CH3Cl', '25 = H2O2', '26 = C2H2', '27 = C2H6',\
# 	'28 = PH3', '29 = COF2', '30 = SF6', '31 = H2S', '32 = HCOOH',\
# 	'33 = HO2', '34 = N/A', '35 = ClONO2', '36 = NO+', '37 = HOBr',\
# 	'38 = C2H4', '39 = CH3OH', '40 = CH3Br', '41 = CH3CN', '42 = CF4',\
# 	'43 = C4H2', '44 = HC3N', '45 = H2', '46 = CS', '47 = SO3',\
# 	'48 = C2N2', '49 = COCl2', '50 = SO', '51 = C3H4', '52 = CH3'\
# 	'53 = CS2']

"""
def _wofz(x):
	#Returns the fadeeva function for complex argument
	#wofz = exp(-x**2)*erfc(-i*x)
	return wofz(x)

def _erfc(x):
	#Return the complementary error function.
	#erfc = 1 - erf(x)
	return erfc(x)

def _erf(x):
	#Returns the error function.
	#erf = 2/sqrt(pi)*integral(exp(-t**2), t = [0,z])
	return erf(x)
"""


def domShiftInv(pars, x):  # Inverted
    """Inverts wavenumber to the arbitrary domain
	"""
    vals = pars.valuesdict()
    c = []
    wvlngthOrder = -1
    for val in vals.keys():
        if "shift" in val:
            wvlngthOrder += 1
    for i in range(wvlngthOrder):
        c.append(vals["shift_c" + str(i)])
    if len(c) == 2:
        return (x - c[0]) / c[1]
    if len(c) == 3:
        #result = (np.sqrt(-4 * c[0] * c[2] + 4 * c[2] * x + c[1] ** 2) - c[1]) / (
        #    2 * c[2]
        #)
        result = (-c[1] - np.sqrt(np.power(c[1]**2) - 4 * (c[0]-x) * c[2])) / (2 * c[2])
        if result > 0 and result < 2048:
            return result  # and not any(np.isnan(result)): return result
        else:
            return (-np.sqrt(-4 * c[0] * c[2] + 4 * c[2] * x + c[1] ** 2) + c[1]) / (
                2 * c[2]
            )
    if len(c) >= 4:
        result = (
            1
            / (3 * 2 ** (1 / 3))
            * (
                (
                    np.sqrt(
                        (
                            -27 * c[0] * c[3] ** 2
                            + 9 * c[1] * c[2] * c[3]
                            - 2 * c[2] ** 3
                            + 27 * c[3] ** 2 * x
                        )
                        ** 2
                        + 4 * (3 * c[1] * c[3] - c[2] ** 2) ** 3
                    )
                    - 27 * c[0] * c[3] ** 2
                    + 9 * c[1] * c[2] * c[3]
                    - 2 * c[2] ** 3
                    + 27 * c[3] ** 2 * x
                )
                ** (1 / 3)
            )
            - (2 ** (1 / 3) * (3 * c[1] * c[3] - c[2] ** 2))
            / (
                3
                * c[3]
                * (
                    np.sqrt(
                        (
                            -27 * c[0] * c[3] ** 2
                            + 9 * c[1] * c[2] * c[3]
                            - 2 * c[2] ** 3
                            + 27 * c[3] ** 2 * x
                        )
                        ** 2
                        + 4 * (3 * c[1] * c[3] - c[2] ** 2) ** 3
                    )
                    - 27 * c[0] * c[3] ** 2
                    + 9 * c[1] * c[2] * c[3]
                    - 2 * c[2] ** 3
                    + 27 * c[3] ** 2 * x
                )
                ** (1 / 3)
            )
            - -c[2] / (3 * c[3])
        )
        return result
        # return (1/(81*np.cbrt(2)*c[3]))*((np.sqrt((-531441*c[0]*c[3]**2 + 177147*c[1]*c[2]*c[3] \
        # - 39366*c[2]**3 + 531441*c[3]**2*x)**2 + 4*(2187*c[1]*c[3] - 729*c[2]**2)**3) - \
        # 531441*c[0]*c[3]**2 + 177147*c[1]*c[2]*c[3] - 39366*c[2]**3 + 531441*c[3]**2*x)**(1/3)) - \
        # (np.cbrt(2)*(2187*c[1]*c[3] - 729*c[2]**2)) / (81*c[3]*(np.sqrt((-531441*c[0]*c[3]**2 + \
        # 177147*c[1]*c[2]*c[3] - 39366*c[2]**3 + 531441*c[3]**2*x)**2 + 4*(2187*c[1]*c[3] - \
        # 729*c[2]**2)**3) - 531441*c[0]*c[3]**2 + 177147*c[1]*c[2]*c[3] - 39366*c[2]**3 + \
        # 531441*c[3]**2*x)**(1/3)) - c[2]/(3*c[3])


"""
############################## Wrapper ########################################
This is the bread and butter of the software and can be applied using a fit
parameter dictionary of the form:
        i.e.  pars = lmfit.Parameters()
        pars.add(key, value = float, min = float, max = float, vary = bool)
    containing each of the environmental parameters
        (temp [cell temp (K)], press [path pressure (hPa)], path [path length (cm)])
        and voigt0_ppmv [volume mixing ratio of primary isotopologue (ppmv)]

    NOTE: parameters 'delw' where w is the isotopologue number of the
    NON-primary isotope can be used to compute varying isotopologue concentraitons
    as a function of permil fractionation with respect to natural abundances.

maserHitranKeys is a configuration table that identifies molecular properties
    based on HITRAN molecular and isotopologue numbering

hitran is the table that ultimately decides the lineshapes.
    col0 = placeholder for internally computed molecular masses
    col1 = molecule number
    col2 = isotopologue number
    col3 = center wavenumber
    col4 = spectral intensity (recall HITRAN scales according to abundances)
    col5 = einsteinA (unused?)
    col6 = air broadening coefficient
    col7 = self broadening coefficient
    col8 = lower state energy
    col9 = spectral temperature dependence
    col10 = pressure shift
    col11 = OBSOLETE

raw = True returns absorption cross sections based on x as wavenumber

raw = False applies wavenumber transfer function to x as power curve using
    parameters 'shift_cz' where z is the polynomial coefficient, then computes
        a laser intensity background scaled using 'back_c1' with optional summed
        fringing as a function of wavenumber using 'amp','freq', and 'phase'
    'back_cz' where z is the polynomial coefficient are optional if the input
        power curve is uncharacteristic of the laser intensity relationship.
    'offset' can also be used to tare the laser intensity zero if this has not
        already been completed in preconditioning
"""


def spectralWrapper(
    pars,
    x,
    hitran,
    molecularInfoDict,
    raw=False,
    prefix=None,
    data=None,
    current=None,
    modelType="wofz",
):
    """Spectral wrapper.

	Wraps HITRAN spectral output into suitable form for fitting

	inputs:
		pars: parameter dictionary containing fit variables
		x: domain of arbitrary values
		hitran: matrix containing absorption features
		molecularInfoDict: Dictionary containing information
			fundamental molecular and isotopologue data.
		raw: Bool, determines if a background is applied to the data
		prefix: ??? Obsolete
		data: (optional) real data to compare to for residuals.
		modelType:
			Options for choosing how to display fit
				'wofz': Fadeeva function

	outpus: Return model based on x OR residual if "data" is populated.
	"""

    #a = time.time()
    # def spectrumFitFeeder(pars, x, hitran, masterHitranKeys, QTDict = None, raw = False, prefix = None, data = None, modelType = 'wofz',current=None):
    # try:
    vals = pars.valuesdict()
    # except:
    #    vals = pars  # copy.deepcopy(pars)

    # Parameter used for mapping injection current to fixed laser power while leaving power to float against wavelength
    if raw:
        y = 1.0 * x[:]
    elif not raw:
        if current is None:
            y = 1.0 * domainShift(pars, 1.0 * x)
        else:
            #y = 1.0 * domainShift(pars, 1.0 * current)
            y = 1.0 * domainShift(pars, 1.0 * x)

    # Break spectral model into various components
    # 	First: figure out how many independent concentrations.
    # 	Second: Iterate through the various concentrations
    # 		combining absorption cross sections.
    # 	Third: Apply to absorption path with q, p, t, path
    # 	Fourth: Apply background to absorption data.

    # Absorption path properties
    p = vals["press"]
    t = vals["temp"] + 273.15
    path = vals["path"]

    # Key used to determine base string for fit parameters
    # 	associated with mixing ratio
    concKey = "conc"

    # concentrationList = []

    mols = []
    isos = []
    moliso = []
    for key in list(vals.keys()):
        if concKey in key:
            # concentrationList.append(key)
            mol = int(key.split("_")[1])
            iso = int(key.split("_")[2])
            mols.append(mol)
            isos.append(iso)
            moliso.append(mol + float(iso) / 10)

    sortIndices = np.argsort(moliso)
    # concentrationList = concentrationList[sortIndices]
    mols = np.array(mols)[sortIndices]
    isos = np.array(isos)[sortIndices]

    model = np.zeros(len(y), dtype="float")
    model = np.exp(model)

    # Search for unique isos in a given molecule list....
    for mol in np.unique(mols):
        isoSubset = isos[np.where(mols == mol)[0]]
        # Narrow lines by molecule....
        lineSubset = hitran[np.where(hitran[:, 1] == mol)[0], :]
        availIsos = np.unique(lineSubset[:, 2])

        # for mol in np.unique(hitran[:,1]):
        # 	for iso in np.unique(hitran[:,2]

        hitranIsos = np.unique(lineSubset[:, 2])
        commonIsos = np.intersect1d(isoSubset, hitranIsos)
        assertIso = int(min(commonIsos))

        for iso in hitranIsos:
            if iso in commonIsos:
                # If iso is part of the common iso's, assert to the fit
                # 	specified value.
                lineSubSubset = lineSubset[np.where(lineSubset[:, 2] == iso)[0], :]
                q = vals[concKey + "_" + str(int(mol)) + "_" + str(int(iso))]

                #Alternative for when I want to run fractionation vals....
                if iso != assertIso:
                    mainq = vals[concKey + "_" + str(mol) + "_" + str(assertIso)]
                    q = mainq*(q/1000.0 + 1.0)
            else:
                # If iso in hitran list is unspecified, assert to highest
                # 	iso number for the given molecule
                lineSubSubset = lineSubset[np.where(lineSubset[:, 2] == iso)[0], :]
                q = vals[concKey + "_" + str(mol) + "_" + str(assertIso)]
            # Note: no condition for a fit parameter that has no corresponding
            # 	absorption in the given HITRAN list. Consider adding exception.

            # model = multiSpectrum(y, hitran, molecularInfoDict, p, t, q, path, 'wofz')
            tmpModel = multiSpectrum(
                y, lineSubSubset, molecularInfoDict, p, t, q, path, modelType#"wofz"
            )
            tmpModel = transmissionSpectrum(y, tmpModel, p, t, q, path)
            model *= tmpModel

    # Apply background if raw is not True
    if not raw:
        if current is not None:
            #background = laserBackground(pars, x) * (1 + fringe(pars, y))
            background = laserBackground(pars, current)# * (1 + fringe(pars, y))
            model = model * background + vals["offset"]
        else:
            background = laserBackground(pars, x)
            model = model * background
        # model = smoothingFunction(model,2,1,'convolve')
        # model = smooth(model,10)
        # print(model)
        # input('wait')

        # if not raw:
        #    background = laserBackground(pars, x) * (1 + fringe(pars,y))#x))# * laserBackground(pars, x)
        #    model = np.exp(-model)*background + vals['offset']

    # 20 point smooth
    # print(time.time() - a)

    #FOR ISOTOPE WORK, dividing by data seems to work well (for power normalization),
    # For CLH-2 a little less clear...


    if data is None:
        return model
    #return np.abs(model - data)
    
    ###### Test model for residuals to be based on 0 - 1 absorption spectrum.
    #   Hope is to emphasize deviations along curve and semi-normalize residual goal
    #   to be independent of laser power. So I need to divide by background (then natural log1p)    
    #res = (np.log1p(model/background) - np.log1p(data/background))
    res = np.log(np.abs(model/data)) # Same as the subtraction above.
    # np.abs added to the log argument to ensure no nans come from the residual to fail minimization
    # np.log1p added because with very small values, np.log is inaccurate.
    
    #   Need to come up with way to STRONGLY penalize residual with I0 < I. Recovered signal can
    #   NEVER be greater than the unattenuated signal....   
    #   So where( data/background > 1 ), take 5 point to either side, if negative 
    
    negMask = np.where(data/background > 1.0)[0]
    for index in negMask:
        try:
            if np.mean(data[index-3:index+5]/background[index-3:index+5]) > 1.0:
                res[index] * 100.0
        except:
            pass
            
    #res[np.where(data/background > 1.0)[0]] *= 4.0
    
    return res
    
    #return ((model) - (data)) / (model)
    #return (model+1)/(1+data)-1# / np.abs(1.0+data)  # np.power((model - data),2)
    #return np.log(-np.log(model / background)) - np.log(-np.log(data / background))
    # return np.power(model - data, 2)  # (model - data)/background)


def fitParsInit(wavelengthPolyOrder, backgroundPolyOrder, uniqueIDs=["1_1"], extra=None):
    """Initialize fitting parameters

	Loads fitting dictionary based

	inputs:
		wavelengthPolyOrder: order of polynomial for
			domain to wavelength conversion
		backgroundPolyOrder: order of polynomial for
			domain to laser power curve
		uniqueIDs: Array with mol_iso values for unique
			fitting (i.e. 1_1 for H216O, 1_2 for H218O)

	outputs:
		pars: fitting dictionary
	"""

    pars = Parameters()
    for i in range(backgroundPolyOrder + 1):
        pars.add(
            "back_c" + str(i), value=0, vary=True
        )  # , min = 0, max = 1.0)#, max = backMaxs[i], min = backMins[i])#, value = backArr[i])#plsq[i])
    for i in range(wavelengthPolyOrder + 1):
        pars.add(
            "shift_c" + str(i), value=0, vary=True
        )  # , min = shiftMins[i], max = shiftMaxs[i])#, vary = True)
    # pars.add('press', value = data['press'][10], min = 1, max =data['press'][10], vary = False)#True)#False)
    pars.add(
        "press", value=840, vary=False
    )  # True)#, min = 1, max =1400, vary = True)# False)#True)#True)#False)
    pars.add(
        "temp", value=40, vary=False
    )  # True)#False)#True)#, min = -10+273.15, max = 100+273.15, vary = False)#True)#False)# True)#False)
    pars.add("path", value=53.3, vary=False)  # min = 2700, max = 10000, vary = False)

    # for iso in range(len(isoVary)):
    # 	pars.add('voigt'+str(iso)+'_ppmv', value = 5000.0, vary = True)#min = 0, max = 200000, vary = True)# min = 0, max = 200000, vary = True)

    for uniqueID in uniqueIDs:
        pars.add("conc_" + uniqueID, value=5000.0, vary=True, min=0, max=1e6)

    if extra is not None:
        for key in extra:
            pars.add(key, vary=False)

    return pars


def instrumentFunction(y, model, res=0.001, func="gaussian"):
    resampledModel = np.zeros(len(model), dtype="float")

    # 0.001 nm resolution ~ 0.005 cm-1 Resolution

    for i in range(len(model)):
        instFunc = np.exp(-0.5 * ((y - y[i]) / 0.005) ** 2)
        instFunc /= sum(instFunc)
        resampledModel[i] = (model * instFunc)[i]


def smoothingFunction(data, points=3, repeat=1, method="convolve"):
    # Butterworth filter works by knowing the point sampling rate and then
    #   knowing where the cutoff needs to be...i.eself.
    #   a sampling rate of ????
    cutoff = (points) / len(data)
    b, a = signal.butter(3, cutoff)  # 0.125)
    for i in range(repeat):
        if method == "butter":
            data = signal.filtfilt(b, a, data, padlen=int(len(data) / 2))  # 150)
        elif method == "savgol":
            #savgol_filter(data,win_length, poly_order)
            data = savgol_filter(data, points, 2)
        else:
            data = np.convolve(data, np.ones(points) / points, mode="same")
        
    return data


# This function was modified from scipy cookbook signal processing section
def smooth(x, window_len=10, window="hanning"):
    """smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    input:
        x: the input signal
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal

    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)

    see also:

    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter

    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """
    """
    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"
	"""

    s = np.r_[x[window_len - 1 : 0 : -1], x, x[-2 : -window_len - 1 : -1]]
    # print(len(s))
    if window == "flat":  # moving average
        w = np.ones(window_len, "d")
    else:
        w = eval("np." + window + "(window_len)")

    y = np.convolve(w / w.sum(), s, mode="valid")
    return y[int(window_len / 2 - 1) : -int(window_len / 2)]


def transmissionSpectrum(y, model, p, t, q, path):
    boltz = 1.3806485279e-23
    amp = 1.0e-6 * 1.0e-4 * q * (p) * path / (boltz * t)
    model = np.exp(-amp * model)
    return model


# @jit(forceobj=True)
def multiSpectrum(x, hitran, molecularInfoDict, p, t, q, path, modelType="wofz"):
    """Multi absorption spectral model.

	Model that merges many absorption features for a given
	molecular isotopologue. See multiMoleculeSpectrum for
	plotting independent features.

	inputs:
		x: wavenumber domain
		hitran: matrix with HITRAN lines
		molecularInfoDict: Dictionary containing information
			fundamental molecular and isotopologue data.
		p: pressure
		t: temperature
		q: mixing ratio
		path: path length
		modelType: use "wofz" initially

	outputs:
		Tuple of wavenumber domain and absorption cross sections.
	"""

    lines = np.arange(len(hitran[:, 0]))

    if np.nanmean(hitran[:, 0]) == 0:
        for i in lines:
            # hitran[i,0] = masterHitranKeys[str(int(hitran[i,1]))+' '+str(int(hitran[i,2]))][9]#+ ' - ' + self.masterHitranKeys[mol+ ' 1'][3])
            hitran[i, 0] = molecularInfoDict[
                str(int(hitran[i, 1])) + "_" + str(int(hitran[i, 2]))
            ][
                "molmass"
            ]  # + ' - ' + self.masterHitranKeys[mol+ ' 1'][3])

    # sol[m/s], boltzmann [J/K], press [mbar], temp [K], planck [J*s], avoNum [molec/mol]
    sol = 299792458.0
    boltz = 1.3806485279e-23
    refPress = 1013.25
    refTemp = 296.0#6.0
    planck = 6.62607004e-34
    avoNum = 6.022140857e23
    # Total internal partition sum calculation based on temperature
    Qtips = np.zeros(len(hitran[:, 0]), dtype="float")

    # NEED TO VERIFY that more than one isotope is not applied to a single isotope TIPS
    # This iterates through the unique molecule id's and isotopologue id's
    #   to populate the total internal partition sums based on temperature
    for mol in np.unique(hitran[:, 1]):
        for iso in np.unique(hitran[:, 2]):
            tips = molecularInfoDict[str(int(mol)) + "_" + str(int(iso))]["tips"]
            Qtips[np.where((hitran[:, 1] == mol) * (hitran[:, 2] == iso))[0]] = TIPStemp(
                refTemp, tips
            ) / TIPStemp(t, tips)

    vmrs = np.zeros(len(hitran[:, 0]), dtype="float")
    vmrs[:] = q

    # Wrote this with the intention to provide mole fraction correction to self broadening
    molFrac = vmrs * 1.0e-6 # * 28.97 / 18.015#29.0/18.0#28.08 / 18.02 * 1/761
    
    #molFrac = vmrs * 1.0e-6 * (28.97 / 18.015) / ((1-vmrs*1e-6)*(18.015/28.97) + vmrs*1e-6*(28.97/18.015))
    for mol in np.unique(hitran[:, 1]):
        for iso in np.unique(hitran[:, 2]):
            abund = molecularInfoDict[str(int(mol)) + "_" + str(int(iso))]["abund"]
            redIndex = np.where((hitran[:, 1] == mol) * (hitran[:, 2] == iso))[0]
            molFrac[redIndex] *= abund

    # Added ppmv[hitran[i,9]] so that the mixing ratio corresponds only to the index
    # hitranPars = np.c_[0 - molMass, 1 - molnum, 2 - isonum, 3 - wavelength, 4 - intensity, 5 - einsteinA, 6 - airWidth, \
    #    7 - selfWidth, 8 - lowerStateEnergy, 9 - tempDep, 10 - pressShift, 11 - ppmvNum]

    # volConc = (p/9.869233e-7)/(boltz*t)
    return spectrumMatrix(
        x, hitran, lines, Qtips, molFrac, p, t, q, path, modelType=modelType#"wofz"
    )


# @jit(nopython=True)
# @jit  # (nopython=True, parallel=True)
# @jit(forceobj=True)
# @nb.njit
def spectrumMatrix(x, hitran, lines, Qtips, molFrac, p, t, q, path, modelType="wofz"):
    #print(modelType)
    sol = 299792458.0 #m/s
    boltz = 1.3806485279e-23 #J/K
    refPress = 1013.25 #mbar
    refTemp = 296.0#296.0
    planck = 6.62607004e-34
    avoNum = 6.022140857e23
    lineShifts = hitran[:, 3] + hitran[:, 10] * p / refPress

    # lorWidths = ((1.0 - vmrs*1.0e-6)*hitran[:,6] + vmrs*1.0e-6*hitran[:,7])*\
    #    (p/refPress)*np.power((refTemp/t),(hitran[:,9]))

    # HWHM when skipping self broadening (must be done for HAPI match)
    #lorWidths = hitran[:, 6] * (p / refPress) * np.power((refTemp / t), (hitran[:, 9]))
    # Gamma0_ref*p/pref*(Tref/T)**TempRatioPower

    ##### The following was used for Isotope work, does not seem to be working well for CLH-2 ####
    ##### This is likely due to using mole fractions without accounting for various isotopes #####
    # Self broadening alternative to lorentzian widths
    lorWidths = (
        (((1.0 - molFrac) * hitran[:, 6]) + ( molFrac * hitran[:, 7]))
        * (p / refPress)
        * np.power((refTemp / t), (hitran[:, 9]))
    )

    # HWHM
    dopWidths = (lineShifts) * np.sqrt(
        2.0 * boltz * t / (np.power(sol,2.0) * (hitran[:, 0]) / (avoNum * 1000.0))
    )
    #dopWidths = 7.17e-7 * (lineShifts/sol) * np.sqrt(t/hitran[:,0])
    #dopWidths *= np.sqrt(1/1000)*np.sqrt(np.log(2))#0.9
    #dopWidths /= np.sqrt(np.log(2))#0.9 # By doing this SOCRATES Chamber test matches better.
    #dopWidths *= 2#*sqrt(np.log(2))
    #dopWidths *= *sqrt(np.log(2))
    #dopWidths *= np.sqrt(2.0)
    #### sqrt(log(2)) ~ 0.83

    # When I add the following line, scipy matches Pseudo
    # When I remove it, scipy matches hapi # may be deprecated comment?
    #dopWidths *= np.sqrt(1/10000)

    amps = (
        Qtips
        * hitran[:, 4]
        * np.exp(-planck * sol * 100.0 * hitran[:, 8] / (boltz * t))
        * (1.0 - np.exp(-planck * sol * 100.0 * lineShifts / (boltz * t)))
        / (
            np.exp(-planck * sol * 100.0 * hitran[:, 8] / (boltz * refTemp))
            * (1.0 - np.exp(-planck * sol * 100.0 * lineShifts / (boltz * refTemp)))
        )
    )

    const = 1.4388028496642257

    amps *= (1.0 / lineShifts) * 1.0 / np.tanh(const * lineShifts / (2.0 * t))
    ampsy = x * np.tanh(const * 100.0 * x / (2.0 * t))

    if modelType == "wofz":
        amps *= 1.0 / dopWidths * 1.0 / np.sqrt(np.pi)
        zs = (1.0 / dopWidths) * (1.0 + (1.0j * lorWidths))# * np.sqrt(np.log(2.0))
    elif modelType == 'rautian':
        vh = lorWidths*hitran[:,7]
        vt = lorWidths + vh
        zs = 1.0/dopWidths * (1.0 + (1.0j*vt))
    else:
        dopWidths *= np.sqrt(np.log(2))  # / np.sqrt(2.0)

    # if modelType == 'wofz':
    # 	zs = 1/dopWidths * (1.0 + (1.0j*lorWidths))
    # elif modelType == 'rautian':
    #    vh = lorWidths*hitran[:,7]
    #    vt = lorWidths + vh
    #    zs = 1/dopWidths * (1.0 + (1.0j*vt))

    if modelType == "pseudo":
        fg = dopWidths * np.sqrt(np.pi) / 2

        fl = lorWidths
        f = np.power(
            np.power(fg, 5)
            + 2.69269 * np.power(fg, 4) * fl
            + 2.42843 * np.power(fg, 3) * np.power(fl, 2)
            + 4.47163 * np.power(fg, 2) * np.power(fl, 3)
            + 0.07842 * fg * np.power(fl, 4)
            + np.power(fl, 5),
            1 / 5,
        )
        eta = (
            1.36603 * (fl / f)
            - 0.47719 * (fl / f) * (fl / f)
            + 0.11116 * np.power(fl / f, 3)
        )

    model = np.zeros(len(x), dtype=np.float64)

    # time2 = time.time()
    for i in lines:
        if modelType == "pseudo":
            lorShape = f[i] / (
                np.pi * (np.power(x - lineShifts[i], 2) + np.power(f[i], 2))
            )
            gauShape = np.exp(
                -np.power(x - lineShifts[i], 2) / (2 * np.power(f[i], 2))
            ) / (f[i] * np.sqrt(2 * np.pi))
            line = amps[i] * ampsy * (eta[i] * lorShape + (1 - eta[i]) * gauShape)
        elif modelType == "wofz":
            # wofzArg = (x - lineShifts[i]) * zs[i].real + 1.0j * zs[i].imag
            # line = amps[i] * ampsy * wofz(wofzArg).real
            #wofzArg = (x - lineShifts[i]) * np.real(zs[i]) + 1.0j * np.imag(zs[i])
            wofzArg = ((x - lineShifts[i]) * np.real(zs[i]) + 1.0j * np.imag(zs[i]))
            line = (
                amps[i] * ampsy * np.real(njitWofz(wofzArg))
            )  # np.real(njitWofz(wofzArg))
        elif modelType == "alt":
            line = amps[i]  # * dopWidths[i] * np.sqrt(np.pi)#1/np.sqrt(np.pi)
            line *= ampsy * PROFILE_VOIGT(lineShifts[i], dopWidths[i], lorWidths[i], x)[0]
        elif modelType == "rautian":
            wofzArg = (x - lineShifts[i]) * np.real(zs[i]) + 1.0j * np.imag(zs[i])
            line = (
                amps[i]
                * ampsy
                * (
                    njitWofz(wofzArg)#sc.wofz(wofzArg)
                    / (
                        1
                        - np.sqrt(np.pi)
                        * njitWofz(wofzArg)#wofz_fn(wofzArg)
                        / ((lineShifts[i] / x) * dopWidths[i])
                    )
                ).real
            )
        else:
            #print('here')
            line = model
        # try:
        model += line
        # except:
        #    pass

    
    if modelType == "hapi":  # or modelType == 'ht':
        #print('here')
        db_begin("data")
        # select('H2O')
        fetch_by_ids("H2O", [1, 2, 3, 4, 5, 6], min(x), max(x))
        p = p / 1013.25
        newx, model = absorptionCoefficient_Voigt(
            ((1, 1), (1, 2), (1, 3), (1, 4), (1, 5)),
            "H2O",
            HITRAN_units=True,
            GammaL="gamma_air",
            WavenumberGrid=list(x),
            Environment={"p": p, "T": t},
        )
        if not np.array_equal(x, newx):
            model = np.flip(model, axis=0)
        return model
    
    """
	if modelType == 'ht':
		p = p/1013.25
		x,model = absorptionCoefficient_HT(((1,1),(1,2),(1,3),(1,4)),'H2O',
			OmegaStep=0.0001,HITRAN_units=True,GammaL='gamma_air',OmegaWing = 1000.0,
			Environment={'p':p,'T':t})
	"""
    return model


# @vectorize(nopython=True)
# @njit
#@nb.jit(forceobj=True)
def njitWofz(z):
    return sc.wofz(z)
    # return np.exp(-np.power(z, 2)) * sc.erfc(nb.complex128(-1j * z))


# tmp = np.zeros(len(z), dtype=np.float64)  # complex)
# or i in np.arange(len(z)):
#    tmp[i] = np.real(np.exp(-(np.power(z[i], 2)))) * np.float(
#        np.real(mpm.erfc(-(z[i])))
#    )
# return tmp


def domainShift(pars, x):
    """Calculate arbitrary domain to wavenumber conversion.

	inputs:
		pars: line fit parameter dictionary
		x: arbitray domain

	outputs:
		c: wavenumber domain
	"""
    vals = pars.valuesdict()
    c = 0.0
    wvlngthOrder = -1
    for val in vals.keys():
        if "shift" in val:
            wvlngthOrder += 1
    for i in range(wvlngthOrder + 1):
        c += vals["shift_c" + str(i)] * np.power(1.0 * x, 1.0 * i)
    return c


def fringe(pars, x, data=None):
    vals = pars.valuesdict()
    model = pars["amp"] * np.cos(pars["freq"] * (x) - (pars["phase"]))  # + \

    if data is None:
        return model
    return model - data
    # pars['amp']*pars['amp2']*np.cos(pars['freq']*x - pars['phase2'])# \
    # pars['amp']*np.cos(pars['freq']*x - pars['phase3'])


def backgroundWithFringe(pars, x, data=None):
    background = laserBackground(pars, x) * (1 + fringe(pars, x))  # domainShift(pars,x)))
    # background = laserBackground(pars,x) * (1 + fringe(pars,domainShift(pars,x)))
    if data is None:
        return background
    else:
        return background - data


def laserBackground(pars, x, data=None):
    """Calculate arbitrary domain to laser intensity conversion.

	inputs:
		pars: line fit parameter dictionary
		x: arbitray domain

	outputs:
		c: laser intensity curve
	"""
    vals = pars.valuesdict()
    p = 0.0
    backOrder = -1
    for val in vals.keys():
        if "back" in val:
            backOrder += 1
    for i in range(backOrder + 1):
        #if i == 1:
        p += vals["back_c" + str(i)] * np.power(1.0 * x, i * 1.0)
        #else:
        #    p += vals["back_c1"]*vals["back_c" + str(i)] * np.power(1.0 * x, i * 1.0)
    if data is None:
        return p
    return p - data


def loadTIPSTable(mol=1, iso=1):
    """Load TIPS table for specific molecule.

	inputs:
		mol: molecular number
		iso: isotopologue number

	outputs:
		QTdict: dictionary of TIPS value with
			temperature (K) as the key.
	"""
    file = "./QTpy/" + str(mol) + "_" + str(iso) + ".QTpy"
    with open(file, "rb") as handle:
        tips = pickle.loads(handle.read())
    return tips


def TIPStemp(T, tips):
    """TIPS temperature interpolation.
	Linear interpolation of TIPS value
		between two integer temperatures.

	inputs:
		T: temperature in kelvin
		QTdict: Dictionary to interpolate from

	outputs:
		TIPS value
	"""

    if tips is None:
        return 1
    if T == int(T):
        return float(tips[str(int(T))])
    else:
        Q1 = float(tips[str(int(T))])
        Q2 = float(tips[str(int(T + 1))])
        return Q1 + (Q2 - Q1) * (T - int(T))


def loadHitranKeys():
    """Read in molecular isotope reference data.

	Includes molecular id, isotope id, plain text,
		English name, Formula, AFGL Code, Abundance,
		concentration (ppmv for primary isotope
		and permil for various isotopes),
		molecular mass, inclusion bool.

	inputs: None
	outputs: nested dictioanry containing molecular info
		based on molid_isoid, with nested keys from above.
	outputs: array containing reference parameters
	"""
    fileName = "./config/hitranKeys.csv"
    molecularInfoDict = {}
    df = pd.read_csv(fileName)
    for index, (mol, iso) in enumerate(zip(df["mol"], df["iso"])):
        molkey = str(mol) + "_" + str(iso)
        molecularInfoDict[molkey] = {}
        for key in df.dtypes.index:
            molecularInfoDict[molkey][key] = df[key][index]

    for key in molecularInfoDict.keys():
        mol = molecularInfoDict[key]["mol"]
        iso = molecularInfoDict[key]["iso"]
        try:
            molecularInfoDict[key]["tips"] = loadTIPSTable(mol, iso)
        except:
            molecularInfoDict[key]["tips"] = None

    # with open(fileName, mode = 'r') as infile:
    # 	reader = csv.reader(infile)
    # 	masterHitranKeys = {rows[0]+' '+rows[1]: rows[:] for rows in reader}
    # 	return masterHitranKeys

    return molecularInfoDict


def readHitran(molecularInfoDict, lines=[], cutoffOrder=1e10, magCutoffSlope=5.0):
    """Reads and filters HITRAN data.

	Inputs:
		masterHitranKeys: Reference parameter table
		lines: 2 element array containing wavenumber extents of critical window
		cutoffOrder: Ratio of largest line in window to smallest line before rejection
		magCutoffSlope: The slope at which the minimum cutoff rises every critical
			window width from the center of the critical window.

	outputs: Returns table containing the filtered hitran lines with molecular mass merged.
	"""
    # Read the reduced hitran file containing subset to minimize process time. May use full file but beware of memory.
    with open("./config/1365-1395.csv", "r") as csvFile:  # 01_hit16.par','r') as csvFile:
        spamreader = csv.reader(csvFile, delimiter=",")
        for i, row in enumerate(spamreader):
            if i == 0:
                continue
            try:
                tmprow = np.array([float(x) for x in row])
            except:
                continue
            try:
                hitranArr = np.c_[hitranArr, tmprow]
            except:
                hitranArr = np.c_[tmprow]

    # used to remove the duplicate starter lines used for estimating window size
    numlines = len(hitranArr[0, :])

    # Load hitran data file.
    hitranArr = np.transpose(hitranArr)

    # Precondition parameter matrix
    molMass = np.zeros(len(hitranArr[:, 0]), dtype="float")  # self.hitranPars[:,0]))

    # This number should correspond to an array with isotopes that are allowed to float along an "adjusted ppmv".
    # If the iso number is not in the list, it is asserted to the primary isotope (11)
    isoVary = np.unique(hitranArr[:, 1])  # self.hitranPars[:,1])
    isoVary = np.sort(isoVary)

    # if len(isoVary) > 2: isoVary = isoVary[:2]
    # if len(isoVary) > 1: isoVary = isoVary[:1]

    # Configure mixing ratios associated with individual isotopes
    ppmvNum = np.zeros(len(molMass), dtype="int")
    for isoInc, iso in enumerate(isoVary):
        if iso in hitranArr[:, 1]:
            ppmvNum[np.where(hitranArr[:, 1] == iso)] = isoInc
            # ppmvNum[hitranArr[:,1] == iso] = isoInc

    # Configure hitran parameters array
    hitranTable = np.c_[molMass]
    for i in range(0, 10):
        hitranTable = np.c_[hitranTable, hitranArr[:, i]]
    hitranTable = np.c_[hitranTable, ppmvNum]

    for i in range(len(hitranTable[:, 0])):
        mol = str(int(hitranTable[i, 1]))
        iso = str(int(hitranTable[i, 2]))
        hitranTable[i, 0] = molecularInfoDict[mol + "_" + iso]["molmass"]
        # hitranTable[i,0] = masterHitranKeys[str(int(hitranTable[i,1]))+' '+str(int(hitranTable[i,2]))][9]
        # hitranTable[i,0] = molecularInfoDict[str(int(hitranTable[i,1]))+' '+str(int(hitranTable[i,2]))][9]

    # Now filter the table based on cushion and roll off filter

    # Find center of window
    windowCenter = (max(lines) - min(lines)) / 2.0 + min(lines)
    # Double window as the official range!
    windowHW = np.abs(max(lines) - min(lines)) * 2.0

    # Find the maximum intensity line within the window
    windowMax = np.max(
        hitranTable[
            (hitranTable[:, 3] > (windowCenter - windowHW))
            * (hitranTable[:, 3] < (windowCenter + windowHW)),
            4,
        ]
    )
    # use cushion to determine what the minimum perceivable lines in window are
    windowMin = windowMax / cutoffOrder
    # windowMin = cushion#5e15

    mask = np.ones(numlines)

    for i in range(numlines):
        # Check distance of line to center of window
        distance = np.abs(hitranTable[i, 3] - windowCenter)
        # If distance within allowable range, make sure greater than minimum
        if distance < windowHW:
            if hitranTable[i, 4] < windowMin:
                mask[i] = 0
        else:
            # If outside of window, use rolloff slope based on # of window HW's
            #   outside of range. Allowable minimum increases further from window
            if hitranTable[i, 4] < (
                np.abs(distance - windowHW) / (windowHW)
            ) * magCutoffSlope * (windowMin):
                mask[i] = 0

    hitranTable = hitranTable[np.where(mask)[0], :]
    numlines = len(hitranTable[:, 0])  # wavelength)

    return hitranTable
