# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4 import QtCore
from matplotlib.ticker import MultipleLocator
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import pyplot
import numpy as np
import struct
import operator
import os
import threading
from datetime import timedelta
from matplotlib.dates import SecondLocator, MinuteLocator, HourLocator, DateFormatter
from pcierecv import PCIeHost

Y_MAX = 10
Y_MIN = 1
INTERVAL = 1
INTERVAL_COUNT = 60
MAXCOUNTER = 100

send_lock = threading.Lock()


class MplCanvas(FigureCanvas):
    clickdate = []

    def __init__(self):
        self.fig = Figure(facecolor='w')
        
        self.ax_data = self.fig.add_subplot(211)
        self.ax_data.set_xlabel("time/s")
        self.ax_data.set_ylabel('value')
        # self.ax_data.legend()
        # self.ax_data.set_ylim(0,100)
        # self.ax_data.xaxis.set_major_locator(MultipleLocator(100))  # every minute is a major locator
        # self.ax_data.xaxis.set_minor_locator(MultipleLocator(10)) # every 10 second is a minor locator
        
        self.ax_freq = self.fig.add_subplot(212)
        self.ax_freq.set_ylabel('frequency')
        # self.ax_freq.legend()
        # self.ax_freq.set_ylim(Y_MIN, Y_MAX)
        # self.ax_freq.xaxis.set_major_locator(HourLocator([3, 6, 9, 12, 15, 18, 21]))  # every minute is a major locator
        # self.ax_freq.xaxis.set_minor_locator(SecondLocator([10, 20, 30, 40, 50]))  # every 10 second is a minor locator
        # self.ax_freq.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))  # tick label formatter
        
        self.fig.subplots_adjust(top=0.92, bottom=0.13, left=0.10, right=0.95)

        self.curve = {}
        self.point = {}

        self.clickObj_data = None
        self.annotate_data = None

        '''
        self.curveObj_freq = None  # draw object
        '''

        self.cid = None
        
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot_realtime(self, datalist, counter):
        self.clear_data_annotate()
        self.clear_data_starpoint()
        for x in datalist:
            if x['enabled']:
                xa = x
                if self.curve[x['device']] is None:
                    # create draw object once
                    self.curve[x['device']], = self.ax_data.plot(
                                                        np.array(x['datax']),
                                                        np.array(x['datay']),
                                                        '-',
                                                        picker=False,
                                                        linewidth=1
                                                        )

                    self.point[x['device']], = self.ax_data.plot(
                                                        np.array(x['datax']),
                                                        np.array(x['datay']),
                                                        'o',
                                                        picker=5,
                                                        markersize=3,
                                                        mew=0
                                                        )
                else:
                    # update data of draw object
                    self.curve[x['device']].set_data(np.array(x['datax']), np.array(x['datay']))
                    self.point[x['device']].set_data(np.array(x['datax']), np.array(x['datay']))
        # update limit of X axis,to make sure it can move
        # if counter >= MAXCOUNTER:
        #      self.ax_data.set_xlim(xa['datax'][0], xa['datax'][-1])
        # else:
        #      self.ax_data.set_xlim(xa['datax'][0], xa['datax'][0] + MAXCOUNTER)
        ticklabels = self.ax_data.xaxis.get_ticklabels()
        for tick in ticklabels:
            tick.set_rotation(25)
        self.draw()

    def plot_history(self, datalist):
        self.clear_data_annotate()
        self.clear_data_starpoint()
        for x in datalist:
            if x['enabled']:
                xa = x
                if self.curve[x['device']] is None:
                    # create draw object once
                    self.curve[x['device']], = self.ax_data.plot(
                                                        np.array(x['datax']),
                                                        np.array(x['datay']),
                                                        '-',
                                                        picker=False,
                                                        linewidth=1
                                                        )

                    self.point[x['device']], = self.ax_data.plot(
                                                        np.array(x['datax']),
                                                        np.array(x['datay']),
                                                        'o',
                                                        picker=5,
                                                        markersize=3,
                                                        mew=0
                                                        )
                else:
                    # update data of draw object
                    self.curve[x['device']].set_data(np.array(x['datax']), np.array(x['datay']))
                    self.point[x['device']].set_data(np.array(x['datax']), np.array(x['datay']))
        # update limit of X axis,to make sure it can move
        self.ax_data.set_xlim(xa['datax'][0], xa['datax'][-1])
        ticklabels = self.ax_data.xaxis.get_ticklabels()
        for tick in ticklabels:
            tick.set_rotation(25)
        self.draw()
        
    def onclick(self, event):
        xdata = event.artist.get_xdata()[event.ind][0]
        ydata = event.artist.get_ydata()[event.ind][0]
        for k, v in self.point.items():
            if event.artist == v:
                if self.clickObj_data is None:
                    self.clickObj_data, = self.ax_data.plot(xdata, ydata, '*', markersize=10, mew=0)
                else:
                    self.clickObj_data.set_data(xdata, ydata)
                str_datay = str(round(ydata, 2))
                self.clear_data_annotate()
                self.annotate_data = self.ax_data.annotate(str_datay, xy=(xdata, ydata))
                break
        self.draw()

    def clear_data_annotate(self):
        if self.annotate_data is not None:
            self.annotate_data.remove()
            self.annotate_data = None

    def clear_data_starpoint(self):
        if self.clickObj_data is not None:
            self.clickObj_data.remove()
            self.clickObj_data = None



class MplCanvasWrapper(QtGui.QWidget):
    signal_tcpsend = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        pyplot.style.use('bmh')
        QtGui.QWidget.__init__(self, parent)

        self.canvas = MplCanvas()
        self.host = PCIeHost()

        self.vbl = QtGui.QVBoxLayout()
        self.ntb = NavigationToolbar(self.canvas, parent)
        self.vbl.addWidget(self.ntb)
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)

        self.counter = 0
        self.canvas.cid = self.canvas.fig.canvas.mpl_connect('pick_event', self.canvas.onclick)
        self.host.cap_data.signal_getrealtimedata.connect(self.displayrealtimedata)
        self.host.cap_data.signal_gethistorydata.connect(self.displayrealhistorydata)
        self.canvas.cid = self.canvas.fig.canvas.mpl_connect('pick_event', self.canvas.onclick)

    def startPlot(self):
        self.canvas.clear_data_annotate()
        self.canvas.clear_data_starpoint()
        for x in self.host.cap_data.datalist:
            self.canvas.curve[x['device']] = None
            self.canvas.point[x['device']] = None
            x['datay'] = []
            x['datax'] = []
        self.counter = 0
        self.host.generating = True

    def pausePlot(self):
        self.host.generating = False

    def gethistorydata(self, path):
        pass

    @QtCore.pyqtSlot(list)
    def displayrealtimedata(self, datalist):
        self.canvas.plot_realtime(datalist, self.counter)
        # if self.counter >= MAXCOUNTER:
        #      for x in datalist:
        #          if x['enabled']:
        #              x['datax'].pop(0)
        #              x['datay'].pop(0)
        # else:
        #      self.counter += 1

    @QtCore.pyqtSlot(list)
    def displayrealhistorydata(self, datalist):
        self.canvas.plot_history(datalist)
