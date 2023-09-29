from common.libraryImports import *
from common.ui_init import *

plt.style.use("dark_background")


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress
    """

    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs["progress_callback"] = self.signals.progress

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class Ui_MainWindow(QWidget):
    def __init__(self, parent=None):
        """Class initializer"""
        super(Ui_MainWindow, self).__init__(parent)
        self.title = "PyQt5 file dialogs"
        # self.left = 20
        # self.top = 50
        # self.width = 960 * 1.8
        # self.height = 540 * 1.7
        initUI(self)

    def zoomFunction(self, event=[]):
        """Zoom Function

    	When scroll or zoom is applied to plot, this slot will catch the action
        and zoom in/out using a 2x multiplier

    	inputs:
    		event: pulls the event locations (where your mouse was on the plot

    	outpus: None
    	"""

        # print("bye", event)
        # self.figure.canvas.blockSignals(True)
        # self.setUpdatesEnabled(False)
        # get the current x and y limits
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        cur_xrange = (cur_xlim[1] - cur_xlim[0]) * 0.5
        cur_yrange = (cur_ylim[1] - cur_ylim[0]) * 0.5
        # xdata = event.xdata  # get event x location
        # ydata = event.ydata  # get event y location

        m_x, m_y = event.x, event.y
        # ax = self.figure.subplots()
        xZoom, yZoom = self.ax.transData.inverted().transform([m_x, m_y])

        if event.button == "up":
            # deal with zoom in
            scale_factor = 1 / 2  # base_scale
        elif event.button == "down":
            # deal with zoom out
            scale_factor = 2  # base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1

        x = self.time
        y = self.data["binCenter"]
        # set new limits
        xMax = xZoom + cur_xrange * scale_factor
        xMin = xZoom - cur_xrange * scale_factor
        yMax = cur_ylim[1]  # max(y)  # yZoom + cur_yrange * scale_factor
        yMin = cur_ylim[0]  # min(y)  # yZoom - cur_yrange * scale_factor
        if xMax > max(x):
            xMax = max(x)
        if xMin < min(x):
            xMin = min(x)
        self.ax.set_xlim([xMin, xMax])

        if scale_factor > 1:
            yMax = max(y)
            yMin = min(y)
            # if yMax > max(y):
            #    yMax = max(y)
            # if yMin < min(y):
            #    yMin = min(y)
            self.ax.set_ylim([yMin, yMax])

        self.processReanalysis(
            xLoc=xZoom, yLoc=yZoom, xLims=[xMin, xMax], yLims=[yMin, yMax]
        )

        self.resizeEvent()
        self.canvas.draw()  # force re-draw
        # self.figure.canvas.flush_events()  # app.processEvents()

        # Now, once we are in the new zoom range, check to see if an averaged histogram
        #   option exists for second plot, if not, create, and populate. also
        #   check for combination
        # self.plotClick(False)

        # self.setUpdatesEnabled(True)
        # self.figure.canvas.blockSignals(False)

    def processReanalysis(self, xLoc=None, yLoc=None, xLims=None, yLims=None):
        """ Process reanalysis

        Reprocesses data absed on limits of graph and where was last clicked....
        """

        # Checks whether clicked or zoomed, value of 0 is to do everything regardless
        # clickOrZoom = 0
        x = np.array(self.time)  # data[self.dataNames[2]]
        y = np.array(self.data["binCenter"])

        # else:
        #    xLims = [np.nanmin(x), np.nanmax(x)]
        #    yLims = [np.nanmin(y), np.nanmax(y)]
        #    clickOrZoom = 2  # return

        # self.reanalysis dict is the dictionary containing self.histFigKeys
        Z = copy.deepcopy(
            self.data[self.dataNames[0]]
        )  # self.figMenu.currentIndex()]])#self.figMenu.currentIndex()]])
        M = copy.deepcopy(self.data[self.dataNames[1]])
        # X, Y = np.meshgrid(self.data[self.dataNames[1]], self.data['binCenter'])

        Z[Z < 0] = np.nan
        M[M < 0] = np.nan

        x1 = self.data["leftBin"]
        x2 = self.data["rightBin"]
        w = x2 - x1

        try:
            xMatchIndex = np.nanargmin(np.abs(x - xLoc))
            yMatchIndex = np.nanargmin(np.abs(y - yLoc))
        except:
            pass

        xMatchMin = np.nanargmin(np.abs(x - xLims[0]))
        xMatchMax = np.nanargmin(np.abs(x - xLims[1])) + 1

        yMatchMin = np.nanargmin(np.abs(y - yLims[0]))
        yMatchMax = np.nanargmin(np.abs(y - yLims[1])) + 1

        self.xMatchIndices = [xMatchMin, xMatchMax]
        self.yMatchIndices = [yMatchMin, yMatchMax]

        timeRange = str(int(xLims[0])) + "-" + str(int(xLims[1]))

        for i, key in enumerate(self.histFigKeys):
            if i < 4:
                self.reanalysisDict[key]["domain"] = y
                self.reanalysisDict[key]["xlabel"] = "Bin Center (nm)"
            else:
                self.reanalysisDict[key]["domain"] = x[xMatchMin:xMatchMax]
                self.reanalysisDict[key]["xlabel"] = "Time (s)"

        for i, key in enumerate(self.histFigKeys):
            # if i in [2, 3] and clickOrZoom == 1:
            #    continue
            # if i in [0, 1] and clickOrZoom == 2:
            #    continue
            if i == 0:
                self.reanalysisDict[key]["range"] = Z[:, xMatchIndex]
                self.reanalysisDict[key][
                    "title"
                ] = "Histogram (dN/dLogD) at Time: " + str(int(xLoc))
            elif i == 1:
                self.reanalysisDict[key]["range"] = M[:, xMatchIndex]
                self.reanalysisDict[key][
                    "title"
                ] = "Histogram (dM/dLogD) at Time: " + str(int(xLoc))
            elif i == 2:
                self.reanalysisDict[key]["title"] = (
                    "Histograms in time range: " + timeRange
                )
                self.reanalysisDict[key]["ylabel"] = "dN/dLogD"
                # Reduce range to be a 2d array
                self.reanalysisDict[key]["domain"] = np.transpose(
                    np.array([list(y)] * (xMatchMax - xMatchMin))
                )
                self.reanalysisDict[key]["range"] = Z[:, xMatchMin:xMatchMax]
            elif i == 3:
                self.reanalysisDict[key]["title"] = (
                    "Histogram Average in time range: " + timeRange
                )
                self.reanalysisDict[key]["ylabel"] = "dN/dLogD"
                self.reanalysisDict[key]["range"] = np.nanmean(
                    Z[:, xMatchMin:xMatchMax], axis=1
                )
            elif i == 4:
                # Number concentration at selected bin
                z = Z[yMatchIndex, xMatchMin:xMatchMax]
                self.reanalysisDict[key]["range"] = z
                self.reanalysisDict[key]["title"] = (
                    "Number conc at bin: "
                    + str(int(yLoc))
                    + " in time range: "
                    + timeRange
                )
                self.reanalysisDict[key]["ylabel"] = "Peak Size (nm)"
            elif i == 5:
                # Mass at selected bin
                z = M[yMatchIndex, xMatchMin:xMatchMax]
                self.reanalysisDict[key]["range"] = z
                self.reanalysisDict[key]["title"] = (
                    "Mass conc at bin: " + str(int(yLoc)) + " in time range: " + timeRange
                )
                self.reanalysisDict[key]["ylabel"] = "Peak Size (nm)"
            elif i == 6:
                # Average Concentration vs Time
                z = np.nanmean(Z[:, xMatchMin:xMatchMax], axis=0)
                self.reanalysisDict[key]["range"] = z
                self.reanalysisDict[key]["title"] = (
                    "Average # conc in time range: " + timeRange
                )
                self.reanalysisDict[key]["ylabel"] = "Average dN/dlogD"
            elif i == 7:
                # Average Mass vs Time
                z = np.nanmean(M[:, xMatchMin:xMatchMax], axis=0)
                self.reanalysisDict[key]["range"] = z
                self.reanalysisDict[key]["title"] = (
                    "Average mass conc in time range: " + timeRange
                )
                self.reanalysisDict[key]["ylabel"] = "Average dM/dlogD"
            elif i == 8:
                # Peak size from data
                z = Z[0, :]
                z[:] = np.nan
                for i, val in enumerate(x):
                    z[i] = y[np.argmax(Z[:, i])]
                self.reanalysisDict[key]["range"] = z[xMatchMin:xMatchMax]
                self.reanalysisDict[key]["title"] = (
                    "Peak Size in time range: " + timeRange
                )
                self.reanalysisDict[key]["ylabel"] = "Peak Size (nm)"
            elif i == 9:
                # Peak value from data
                z = Z[0, :]
                z[:] = np.nan
                for i, val in enumerate(x):
                    z[i] = np.nanmax(Z[:, i])
                self.reanalysisDict[key]["range"] = z[xMatchMin:xMatchMax]
                # ax.set_title("Peak Value vs Time")
                self.reanalysisDict[key]["title"] = (
                    "Peak Value in time range: " + timeRange
                )
                self.reanalysisDict[key]["ylabel"] = "Peak Value (counts)"
            elif i == 10:
                # Summed N from raw data
                # z = Z[0, xMatchMin:xMatchMax]
                z = np.nansum(self.rawHist[0, xMatchMin:xMatchMax], axis=0)
                self.reanalysisDict[key]["range"] = z
                self.reanalysisDict[key]["title"] = (
                    "Summed counts (all bins): " + timeRange
                )
                self.reanalysisDict[key]["ylabel"] = "N (total)"
            elif i == 11:
                # Summed dN/dlogD (bins 1 - 33)
                z = np.nansum(Z[0:33, xMatchMin:xMatchMax], axis=0)
                self.reanalysisDict[key]["range"] = z
                self.reanalysisDict[key]["title"] = (
                    "Summed dN/dlogD (bins 1-33): " + timeRange
                )
                self.reanalysisDict[key]["ylabel"] = "n"
            elif i == 12:
                # Summed dN/dlogD (bins 34 - 66)
                z = np.nansum(Z[33:66, xMatchMin:xMatchMax], axis=0)
                self.reanalysisDict[key]["range"] = z
                self.reanalysisDict[key]["title"] = (
                    "Number Density (bins 34-66): " + timeRange
                )
                self.reanalysisDict[key]["ylabel"] = "n"
            elif i == 13:
                # Summed dN/dlogD (bins 67 - 99)
                z = np.nansum(Z[66:, xMatchMin:xMatchMax], axis=0)
                self.reanalysisDict[key]["range"] = z
                self.reanalysisDict[key]["title"] = (
                    "Number Density (bins 66-99): " + timeRange
                )
                self.reanalysisDict[key]["ylabel"] = "n"
            elif i == 14:
                # Summed dN/dlogD (all bins)
                z = np.nansum(Z[:, xMatchMin:xMatchMax], axis=0)
                self.reanalysisDict[key]["range"] = z
                self.reanalysisDict[key]["title"] = (
                    "Number Density (all bins): " + timeRange
                )
                self.reanalysisDict[key]["ylabel"] = "n"
            elif i == 15:
                # Volume density summed
                z = np.nansum(M[:, xMatchMin:xMatchMax], axis=0)
                # z[:] = np.nan
                self.reanalysisDict[key]["range"] = z
                self.reanalysisDict[key]["title"] = (
                    "Volume Density (all bins): " + timeRange
                )
                self.reanalysisDict[key]["ylabel"] = "v"
            else:
                z = Z[0, xMatchMin:xMatchMax]
                self.reanalysisDict[key]["range"] = z
                self.reanalysisDict[key]["title"] = "unimplemented"
                self.reanalysisDict[key]["ylabel"] = "unimplemented"

        """
        The variables that are worth having in a "reduced data" file are:
        Date, Time, Mode, Sample flow, Temp, Pres, N(tot), n(1-33), n(34-66), n(67-99), n, v, useful fit parameters...
        Mode = inlet (CVI, Total, SDI)
        N(tot) is particle counts summed over 99 bins
        n(1-33) is number density (i.e., number of particles divided by the flow rate) in first 33 bins
        n(34-66) is number density in second 33 bins
        n(67-99) is number density in third 33 bins
        n is total number density, and is probably the same value as CVIU, or whatever is currently in the exchange files for the CVI.
        v is volume density (in microns^3 per cm^3) for full 99 bins
        we can iterate 'useful fit parameters' based on a looking at a few flights, but I'm guessing:
        D1(max) is diameter at maximum number in the first gaussian mode based on fits
        D2(max) is the diameter at maximum number in the second gaussian mode based on fits
        D3 (if there is a third mode - strike if not)
        Just a heads' up here. We may need to merge some other quantities into this file. The most useful will be CVFX3 (which is important for residence time in the sample lines (i.e., delay times) and a suitable measurement of H2O to deal with RH. RH is problematic - it's the TDL when we are sampling on the CVI line, and it's ambient H2O when we are sampling on the SDI. So we'll want to think this through. Maybe we include both.
        """

        # Start going through each reanalysss parameter and adjust accordingly...

        # self.reanalysisDict[self.histFigKeys[0]]

    def plotClick(self, event=[]):
        """Click Function

    	When you click on a time trace plot, this will receive the x (and y) coordinate
        that was clicked on and provide reanalysis (histograms, etc.) at that value.

    	inputs:
    		event: pulls the event locations (where your mouse was on the plot

    	outpus: None
    	"""
        self.fitOutput.setFocus()
        # print("hi", event)
        # if event == []:
        #    return

        # print("hi", event)

        if not event or event == []:
            try:
                xClick = self.xClick
                yClick = self.yClick
                # return
            except:
                return
        else:
            try:
                m_x, m_y = event.x, event.y
                # ax = self.figure.subplots()
                xClick, yClick = self.ax.transData.inverted().transform(
                    [event.x, event.y]
                )
            except:
                xClick = self.ax.get_xlim()[0]
                yClick = self.ax.get_ylim()[0]

        x_lim = self.ax.get_xlim()
        y_lim = self.ax.get_ylim()
        if xClick > x_lim[1]:
            xClick = x_lim[1]
        elif xClick < x_lim[0]:
            xClick = x_lim[0]
        if yClick > y_lim[1]:
            yClick = y_lim[1]
        elif yClick < y_lim[0]:
            yClick = y_lim[0]

        # Store saved click state from earlier runs
        self.xClick = xClick
        self.yClick = yClick

        # if event != None:
        #    self.processReanalysis(xClick, yClick, x_lim, y_lim)
        # return
        self.processReanalysis(xLoc=xClick, yLoc=yClick, xLims=x_lim, yLims=y_lim)

        if self.figMenu.currentIndex() > 1:
            return

        histFigChoice = self.histFigMenu.currentIndex()
        reanalysisOption = self.reanalysisDict[self.histFigKeys[histFigChoice]]

        if histFigChoice == 2 and (self.xMatchIndices[1] - self.xMatchIndices[0]) > 1000:
            result = QMessageBox.warning(
                MainWindow,
                "WARNING",
                "Quite a lot of data for this option, would you like to continue? If not, consider zooming",
                QMessageBox.Yes,
                QMessageBox.No,
            )

            if result == QMessageBox.No:
                return

        # self.histFigure.clear()
        # self.histax = self.histFigure.subplots()
        self.histax.clear()

        self.histax.set_title(reanalysisOption["title"], fontsize=9, fontweight="bold")
        self.histax.set_xlabel(reanalysisOption["xlabel"], fontsize=8, fontweight="bold")
        self.histax.set_ylabel(reanalysisOption["ylabel"], fontsize=8, fontweight="bold")

        if histFigChoice < 4:
            self.histax.set_yscale("log")
            self.histax.set_xscale("log")
            self.histax.set_aspect("auto")

        try:
            self.histax.plot(reanalysisOption["domain"], reanalysisOption["range"])
        except:
            pass
        """
        elif histFigChoice == 2:
            # Need match index information
            for index in np.arange(matchMin, matchMax + 1):  # Z[matchMin:matchMax, :]:
                if np.sum(Z[:, index]) == 0 or (Z[:, index] < 0).any():
                    continue
                ax.plot(c, Z[:, index], linewidth=1)

            # Question, do I want to fit here as well?
        """
        if histFigChoice == 1:
            reanalysisOption = self.reanalysisDict[self.histFigKeys[0]]
        if histFigChoice == 0 or histFigChoice == 1 or histFigChoice == 3:
            try:
                fitx = reanalysisOption["domain"]
                fity = reanalysisOption["range"]
                fitx = fitx[~np.isnan(fity)]
                fity = fity[~np.isnan(fity)]

                numModes = self.numModes.value()
                varyOffset = self.varyOffset.isChecked()
                fitMin = self.fitMin.value()
                fitMax = self.fitMax.value()

                fity = fity[(fitx >= fitMin) * (fitx <= fitMax)]
                fitx = fitx[(fitx >= fitMin) * (fitx <= fitMax)]
                # print(fitx, fity)
                out = self.fitWrapper(
                    fitx, fity, numModes=numModes, varyOffset=varyOffset
                )

                outReport = pprint.pformat(fit_report(out))
                self.fitOutput.setPlainText(outReport)

                # print(fit_report(out.params))
                fitResult = self.pdf(out.params, reanalysisOption["domain"])

                if histFigChoice == 1:
                    fitResult = self.convertdN2dM(fitResult, reanalysisOption["domain"])

                self.histax.plot(
                    (reanalysisOption["domain"]), fitResult, "b-", lw=5, alpha=0.6
                )

                if histFigChoice == 3:
                    # Then save the parameters to new spectra
                    reanalysisOption["fit"] = fitResult
                    fitLabel = "Fit_"
                    for key in out.params.keys():
                        fitLabel += (
                            str(key) + ": " + "{:.3f}".format(out.params[key].value) + "_"
                        )
                    reanalysisOption["fit_label"] = fitLabel

            except Exception as e:
                print(e)
        # elif histFigChoice == 4:

        self.histax.autoscale()
        self.histax.relim()

        self.resizeEvent()
        # ax.autoscale()
        # self.histFigure.tight_layout(pad=0, w_pad=0, h_pad=0)

        # Have to call twice to avoid gradually shrinking plot
        self.histCanvas.draw()

        # self.resizeEvent()

        app.processEvents()

    def fitToAllData(self, t, y, Z, numModes, progress_callback):
        # return
        obs = len(Z[0, :])

        # Read in configuration file to determine full file fit parameters
        # Create fit dict based on keys
        fitDict = {}
        pars = self.parsInit(numModes)
        for key in pars:
            fitDict[key] = []
            pars[key].set(value=np.nan)

        for i in range(obs):
            z = Z[:, i]
            x = y[~np.isnan(z)]
            z = z[~np.isnan(z)]
            try:
                if np.nansum(z) < 20:
                    raise
                out = self.fitWrapper(x, z, numModes=1).params
            except:
                out = pars

            for key in out.keys():
                fitDict[key].append(out[key].value)

            # if i % 100 == 0:
            if int(i * 100 / obs) != 100:
                progress_callback.emit(i * 100 / obs)
            time.sleep(0.01)

        # Cannot run this line yet until the dictionary transfers
        # progress_callback.emit(100)
        return fitDict

    def parsInit(self, numModes=1):
        pars = Parameters()
        modeGuess = [0, 0, 1e-10]

        for i in range(numModes):
            pars.add(
                "amp_m" + str(int(i)), value=modeGuess[0], vary=True, min=0
            )  # , max = backMaxs[i], min = backMins[i])#, value = backArr[i])#plsq[i])
            pars.add("mu_m" + str(int(i)), value=modeGuess[1], vary=True)
            pars.add(
                "sig_m" + str(int(i)), value=modeGuess[2], vary=True, min=1e-10
            )  # 1e-5)

        pars.add("offset", value=0.0, vary=False)

        """
        if numModes == 2:
            pars.add("amp1", value=z[0], vary=True, min=0)
            pars.add("mu1", value=0, vary=True, min=0)
            pars.add("sig1", value=1.0, vary=True, min=1e-3)
        """

        return pars

    def fitWrapper(self, y, z, numModes=1, varyOffset=False):

        y = y[~np.isnan(z)]
        z = z[~np.isnan(z)]

        pars = self.parsInit(numModes=numModes)

        try:
            modeGuess = np.array([np.max(z) * 2.0, y[np.argmax(z)], 1.0])
        except:
            modeGuess = [0.0, 0.0, 1e-10]

        pars["amp_m0"].set(value=modeGuess[0], vary=True)
        # , min=0  # , max = backMaxs[i], min = backMins[i])#, value = backArr[i])#plsq[i])
        pars["mu_m0"].set(value=modeGuess[1], vary=True)
        pars["sig_m0"].set(value=modeGuess[2], vary=True, min=1e-10)  # 1e-5)

        if numModes > 1:
            pars["amp_m1"].set(value=1.0)  # z[0])
            pars["mu_m1"].set(value=y[0])
            pars["sig_m1"].set(value=1.0)
        if numModes > 2:
            pars["amp_m2"].set(value=1.0)  # z[-1])
            pars["mu_m2"].set(value=y[-1])
            pars["sig_m2"].set(value=1.0)

        if varyOffset:
            pars["offset"].set(value=0, vary=True)  # , min = 0.0)
        else:
            pars["offset"].set(value=0, vary=False)

        # for i in range(numModes):
        # print(sum_ys)
        # pars.add('amp0', value = sum_ys * np.max(z) / 500.0, vary = True, min = 0)#, max = backMaxs[i], min = backMins[i])#, value = backArr[i])#plsq[i])
        # print(pars, y, z, numModes)

        out = minimize(
            self.pdf,
            pars,
            args=(y[:],),
            kws={"data": z[:], "numModes": numModes},
            scale_covar=True,
            nan_policy="omit",
        )  # , method = 'trust-constr')#'trust-exact')#, reduce_fcn = 'None')

        return out

    def pdf(self, pars, x, data=None, numModes=1):
        """Probability Density Function

    	Model format for fitting to histogram data

    	inputs:
    		pars: model parameter dictionary for fitting
            x: domain
            data: Used to compute residuals from raw data
            modes: determines how many modes are to be fit

    	outpus: Model output OR residual
    	"""
        vals = pars.valuesdict()
        offset = vals["offset"]

        try:
            model = np.zeros(len(x), dtype="float")
        except:
            model = 0
        for i in range(numModes):
            amp = vals["amp_m" + str(i)]
            sig = vals["sig_m" + str(i)]
            mu = np.log(vals["mu_m" + str(i)])

            # model += 1.0*amp/(x*sig*np.sqrt(2.0*np.pi))\
            # 	*np.exp(-pow((np.log(x) - mu),2.0)/\
            # 	(2.0*pow(sig,2.0)))

            # Removing the division by x in the prefix makes
            # A lOT more sense but needs to be documented.
            model += (
                1.0
                * amp
                / (sig * np.sqrt(2.0 * np.pi))
                * np.exp(-pow((np.log(x) - mu), 2.0) / (2.0 * pow(sig, 2.0)))
            )  # + offset

            # Mode for normal (non-log) distribution
            # model += 1.0*amp/(sig*2*np.pi) \
            # 	*np.exp(-pow((x - mu),2.0)/\
            # 	(2.0*pow(sig,2.0)))

        model += offset

        if data is None:
            return model
        return model - data

    # def pdf(self, x, loc, scale):
    # 	return stats.gaussian.pdf(x,loc,scale)

    def saveData(self):
        """Data Saving Function

    	Used to save subset data, reanalysis data, window averaging data, ict, etc.

    	inputs:
    		saveOption: Denotes which save option to use as passed by signal

    	outpus: None
    	"""

        # button = self.sender()
        # if isinstance(button, QPushButton):
        #    self.label.setText("You pressed %s!" % button.text())

        try:
            # filePath = os.path.dirname(os.path.abspath(self.dataFile))
            filePath, fileName = os.path.split(os.path.abspath(self.dataFile))
        except:
            return

        saveFits = False

        sender = self.sender().text()
        if sender == "Save Reduced Data":
            indicesToSave = np.arange(4, len(self.histFigKeys))
            passThroughIndices = np.arange(2, len(self.dataNames))
            SUFFIX = "REANALYSIS.csv"
            HEADER = "Time, "

            if self.progress.value() != 100:
                result = QMessageBox.warning(
                    MainWindow,
                    "WARNING",
                    "Do you want to include in-progress fits in saved file?",
                    QMessageBox.Yes,
                    QMessageBox.No,
                )
                if result == QMessageBox.Yes:

                    saveFits = True

                    result = QMessageBox.information(
                        MainWindow,
                        "Please wait!!",
                        "The saving operation will complete once progress bar below reaches 100%!",
                    )
                    while self.progress.value() != 100:
                        app.processEvents()
                    # do something if no
            else:
                saveFits = True

        elif sender == "Save Reanalysis":
            indicesToSave = [3]
            passThroughIndices = []
            SUFFIX = "HISTAVG.csv"
            HEADER = "Bin Center, "

        if ".nc" in fileName:
            SRC = "NC"
            RFXX = self.flightNum
            LOC = self.uhsasIdent
            MIS = self.project
        else:
            SRC = "RAW"
            RFXX = "RFXX"
            LOC = "CVIU"
            MIS = "MIS"

        DATE = str(self.date)  # YYYYMMDD

        for i in indicesToSave:
            dataToSave = self.reanalysisDict[self.histFigKeys[i]]
            TIME = (
                str(int(min(dataToSave["domain"])))
                + "-"
                + str(int(max(dataToSave["domain"])))
            )
            if i == indicesToSave[0]:
                TIME = dataToSave["title"].split(" ")[-1]
                DATA = dataToSave["domain"]  # , dataToSave["range"]]
                for j in passThroughIndices:
                    DATA = np.c_[
                        DATA,
                        self.data[self.dataNames[j]][
                            self.xMatchIndices[0] : self.xMatchIndices[1]
                        ],
                    ]
                    HEADER += self.dataNames[j] + ", "
            try:
                if len(dataToSave["range"]) == 0:
                    print("Failed index: ", i)
                    raise
            except:
                continue

            DATA = np.c_[DATA, dataToSave["range"]]
            HEADER += dataToSave["title"] + ", "

            if i == 3:
                # Flip over to average plotBtn
                self.histFigMenu.setCurrentIndex(3)
                self.plotClick(False)

                try:
                    DATA = np.c_[DATA, dataToSave["fit"]]
                    HEADER += dataToSave["fit_label"]
                except:
                    HEADER += "FAILEDFIT"

        if saveFits:
            dataToSave = self.reanalysisDict[self.histFigKeys[0]]["fit"]
            # TIME = dataToSave["title"].split(" ")[-1]
            # DATA = dataToSave["domain"]  # , dataToSave["range"]]
            for key in dataToSave.keys():
                DATA = np.c_[
                    DATA, dataToSave[key][self.xMatchIndices[0] : self.xMatchIndices[1]]
                ]
                HEADER += str(key) + ", "
            # DATA = np.c_[DATA, dataToSave["range"]]
            # HEADER += dataToSave["title"] + ", "

        saveName = (
            filePath
            + "\\"
            + "UHSAS_"
            + MIS
            + "_"
            + LOC
            + "_"
            + SRC
            + "_"
            + RFXX
            + "_"
            + DATE
            + "_"
            + TIME
            + "_"
            + SUFFIX
        )

        # DATA[np.isnan(DATA)] = "#N/A"

        np.savetxt(saveName, DATA, header=HEADER, delimiter=",", fmt="%g")

        result = QMessageBox.information(
            MainWindow, "Success!!", "The saving operation has completed successfully!"
        )
        return

        # This function will handle ALL subfunction savePlots
        # Save option 1 is for parsing out a reduced excel file (No changes?)

        # Save options 1 and 2 are used to provide anlaysis on "zoomed" region!
        # Save option 2 is for reanalysis parameters at various timestamp
        # This should include ...

        # Save option 3 is for averaged region which should already have been parsed in
        # The reanalysis table.

        # Finally, should there be an .ict option?

        # Load the primary data, maybe a better way to do this without deepcopy
        x = self.time[:]  # data[self.dataNames[2]]
        y = self.data["binCenter"]

        Z = copy.deepcopy(
            self.data[self.dataNames[0]]
        )  # self.figMenu.currentIndex()]])#self.figMenu.currentIndex()]])
        M = copy.deepcopy(self.data[self.dataNames[1]])
        # if self.figMenu.currentIndex() == 1: Z = deepcopy(self.data[self.dataNames[1]])
        # X, Y = np.meshgrid(self.data[self.dataNames[1]], self.data['binCenter'])

        Z[Z == np.nan] = 0.0
        M[M == np.nan] = 0.0

        # self.histFigMenu.addItems(['Histogram', 'Counts at selected Size', 'Peak Size', 'Peak Value'])

        # matchIndex = np.argmin( np.abs(x - xClick) )

        x1 = self.data["leftBin"]
        x2 = self.data["rightBin"]
        w = x2 - x1  # variable width, can set this as a scalar also

        binEdges = np.r_[x1[:], x2[-1]]
        for j in range(len(w)):
            M[j, :] /= np.log10(binEdges[j + 1]) - np.log10(binEdges[j])

        numModes = 1

        pars = Parameters()

        # for i in range(numModes):
        pars.add(
            "amp0"
        )  # , value = sum_ys * np.max(z) / 500.0, vary = True, min = 0)#, max = backMaxs[i], min = backMins[i])#, value = backArr[i])#plsq[i])
        pars.add("mu0")  # , value = (y[np.argmax(z)]), vary = True)
        pars.add("sig0")  # , value = 1.0, vary = True, min = 1e-3)

        if numModes == 2:
            pars.add("amp1")  # , value = 1000, vary = True, min = 0)
            pars.add("mu1")  # , value = 5, vary = True, min = 0)
            pars.add("sig1")  # ,value = 1.0, vary = True, min = 1e-3)

        pars.add("offset")  # ,value = 0, vary = True, min = 0)

        obs = len(Z[0, :])

        saveDict = {}

        saveDict["FlightNum"] = [int(self.flightNum[-2:])] * obs
        saveDict["Date"] = [self.date] * obs

        self.uhsasIdent = "_" + self.uhsasIdent + "_UHSAS"

        saveDict["Time"] = x
        saveDict["rsq" + self.uhsasIdent] = np.zeros(obs, dtype="float")
        saveDict["amp" + self.uhsasIdent] = np.zeros(obs, dtype="float")
        saveDict["mu" + self.uhsasIdent] = np.zeros(obs, dtype="float")
        saveDict["sig" + self.uhsasIdent] = np.zeros(obs, dtype="float")
        saveDict["fitPeak" + self.uhsasIdent] = np.zeros(obs, dtype="float")
        saveDict["obsPeak" + self.uhsasIdent] = np.zeros(obs, dtype="float")
        saveDict["obsMu" + self.uhsasIdent] = np.zeros(obs, dtype="float")

        saveDict["PM1" + self.uhsasIdent] = np.zeros(obs, dtype="float")
        saveDict["tCounts" + self.uhsasIdent] = np.zeros(obs, dtype="float")

        for i in range(obs):  # len(Z[0,:])):
            try:
                pars["amp0"].set(value=max(Z[:, i]) * 2.0, vary=True, min=0)
                pars["sig0"].set(value=1.0, vary=True, min=1e-5)
                pars["mu0"].set(value=(y[np.argmax(Z[:, i])]), vary=True, min=0.1)
                # print(Z[:,i], Z[Z[:,i] >= 1,i])
                # input('wait')
                if len(Z[Z[:, i] >= 1, i]) <= 2:
                    pars["sig0"].set(value=1e-4, vary=False, min=1e-5)
                    pars["amp0"].set(value=0, vary=False, min=0)
                    pars["mu0"].set(value=0.1, vary=False)
                pars["offset"].set(value=0, vary=True, min=0)

                saveDict["obsPeak" + self.uhsasIdent][i] = max(Z[:, i])
                saveDict["obsMu" + self.uhsasIdent][i] = y[np.argmax(Z[:, i])]

                saveDict["tCounts" + self.uhsasIdent][i] = np.nansum(Z[:, i])
                saveDict["PM1" + self.uhsasIdent][i] = np.nansum(M[:, i])

                z = Z[:, i]  # matchIndex]
                if 1 == 0:  # self.uhsasIdent == 'NCAR':
                    out = minimize(
                        self.pdf,
                        pars,
                        args=(y[y > 100.0],),
                        kws={"data": z[y > 100], "numModes": numModes},
                        scale_covar=True,
                    )  # , method = 'trust-constr')#'trust-exact')#, reduce_fcn = 'None')
                else:
                    out = minimize(
                        self.pdf,
                        pars,
                        args=(y[:],),
                        kws={"data": z[:], "numModes": numModes},
                        scale_covar=True,
                    )  # , method = 'trust-constr')#'trust-exact')#, reduce_fcn = 'None')
                # print(fit_report(out))
                # print("Iteration ", i, " Out of ", len(Z[0, :]))
                slope, intercept, r_value, p_value, std_err = stats.linregress(
                    Z[:, i], self.pdf(out.params, y[:])
                )

                saveDict["rsq" + self.uhsasIdent][i] = r_value
                saveDict["amp" + self.uhsasIdent][i] = out.params["amp0"]
                saveDict["mu" + self.uhsasIdent][i] = out.params["mu0"]
                saveDict["sig" + self.uhsasIdent][i] = out.params["sig0"]
                saveDict["fitPeak" + self.uhsasIdent][i] = max(self.pdf(out.params, y[:]))

                """
				self.histFigure.clear()
				ax = self.histFigure.subplots()
				ax.set_title("Time:")
				ax.set_xlabel('Bin Center')
				ax.set_ylabel('Counts')
				ax.bar(x1, Z[:,i], width = w)
				ax.plot((y), self.pdf(out.params,y[:]), 'b-', lw=5, alpha = 0.6)
				ax.set_yscale('log')
				ax.set_xscale('log')
				ax.set_aspect('auto')
				ax.autoscale()
				ax.relim()
				#ax.autoscale()
				self.histCanvas.draw()
				app.processEvents()
				"""
                # print(np.exp(out.params['mu0'] + pow(out.params['sig0'],2)/2))
                # line1.set_ydata(self.spectralModel(out.params, x[:], hitranPars))
            except:
                print(sys.exc_info())
            # except: print("Failed Fit at index: ", i)

        saveFile = self.project + "_" + self.flightNum + self.uhsasIdent + ".csv"

        with open(saveFile, "w", newline="") as f:  # Just use 'w' mode in 3.x
            w = csv.writer(f)  # DictWriter(f, saveDict.keys())
            w.writerow(saveDict.keys())
            w.writerows(zip(*saveDict.values()))

        # print(saveFile)
        # winsound.Beep(self.freq, self.dur)
        if self.batchArg:  # == 'batch':
            self.loadBtn.click()

    def loadData(self):
        """Data loading function

    	Used to load as much as possible from files.

    	inputs:
    		saveOption: Denotes which save option to use as passed by signal

    	outpus: None
    	"""

        self.loadBtn.setDisabled(True)

        if self.batchArg:  # == 'batch':
            self.batchOrder += 1
            uhsasFile = self.fileList[0]
            if self.batchOrder == 1:
                self.fileList = self.fileList[1:]
            if self.batchOrder == 2:
                self.batchOrder = 0
                # self.loadBtn.click()
                # self.batchOrder = 0
            # else: self.batchOrder += 1
        else:
            options = QFileDialog.Options()
            # options |= QFileDialog.DontUseNativeDialog
            defaultDir = os.path.expanduser("~").replace("\\", "/")
            # fileName, _ = QFileDialog.getOpenFileName(self, "Select NetCDF Files", defaultDir, "NetCDF Files (*.nc);;All Files (*)", options = options)
            uhsasFile, _ = QFileDialog.getOpenFileName(
                self,
                "Select UHSAS File",
                "./",
                "UHSAS Files (*.xls;*.nc);;All Files (*)",
                options=options,
            )
        if not uhsasFile:
            self.loadBtn.setDisabled(False)
            return

        self.dataFile = uhsasFile

        # self.flightLabel = tmp

        # 	dataset = Dataset(fileName)
        # else: return

        # self.dataNames = ['Time','dN/dlogD by Time', 'dM/dlogD by Time']#
        # self.figMenu.addItems(self.dataNames)
        extraNames = []

        # fileName = filedialog.askopenfilename()
        self.data = {}
        self.data["leftBin"] = []
        self.data["rightBin"] = []
        self.data["binCenter"] = []

        ret = 2
        if ".nc" in uhsasFile:
            dataset = Dataset(uhsasFile)
            keys = dataset.variables.keys()

            if self.batchArg:  # == 'batch':
                ret = self.batchOrder
            else:
                msgBox = QMessageBox()  # .warning()
                msgBox.setText("Would you like to process CVI UHSAS or UCAR UHSAS")
                msgBox.addButton(QPushButton("CVI UHSAS"), QMessageBox.YesRole)
                msgBox.addButton(QPushButton("UCAR UHSAS"), QMessageBox.NoRole)
                msgBox.addButton(QPushButton("Cancel"), QMessageBox.RejectRole)
                ret = msgBox.exec_()

            try:
                for key in keys:
                    if "UHSAS" in key and "CVIU" not in key:
                        NCARkey = key.split("_")[-1][-4:]
                        break
            except:
                NCARkey = ""

            """
			for key in keys:
				print(key)
				try:
					print(dataset[key].units)
					print(dataset[key].Category)
					print(dataset[key].long_name)
					#print(dataset[key].standard_name)
					print('\n')
				except: pass
			"""

            # return

            self.project = "NA"
            self.flightNum = "NA"
            self.date = "NA"

            try:
                # tmp = uhsasFile.split('/')[-1]
                self.project = dataset.ProjectName
                self.flightNum = dataset.FlightNumber
                self.date = dataset.FlightDate
                # if 'rf' in tmp: tmp = 'RF' + tmp.split('rf')[-1][0:2]
                # elif 'RF' in tmp: tmp = 'RF' + tmp.split('RF')[-1][0:2]
                # else: raise
            except:
                tmp = "RFNA"

            self.date = self.date.replace("/", "")

            self.uhsasIdent = "CVIU"

            if ret == 2:
                return  # msgBox == QMessageBox.Yes
            elif ret == 0:
                matchStr = "CVIU"
            # elif ret == 1: matchStr = 'RPO'
            elif ret == 1:
                matchStr = NCARkey
                self.uhsasIdent = "NCAR"
                if NCARkey == "":
                    return

            try:
                validTimes = ~np.ma.getmask(dataset["UPRESS_" + matchStr][:])
            except:
                validTimes = np.where(dataset["Time"] != np.nan)[0]
            # print(validTimes)

            self.time = dataset["Time"][:]  # [validTimes]
            # extraNames.append(Time)
            for key in keys:
                if (
                    matchStr in key
                    and "CUHSAS_" + matchStr not in key
                    and "AUHSAS_" + matchStr not in key
                ):
                    extraNames.append(key)
                    self.dataNames.append(key)
                    self.data[key] = dataset[key][:]  # [validTimes]
                    self.data[key][~validTimes] = np.nan

            self.data["rightBin"] = dataset["CUHSAS_" + matchStr].CellSizes[1:] * 1000.0
            self.data["leftBin"] = dataset["CUHSAS_" + matchStr].CellSizes[0:-1] * 1000.0

            # print(self.data['leftBin'],self.data['rightBin'])

            for left, right in zip(self.data["leftBin"], self.data["rightBin"]):
                # self.data['binCenter'].append(np.round((left+right)/2.0,3))
                self.data["binCenter"].append(np.sqrt(left * right))

            # print(self.data['binCenter'])

            # self.data[self.dataNames[0]] = dataset['CUHSAS_'+matchStr][validTimes,0,1:]
            self.data[self.dataNames[0]] = dataset["CUHSAS_" + matchStr][:, 0, 1:]
            self.data[self.dataNames[0]][~validTimes, :] = np.nan
            # self.data[self.dataNames[1]] = dataset['CUHSAS_'+matchStr][:,0,1:]
            fileSize = len(self.data[self.dataNames[0]])
            self.data[self.dataNames[0]] = np.transpose(self.data[self.dataNames[0]])
            self.data[self.dataNames[1]] = copy.deepcopy(self.data[self.dataNames[0]])
            # print(self.data['leftBin'].shape)
        else:

            """
			for key, desc in zip(ncVariableNames,ncVariableDesc):#extraParamKeys:
				#print(key)
				try: dataStruct[key] = dataset.variables[key][:,0]#dataset.variables[key[0]][:]
				except: dataStruct[key] = dataset.variables[key][:]
				try:
					dataStruct[key]
					dataStructDesc[key] = str(dataset.variables[key].long_name)
					if desc == '-':	dataStructUnits[key] = str(dataset.variables[key].units)#key[2]
					else: dataStructUnits[key] = desc
					dataStructFillValue[key] = dataset.variables[key]._FillValue
					#extraParams.append(dataset.variables[key][:])
			"""

            extraNames = [
                "Accum (s)",
                "Scatter (V)",
                "Current (V)",
                "Sample (V)",
                "Ref. (V)",
                "Temp (V)",
                "Sheath (sccm)",
                "Diff. (V)",
                "Box (K)",
                "Purge (sccm)",
                "Pres. (kPa)",
                "Aux. (V)",
                "Flow (sccm)",
            ]
            self.dataNames.extend(extraNames)
            for item in self.dataNames:
                self.data[item] = []
            self.date = []

            # time = []
            # scatter = []

            # reader = csv.reader(open(uhsasFile, "r"), delimiter=",")
            # header1 = next(reader, None
            # header2 = next(reader,None)
            # x = list(reader)
            # result = np.array(x).astype("float")

            self.time = []
            self.date = []

            with open(uhsasFile, "r") as inFile:
                csv_reader = csv.reader(inFile, delimiter="\t")
                fileSize = sum(1 for row in csv_reader) - 2

            with open(uhsasFile, "r") as inFile:
                csv_reader = csv.reader(inFile, delimiter="\t")
                for line_count, row in enumerate(csv_reader):
                    if line_count == 0:
                        header1 = row
                    elif line_count == 1:
                        header2 = row
                        leftBin = header1[15:]
                        self.data["leftBin"] = [float(x) for x in leftBin]
                        rightBin = header2[15:]
                        self.data["rightBin"] = [float(x) for x in rightBin]
                        # binCenter = []
                        for left, right in zip(
                            self.data["leftBin"], self.data["rightBin"]
                        ):
                            # self.data['binCenter'].append(np.round((left+right)/2.0,3))
                            self.data["binCenter"].append(np.sqrt(left * right))
                        self.data[self.dataNames[0]] = np.zeros(
                            (len(self.data["binCenter"]), fileSize), dtype="float"
                        )
                        self.data[self.dataNames[1]] = np.zeros(
                            (len(self.data["binCenter"]), fileSize), dtype="float"
                        )
                    else:
                        timestamp = row[1].split(" ")[0]

                        # timestamp = timestamp.split(':')[0]
                        timestamp = timestamp.split(":")

                        date = row[0].split("/")
                        date = gcal2jd(date[2], date[0], date[1])[1] * 86400.0

                        AMPM = row[1].split(" ")[-1]
                        if int(timestamp[0]) == 12:
                            timestamp[0] = "0"
                        if AMPM == "PM":
                            timestamp[0] = str(int(timestamp[0]) + 12)
                            # print(timestamp[0])
                        # if AMPM == 'AM' and float(timestamp[0]) == 12: timestamp[0] = '0'
                        # elif AMPM == 'PM' and float(timestamp[0]) == : timestamp[0] = str(float(timestamp[0]) + 12)
                        timestamp = (
                            float(timestamp[0]) * 60 * 60
                            + float(timestamp[1]) * 60
                            + float(timestamp[2])
                        )

                        # Correction for bug in uhsas code
                        if timestamp > 86399.5 and timestamp < 86400:
                            date -= 86400.0

                        # self.data[self.dataNames[1]].append(timestamp)

                        self.date.append((date))
                        self.time.append(timestamp + date)

                        for i, item in enumerate(self.dataNames):
                            if i > 1:
                                self.data[item].append(float(row[i]))

                        histVals = row[15:]
                        histVals = np.array([float(x) for x in histVals])
                        self.data[self.dataNames[0]][:, line_count - 2] = histVals
                self.date = self.date[0]
                # date = gcal2jd(date[2], date[0], date[1])[1] * 86400.0

        ###Conditional statement end
        self.figMenu.addItems(extraNames)

        # self.data[self.dataNames[2]] = np.diff(self.data[self.dataNames[1]])

        for key, value in self.data.items():
            self.data[key] = np.array(self.data[key], dtype="float")

        self.rawHist = copy.deepcopy(self.data[self.dataNames[0]])

        for i in range(fileSize):
            self.data[self.dataNames[0]][:, i] = (
                (self.data[self.dataNames[0]][:, i])
            ) / ((np.log10(self.data["rightBin"]) - np.log10(self.data["leftBin"])))

        if ".nc" not in uhsasFile:
            # Index 12 is pressure, index 10 is box temp, index 5 is sample flow, index 2 is accumulation time.
            flow = copy.deepcopy(
                self.data[self.dataNames[5]]
                * (1.0 / 60.0)
                # * (3.5 / 60.0)
                # * (self.data[self.dataNames[12]])
                # / (self.data[self.dataNames[10]])
            )
            self.data[self.dataNames[0]] /= (
                flow[:] * 1.0
            )  # Divide by flow * accumulation time

            self.time = [x - self.date for x in self.time]
            date = jd2gcal(gcal2jd(2000, 1, 1)[0], self.date / 86400)
            self.date = (
                str(date[0]).zfill(4) + str(date[1]).zfill(2) + str(date[2]).zfill(2)
            )

        # self.data[self.dataNames[0]][self.data[self.dataNames[0]] > 15000.0] = np.nan
        # self.data[self.dataNames[0]][self.data[self.dataNames[0]] <= 0.0] = np.nan

        # def reject_outliers(data, m=2):
        # self.data[self.dataNames[0]][abs(self.data[self.dataNames[0]] - \
        # 	np.mean(self.data[self.dataNames[0]])) < 2* np.std(self.data[self.dataNames[0]])] =\
        # 	2*np.std(self.data[self.dataNames[0]])

        # for( i = 0 ;i < 99 ; i += 1 )
        # 	avg[i] = mean(A,i*points,(i+1)*points-1)
        # Make/O/N=(99,2) M_avg = avg[p][q]*pi*(gsize[p])^3/6*10^18
        for i in range(fileSize):
            self.data[self.dataNames[1]][:, i] = self.convertdN2dM(
                self.data[self.dataNames[0]][:, i], self.data["binCenter"]
            )
            # (
            #    self.data[self.dataNames[0]][:, i]
            #    * np.pi
            #    * pow(self.data["binCenter"] * 1e-9, 3.0)
            #    * (1.0 / 6.0)
            #    * (1e18)
            # )
            # print(pow(self.data['binCenter']*1e-9,3.0))

        # defaultDir = os.path.expanduser('./').replace('\\','/')
        calFile = "./config/uhsasCalBins.csv"
        if ret == 0 or ".nc" not in uhsasFile:
            try:
                # raise
                calReader = csv.reader(open(calFile, "r"), delimiter=",")
                calHeader = next(calReader, None)
                cals = list(calReader)
                cals = np.array(cals).astype("float")
                # print(cals[:,1],cals[:,2])
                self.data["leftBin"] = np.array([float(x) for x in cals[:, 1]])
                self.data["rightBin"] = np.array([float(x) for x in cals[:, 2]])
                self.data["binCenter"] = np.sqrt(
                    self.data["leftBin"] * self.data["rightBin"]
                )
                # for i, left, right in enumerate(zip(self.data['leftBin'],self.data['rightBin'])):
                # print(i,left,right)
                # 	self.data['binCenter'][i] = (np.sqrt(left*right))
            except:
                print("Failed to parse cal file")

        self.primaryPlotting(True)

        self.saveBtn.setDisabled(False)
        self.saveReanalysis.setDisabled(False)

        ######################################################
        # worker = Worker(
        #    self.fitToAllData(self.data["binCenter"], self.data[self.dataNames[0]], 1)
        # )  # Any other args, kwargs are passed to the run function

        worker = Worker(
            self.fitToAllData,
            self.time,
            self.data["binCenter"],
            self.data[self.dataNames[0]],
            1,
        )

        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.threadpool.start(worker)
        ######################################################

        if self.batchArg:  # sys.argv[1] == 'batch':
            self.saveBtn.click()

    def convertdN2dM(self, hist, binCenters):
        return hist * np.pi * pow(binCenters * 1e-9, 3.0) * (1.0 / 6.0) * (1e18)

    def progress_fn(self, n):
        # print("%d%% done" % n)
        self.progress.setValue(n)

    def print_output(self, s):
        # load s dict into the self.reanalysisDict
        for key in s.keys():
            self.reanalysisDict[self.histFigKeys[0]]["fit"][key] = s[key]

    def thread_complete(self):
        self.progress.setValue(100)

    def fixPlotLabels(self, axObject, figObject):
        figureObjetct.plt.setp(ax.get_xticklabels())

    def primaryPlotting(self, initial=False):  # , code = 0, )
        """Data Plotting

    	Used to plot data?
    	"""
        self.figMenu.setDisabled(False)
        self.histFigMenu.setDisabled(False)

        x = self.time  # data[self.dataNames[2]]
        y = self.data["binCenter"]
        Z = copy.deepcopy(self.data[self.dataNames[self.figMenu.currentIndex()]])

        # X, Y = np.meshgrid(self.data[self.dataNames[2]], self.data['binCenter'])
        X, Y = np.meshgrid(x, y)

        # self.figure.clear()
        # ax = self.figure.add_subplot(111)
        # self.ax = self.figure.subplots()

        x_lim = self.ax.get_xlim()
        y_lim = self.ax.get_ylim()

        self.figure.clear()
        # ax = self.figure.add_subplot(111)
        self.ax = self.figure.subplots()

        # self.ax = self.figure.gca()
        self.ax.callbacks.connect("xlim_changed", self.plotClick)

        self.ax.set_title(
            self.dataNames[self.figMenu.currentIndex()], fontsize=9, fontweight="bold"
        )
        self.ax.set_xlabel("Time (s)", fontsize=8, fontweight="bold")

        if self.figMenu.currentIndex() <= 1:
            self.ax.set_title(
                self.dataNames[self.figMenu.currentIndex()],
                fontsize=9,
                fontweight="bold"
                + "",  # " .... Click to plot histogram in selected region"
            )

            if self.figMenu.currentIndex() == 0:
                self.ax.set_ylabel("dN/dlogD", fontsize=8, fontweight="bold")
                # Z[Z > 10000.0] = 10000.0
                # Z[Z < 0] = 0.
            elif self.figMenu.currentIndex() == 1:
                self.ax.set_ylabel("dM/dlogD", fontsize=8, fontweight="bold")
                # Z[Z > 50.0] = 50.0
                # Z[Z < 0] = 0.

            Z[Z < 0] = np.nan
            # Z[abs(Z - np.mean(Z)) < 1* np.std(Z)] =	1*np.std(Z)
            # print(np.nanstd(Z),np.nanmean(Z))
            Z[
                Z - np.nanmedian(Z[np.logical_and(Z > 0, Z < 15000)])
                > 4.0 * np.nanstd(Z[np.logical_and(Z > 0, Z < 15000)])
            ] = 4.0 * np.nanstd(Z[np.logical_and(Z > 0, Z < 15000)])
            # extent = [X.min(),X.max(),Y.min(),Y.max()]
            # im = ax.imshow(Z,cmap = cm.magma, extent = extent, origin = 'lower', interpolation = 'nearest', aspect = 'auto')#return
            # im = ax.contourf(X,Y,Z, cmap = cm.magma)
            im = self.ax.pcolormesh(
                X, Y, Z, cmap=cm.viridis  # magma , shading="gouraud",
            )  # , vmax=np.max(Z), vmin=np.min(Z))#-abs(Z).max())
            self.ax.set_yscale("log")
            self.figure.colorbar(im)
            self.ax.set_aspect("auto")

        # elif self.figMenu.currentIndex() == 1:
        # self.ax.set_title(self.dataNames[1] + ' .... Click to plot histogram in selected region')
        # self.ax.set_ylabel('dM/dlogD')
        # im = self.ax.pcolormesh(X,Y,Z, cmap=cm.magma)

        else:  # self.figMenu.currentIndex() > 1:
            self.ax.set_ylabel(
                self.dataNames[self.figMenu.currentIndex()], fontsize=8, fontweight="bold"
            )
            self.ax.plot(x, Z)
            # ax.plot(self.data[self.dataNames[1]],self.data[self.dataNames[self.figMenu.currentIndex()]])

        self.ax.autoscale()

        if not initial:
            # min = np.min(y_lim)
            # max = np.max(y_lim)
            # if self.figMenu.currentIndex() == 0 or self.figMenu.currentIndex() == 1:
            #    if min <= 0:
            #        min = 40
            #    if max <= 0:
            #        max = 50
            # print(x_lim, y_lim)
            # self.ax.set_ylim(y_lim[0], y_lim[1])
            self.ax.set_xlim(np.min(x_lim), np.max(x_lim))

        self.ax.relim()

        # ax.autoscale()
        # self.figure.style.use("dark_background")
        # self.figure.tight_layout()  # pad=0, w_pad=0, h_pad=0)
        self.resizeEvent()

        self.canvas.draw()

        app.processEvents()

        if initial:
            self.plotClick(False)

    def resizeEvent(self, event=[]):
        # self.canvas.draw()
        # self.histCanvas.draw()

        self.histFigure.subplots_adjust(bottom=0, right=1, top=1, left=0)

        self.figure.tight_layout(pad=0, h_pad=0, w_pad=0)
        self.histFigure.tight_layout(pad=0, h_pad=0, w_pad=0)
        # self.resized.emit()
        # return super(Window, self).resizeEvent(event)

    def closeEvent(self, event):
        result = QMessageBox.warning(
            MainWindow,
            "WARNING",
            "Are you sure you want to close the program?",
            QMessageBox.Yes,
            QMessageBox.No,
        )
        event.ignore()

        if result == QMessageBox.Yes:
            self.closeTrigger = True
            event.accept()


"""

uhsasFile = '20180809183125.xls'


for i in range(fileSize):
	uhsasData[i,:] = (uhsasData[i,:])/(np.log(rightBin)-np.log(leftBin))

uhsasData[uhsasData > 10000.0] = 10000.0

X, Y = np.meshgrid(time, binCenter)
#v = np.linspace(0,10000,6, endpoint = True)
#print(v)
#plt.contourf(X,Y,np.transpose(uhsasData),v,extend='both')#,v)#,levels, colors = colors)
#plt.contourf(X,Y,np.transpose(uhsasData), 200, extend = 'both')
extent = [np.min(time), np.max(time), (np.min(binCenter)), (np.max(binCenter))]
fig = plt.imshow(np.transpose(uhsasData), extent = extent, cmap = cm.magma, origin = 'lower')#, aspect = 'auto')
#plt.gcf().autofmt_xdat()
fig.axes.set_yscale('log')
fig.axes.set_autoscale_on(False)
plt.colorbar()
#plt.colorbar(ticks = v)
#plt.contour(x,y,z)
plt.show()
"""


if __name__ == "__main__":
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    MainWindow = Ui_MainWindow()
    MainWindow.setStyleSheet(open("pyqtStyle.qss", "r").read())
    MainWindow.setWindowTitle("UHSAS QA/QC")
    # MainWindow.setGeometry(MainWindow.left, MainWindow.top, MainWindow.width, MainWindow.height)
    MainWindow.showMaximized()
    # MainWindow.setWindowState(QtCore.Qt.WindowMaximized)
    # app.processEvents()

    sys.exit(app.exec_())
