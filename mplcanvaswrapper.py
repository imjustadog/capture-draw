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
from datasender import TcpServer
from dataparse import GetData

Y_MAX = 10
Y_MIN = 1
INTERVAL = 1
INTERVAL_COUNT = 60
MAXCOUNTER = 48

send_lock = threading.Lock()


class MplCanvas(FigureCanvas):
    filepath = ''
    clickdate = []

    def __init__(self):
        self.fig = Figure(facecolor='w')
        
        self.ax_data = self.fig.add_subplot(211)
        self.ax_data.set_xlabel("time/s")
        self.ax_data.set_ylabel('value')
        # self.ax_data.legend()
        # self.ax_data.set_ylim(-5,5)
        # self.ax_data.xaxis.set_major_locator(MultipleLocator(100))  # every minute is a major locator
        # self.ax_data.xaxis.set_minor_locator(MultipleLocator(10)) # every 10 second is a minor locator
        
        self.ax_freq = self.fig.add_subplot(212)
        self.ax_freq.set_ylabel('frequency')
        # self.ax_freq.legend()
        # self.ax_freq.set_ylim(Y_MIN, Y_MAX)
        self.ax_freq.xaxis.set_major_locator(HourLocator([3, 6, 9, 12, 15, 18, 21]))  # every minute is a major locator
        #self.ax_freq.xaxis.set_minor_locator(SecondLocator([10, 20, 30, 40, 50]))  # every 10 second is a minor locator
        self.ax_freq.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))  # tick label formatter
        
        self.fig.subplots_adjust(top=0.92, bottom=0.13, left=0.10, right=0.95)

        self.curveObj_data = None
        self.clickObj_data = None
        self.annotate_data = None
        self.pointObj_data = None

        self.clickObj_freq = None
        self.annotate_freq = None

        '''
        self.curveObj_freq = None  # draw object
        '''

        self.cid = None
        
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot_realtime(self, datalist, counter):
        self.clear_freq_annotate()
        for x in datalist:
            if x['freqcurve'] is None:
                # create draw object once
                x['freqcurve'], = self.ax_freq.plot(
                                                    np.array(x['datax']),
                                                    np.array(x['datay']),
                                                    '-',
                                                    picker=False,
                                                    linewidth=2.5
                                                    )

                x['freqpoint'], = self.ax_freq.plot(
                                                    np.array(x['datax']),
                                                    np.array(x['datay']),
                                                    'o',
                                                    picker=5,
                                                    mew=0
                                                    )
            else:
                # update data of draw object
                x['freqcurve'].set_data(np.array(x['datax']), np.array(x['datay']))
                x['freqpoint'].set_data(np.array(x['datax']), np.array(x['datay']))
        # update limit of X axis,to make sure it can move
        if counter >= MAXCOUNTER:
            self.ax_freq.set_xlim(x['datax'][0], x['datax'][-1])
        else:
            self.ax_freq.set_xlim(x['datax'][0], x['datax'][0]+timedelta(hours=24))
        self.ax_freq.set_ylim(3, 7)
        ticklabels = self.ax_freq.xaxis.get_ticklabels()
        for tick in ticklabels:
            tick.set_rotation(25)
        self.draw()

    def plot_history(self, datalist):
        self.clear_freq_annotate()
        for x in datalist:
            if x['freqcurve'] is None:
                # create draw object once
                x['freqcurve'], = self.ax_freq.plot(
                                                    np.array(x['datax']),
                                                    np.array(x['datay']),
                                                    '-',
                                                    picker=False,
                                                    linewidth=2.5
                                                    )

                x['freqpoint'], = self.ax_freq.plot(
                                                    np.array(x['datax']),
                                                    np.array(x['datay']),
                                                    'o',
                                                    picker=5,
                                                    mew=0
                                                    )
            else:
                # update data of draw object
                x['freqcurve'].set_data(np.array(x['datax']), np.array(x['datay']))
                x['freqpoint'].set_data(np.array(x['datax']), np.array(x['datay']))
        # update limit of X axis,to make sure it can move
        self.ax_freq.set_xlim(x['datax'][0], x['datax'][-1])
        self.ax_freq.set_ylim(3, 7)
        ticklabels = self.ax_freq.xaxis.get_ticklabels()
        for tick in ticklabels:
            tick.set_rotation(25)
        self.draw()
        
    def onclick(self, event):
        xdata = event.artist.get_xdata()[event.ind][0]
        ydata = event.artist.get_ydata()[event.ind][0]
        for x in self.datalist:
            if event.artist == x['freqpoint']:
                if self.clickObj_freq is None:
                    self.clickObj_freq, = self.ax_freq.plot(xdata, ydata, '*', markersize=15, mew=0)
                else:
                    self.clickObj_freq.set_data(xdata, ydata)

                self.clear_freq_annotate()

                str_datay = str(round(ydata, 2))
                self.annotate_freq = self.ax_freq.annotate(str_datay, xy=(xdata, ydata))
                break

    def clear_freq_annotate(self):
        if self.clickObj_freq is not None:
            self.clickObj_freq.remove()
            self.clickObj_freq = None
        if self.annotate_freq is not None:
            self.annotate_freq.remove()
            self.annotate_freq = None


class MplCanvasWrapper(QtGui.QWidget):
    signal_tcpsend = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        pyplot.style.use('bmh')
        QtGui.QWidget.__init__(self, parent)

        self.server = TcpServer()
        self.canvas = MplCanvas()
        self.cap_data = GetData()

        self.vbl = QtGui.QVBoxLayout()
        self.ntb = NavigationToolbar(self.canvas, parent)
        self.vbl.addWidget(self.ntb)
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)

        self.counter = 0
        self.canvas.cid = self.canvas.fig.canvas.mpl_connect('pick_event', self.canvas.onclick)

    def startPlot(self):
        if self.canvas.cid is not None:
            self.canvas.fig.canvas.mpl_disconnect(self.canvas.cid)
        for x in self.cap_data.datalist:
            x['datay'] = []
            x['datax'] = []
        self.counter = 0
        self.TcpServer.generating = True

    def pausePlot(self):
        self.canvas.cid = self.canvas.fig.canvas.mpl_connect('pick_event', self.canvas.onclick)
        self.TcpServer.generating = False

    def displayrealtimedata(self):
        self.canvas.plot_realtime(self.cap_data.datalist, self.counter)
        if self.counter >= MAXCOUNTER:
            for x in self.cap_data.datalist:
                if x['enabled']:
                    x['datax'].pop(0)
                    x['datay'].pop(0)
                else:
                    self.counter += 1

    def displayhistorydata(self, datechoosed, channelchoosed):
        pass