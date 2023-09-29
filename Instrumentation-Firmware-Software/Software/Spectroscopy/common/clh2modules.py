###CLH2 Modules###


def lineint(
    self, scans, numDark, plotscans, fitlen, press, celltemp, figdir, saturatedVoltage
):
    """Old processing module.

	Processing module

	inputs:
		scans: matrix containing scans
		numDark: Number of bits devoted to background measurement
		plotScans: bool to determine if scans are plotted
		fitlen: # of bits on either end of spectrum to use for background
		press: array of pressures
		cellTemp: array of cell temperatures
		figdir: directory where figures are saved to
		saturatedVoltage: Voltage threshold to use for signal saturation indicator
	"""

    dims = scans.shape
    obs = dims[0]
    scanpts = dims[1]

    x = np.arange(scanpts)
    # powerzero = np.mean(scans[:,2:numDark+1],1)
    powerzero = np.nanmean(scans[:, 2 : 45 - 5], 1)  # numDark+1],1)

    lower1 = numDark
    lower2 = numDark + fitlen
    upper1 = round(scanpts - fitlen * 0.75)
    upper2 = scanpts - 1

    intvmr = np.arange(float(obs))
    centerindex = np.arange(obs)
    vscan = np.arange(scanpts)

    ims = []
    self.figure.clear()

    nullSpectra = np.zeros(len(x[lower1:upper2]), dtype="float")
    ax = self.figure.add_subplot(111)

    # line1, line2, line3, line4, line5, line6, line7, = ax.plot(x[lower1:upper2],nullSpectra,'k',x[lower1:upper2],nullSpectra,'r',
    # 	x[lower1:upper2],nullSpectra,'b',x[lower1:upper2],nullSpectra,'y',
    # 	x[lower1:upper2],nullSpectra,'g',x[lower1:upper2],nullSpectra,'m',
    # 	x[lower1:upper2],nullSpectra,'c')
    line1, line2, line4 = ax.plot(
        x[lower1:upper2],
        nullSpectra,
        "k",
        x[lower1:upper2],
        nullSpectra,
        "r",
        x[lower1:upper2],
        nullSpectra,
        "y",
    )
    ax2 = ax.twinx()

    line3, = ax2.plot(x[lower1:upper2], nullSpectra, "b")

    self.progress.setRange(0, obs - 1)
    self.progress.setValue(0)

    try:
        plotDivisions = int(self.plotDivisions.text())
    except:
        plotDivisions = 100
        self.plotDivisions.setText("100")
    if plotDivisions > obs:
        plotDivisions = obs
        self.plotDivisions.setText(str(round(obs)))

    originalUpper2 = upper2
    originalUpper1 = upper1
    for i in range(obs):
        if self.closeTrigger:
            return
        upper2 = originalUpper2
        upper1 = originalUpper1

        while (
            np.abs(scans[i, upper2] > saturatedVoltage)
            and upper2 > upper1 + 10
            and np.abs(scans[i, upper2]) <= np.abs(scans[i, upper2 - 1])
        ):
            upper2 -= 1
        if scans[i, upper2] > saturatedVoltage:
            while np.abs(scans[i, upper2]) > saturatedVoltage and upper1 > 300:
                upper1 -= 1
                upper2 -= 1

        if self.newFmt:
            upper2 = originalUpper2
            upper1 = originalUpper1

        # if upper1 != originalUpper1:
        # 	print(upper1)

        # print(upper2)

        scanact = -np.abs((scans[i, :]) - powerzero[i])
        if self.newFmt:
            scanact = -np.abs(scans[i, :])
        yarr = np.r_[scanact[lower1 : lower2 + 1], scanact[upper1 : upper2 + 1]]
        xarr = np.r_[x[lower1 : lower2 + 1], x[upper1 : upper2 + 1]]
        fitout = np.polyfit(xarr, yarr, 3)
        # fitline = fitout[3] + fitout[2]*x + fitout[1]*x**2 + fitout[0]*x**3
        fitline = (
            fitout[3] + fitout[2] * x + fitout[1] * pow(x, 2.0) + fitout[0] * pow(x, 3.0)
        )
        scanfit = scanact - fitline
        # valid = [i for i, val in enumerate(x) if val > lower1]

        valid = np.where(x > lower1)
        # print(valid)

        maxindex = np.argmin(scanfit[valid])

        # maxindex+=lower1
        power = fitline[maxindex]
        powervo = scanact[maxindex]
        scanscale = scanact / fitline

        # Code for plotting various data
        centerindex[i] = maxindex + lower1 + 1

        try:
            intvmr[i] = np.trapz(1.0 - scanscale[valid], x=vscan[valid])
        except:
            intvmr[i] = -9999

        if i % int(np.floor(obs / plotDivisions)) == 0:  # or intvmr[i]>100:
            scaling = np.max(
                np.r_[np.abs(scanact[lower1:upper2]), np.abs(fitline[lower1:upper2])]
            ) / max(1.0 - scanscale[lower1:upper2])

            # line1.set_ydata(self.spectralModel(out.params,x[left:-right]))
            line1.set_ydata(np.abs(scanact[lower1:upper2]))
            line1.set_xdata(x[lower1:upper2])
            ax.set_title("Raw Spectra")
            ax.set_xlabel("Bit #")
            ax.set_ylabel("Voltage (V)")

            line2.set_ydata(-fitline[lower1:upper2])
            line2.set_xdata(x[lower1:upper2])

            line4.set_ydata(
                np.abs(scans[i, lower1:originalUpper2])
            )  # -scanact[lower1:upper2])
            line4.set_xdata(x[lower1:originalUpper2])

            # ax2 = ax.twinx()

            line3.set_ydata((1.0 - scanscale[lower1:upper2]))  # *scaling)
            line3.set_xdata(x[lower1:upper2])
            ax2.set_ylabel("Absorption")
            # line3.set_ydata(np.abs(scans[i,upper1:]))#*scaling)
            # line3.set_xdata(np.arange(len(scans[i,upper1:]))*512.0/len(scans[i,upper1:]))
            # ax2.set_ylabel('Absorption')

            # line4.set_ydata(scaling * self.spectralModel(out.params,self.domShift(out.params,x[left:-right]),True,0))

            # if numlines > 1: line5.set_ydata(scaling * self.spectralModel(out.params,self.domShift(out.params,x[left:-right]),True,1))

            ax.relim()
            ax.autoscale_view()
            ax2.relim()
            ax2.autoscale_view()

            # Uncomment for saving animation
            # ims.append([line1])
            # if numlines == 1: ims.append([line1,line2,line3,line4])

            # ax.draw_artist(ax.patch)
            # ax.draw_artist(line)
            # ax2.draw_artist(ax2.patch)
            # ax2.draw_artist()

            # self.canvas.update()
            # self.canvas.flush_events()

            self.canvas.draw()
            self.processEvents()

        self.progress.setValue(i)
        # time.sleep(1)

    powermax = (-1) * np.min(scans, 1)
    # print(powermax.shape)
    # March 2013 cal
    # fitted = np.array([-8.0605e3, -7.1624e0, -7.0584e3, -6.3956e0, -9.0851e-2, 1.0054e-1, 2.4235e-4])

    # October cal1
    # fitted = np.array([1.78e11, 8.15e10, -1.3e7, 9.2e7, -9.93e5, 1.0e6, -3.04e3])
    # October cal2
    # fitted = np.array([9e11, 8.15e10, -1.3e7, 9.2e7, -9.93e5, 1.0e6, -3.04e3])

    # Commented out prior to SOCRATES
    fitted = np.array(
        [
            9.9882e4,
            -6.3415e3,
            2.113e3,
            1.3178e1,
            -6.0409e-2,
            6.2395e-2,
            1.6877e-4,
            -1.04886e5,
        ]
    )

    VMR = (
        (fitted[0] + fitted[1] * press + fitted[2] * intvmr + fitted[3] * press * intvmr)
        / (1 + fitted[4] * press + fitted[5] * intvmr + fitted[6] * press * intvmr)
        + fitted[7]
    )
    # VMR = (fitted[0]+fitted[1]*press + fitted[2]*intvmr + fitted[3]*press*intvmr)/(1+fitted[4]*press + fitted[5]*intvmr + fitted[6]*press*intvmr)

    # powerzero = np.mean(scans[:,4:35],1)
    # print(powerzero.shape)

    ints = {
        "dark": powerzero,
        "int": intvmr,
        "VMR": VMR,
        "powermax": powermax,
        "centerindex": centerindex,
    }
    ints_desc = copy.deepcopy(ints)
    ints_desc["dark"] = "Measure of unpowered laser intensity"
    ints_desc["VMR"] = "Volume mixing ratio (ppmv)"
    ints_desc["int"] = "Raw integral of normalized spectra"
    ints_desc["powermax"] = "Highest laser intensity"
    ints_desc["centerindex"] = "Line Center Index"

    return [ints, ints_desc]
