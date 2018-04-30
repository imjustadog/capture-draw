from datetime import datetime
from datetime import timedelta
import os
from PyQt4 import QtGui, QtCore

num_dev = 2


class GetData(QtCore.QObject):
    signal_getrealtimedata = QtCore.pyqtSignal(list)
    signal_gethistorydata = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        super(GetData, self).__init__(parent)
        self.datalist = []
        for i in range(num_dev):
            datadict = {}
            datadict['enabled'] = 'true'
            datadict['device'] = ''
            datadict['datax'] = []
            datadict['datay'] = []
            self.datalist.append(datadict)

        self.datalist[0]['device'] = '0'
        self.datalist[1]['device'] = '1'

        self.datalisthistory = []
        for i in range(num_dev):
            datadict = {}
            datadict['enabled'] = 'false'
            datadict['device'] = ''
            datadict['datax'] = []
            datadict['datay'] = []
            self.datalisthistory.append(datadict)

    def signal_realtimedata_emitter(self):
        self.signal_getrealtimedata.emit(self.datalist)

    def signal_historydata_emitter(self):
        self.signal_gethistorydata.emit(self.datalisthistory)

    @QtCore.pyqtSlot(list)
    def data_getter(self, path):
        self.signal_historydata_emitter()
