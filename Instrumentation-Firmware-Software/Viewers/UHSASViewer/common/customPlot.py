# Saved data Plotting
from common.libraryImports import *


def plot(
    x,
    yTuple=None,
    plotStyle="line",
    labels=["Title", "xaxis", "yaxis"],
    colorTuple=None,
    legendTuple=None,
    alphaTuple=None,
    savePath=None,
    wide=True,
):

    if wide:
        plt.figure(figsize=(16, 9))
    else:
        plt.figure(figsize=(12, 6))

    if yTuple is None:
        yTuple = (x,)
        x = np.arange(len(x))
    if yTuple is not isinstance(yTuple, tuple):
        yTuple = (yTuple,)

    numLines = len(yTuple)
    if colorTuple is None:
        colorTuple = ("k",) * numLines
    if legendTuple is None:
        legendTuple = ("line",) * numLines
    if alphaTuple is None:
        alphaTuple = (1.0,) * numLines

    if plotStyle == "line":
        legendElements = []
        oldColor = None
        for data, color, alpha, label in zip(yTuple, colorTuple, alphaTuple, legendTuple):
            plt.plot(x, data, color, alpha=alpha, linestyle="-", linewidth=1)
            if color != oldColor:
                oldColor = color
                legendElements.extend(
                    [
                        Line2D(
                            [0],
                            [0],
                            marker=None,
                            label=label,
                            markerfacecolor=color,
                            color=color,
                        )
                    ]
                )
    if plotStyle == "coloredScatter":
        plt.scatter(
            newData["CLHOld"][redData],
            newData["PLWCD_RWIO"][redData],
            c=np.log(newData["PLWCPIP_RWII"][redData]),
            marker=".",
            cmap="magma",
            alpha=0.5,
        )

    # legendElements = []
    # for color, label in zip(np.unique(colorTuple), np.unique(legendTuple)):
    # print(color,label)

    numColors = len(np.unique(colorTuple))
    if len(legendTuple) != numColors:
        print("error")
    # plt.hexbin(newData['CLHOld'][redData],newData['CVCWCC'][redData],vmax=max,cmap=my_blues,extent=(0,high,0,high))#plt.cm.jet)
    # plt.hexbin(newData['CLHOld'][redData],newData['PLWCC'][redData],vmax=max,cmap = my_reds,extent=(0,high,0,high))
    # plt.hexbin(newData['CLHOld'][redData],newData['PLWCD_RWIO'][redData],vmax=max,cmap = my_greens,extent=(0,high,0,high))
    # plt.hexbin(newData['CLHOld'][redData],newData['PLWCPIP_RWII'][redData]*0.01,vmax=max,cmap = my_purps,extent=(0,high,0,high))
    # plt.hexbin(newData['CLHOld'][redData],newData['RICE'][redData],vmax=max,cmap = my_grays,extent=(0,high,0,high))
    # plt.plot([0,high],[0,high],color='black',lw=5)
    plt.xlabel(labels[1], fontsize=24, fontweight="bold")  # ,fs,30)
    plt.ylabel(labels[2], fontsize=24, fontweight="bold")
    plt.tick_params(axis="x", labelsize=20)
    plt.tick_params(axis="y", labelsize=20)

    if plotStyle == "line":
        plt.gca().legend(
            handles=legendElements, loc="lower right", fontsize=24, markerscale=1
        )
    plt.title(labels[0], fontsize=28, fontweight="bold")
    plt.tight_layout()  #

    plt.show()


"""
def plot(x, yTuple, colorTuple, plotStyle = 'line', labels = ['Title', 'xaxis','yaxis'],\
    legendTuple = None, alphaTuple = None, savePath = None, wide = True,):

        if wide: plt.figure(figsize=(16,9))
        else: plt.figure(figsize = (12,6))

        numLines = len(yTuple)
        if colorTuple is None: colorTuple = ('k',)*numLines
        if legendTuple is None: legendTuple = ('line',)*numLines
        if alphaTuple is None: alphaTuple = (1.0,)*numLines

        if plotStyle == "line":
            legendElements = []
            oldColor = None
            for data, color, alpha, label in zip(yTuple,colorTuple,alphaTuple,legendTuple):
                plt.plot(x,data,color,alpha = alpha,linestyle=':',linewidth=1)
                if color != oldColor:
                    oldColor = color
                    legendElements.extend([Line2D([0],[0],marker=None, label=label,markerfacecolor=color,color=color)])
        if plotStyle == 'coloredScatter':
            plt.scatter(newData['CLHOld'][redData],newData['PLWCD_RWIO'][redData],c = np.log(newData['PLWCPIP_RWII'][redData]),marker='.',cmap='magma',alpha=0.5)

        #legendElements = []
        #for color, label in zip(np.unique(colorTuple), np.unique(legendTuple)):
            #print(color,label)


        numColors = len(np.unique(colorTuple))
        if len(legendTuple) != numColors: print('error')
        #plt.hexbin(newData['CLHOld'][redData],newData['CVCWCC'][redData],vmax=max,cmap=my_blues,extent=(0,high,0,high))#plt.cm.jet)
        #plt.hexbin(newData['CLHOld'][redData],newData['PLWCC'][redData],vmax=max,cmap = my_reds,extent=(0,high,0,high))
        #plt.hexbin(newData['CLHOld'][redData],newData['PLWCD_RWIO'][redData],vmax=max,cmap = my_greens,extent=(0,high,0,high))
        #plt.hexbin(newData['CLHOld'][redData],newData['PLWCPIP_RWII'][redData]*0.01,vmax=max,cmap = my_purps,extent=(0,high,0,high))
        #plt.hexbin(newData['CLHOld'][redData],newData['RICE'][redData],vmax=max,cmap = my_grays,extent=(0,high,0,high))
        #plt.plot([0,high],[0,high],color='black',lw=5)
        plt.xlabel(labels[1],fontsize=24, fontweight="bold")#,fs,30)
        plt.ylabel(labels[2],fontsize=24, fontweight="bold")
        plt.tick_params(axis='x',labelsize=20)
        plt.tick_params(axis='y',labelsize=20)

        #legend_elements = [Line2D([0],[0],marker='o',label='CVI TDL (g/m^3)',markerfacecolor='b'),\
        #  Line2D([0],[0],marker='o',label='King (g/m^3)',markerfacecolor='r'),\
        #  Line2D([0],[0],marker='o',label='CDP (g/m^3)',markerfacecolor='g'),\
        #  Line2D([0],[0],marker='o',label='PIP (g/m^3)',markerfacecolor='purple')]
        if plotStyle == 'line':  plt.gca().legend(handles=legendElements,loc='lower right',fontsize=24,markerscale=1)
        plt.title(labels[0],fontsize=28, fontweight="bold")
        plt.tight_layout()#


"""
