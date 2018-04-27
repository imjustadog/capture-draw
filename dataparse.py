from datetime import datetime
from datetime import timedelta
import os

num_dev = 16


class GetData:
    def __init__(self):
        self.datalist = []
        for i in range(num_dev):
            datadict = {}
            datadict["enables"] = 'true'
            datadict["device"] = ''
            datadict['datax'] = []
            datadict['datay'] = []
            datadict['freqcurve'] = None
            datadict['freqpoint'] = None
            self.datalist.append(datadict)

        self.datalisthistory = []
        for i in range(num_dev):
            datadict = {}
            datadict["enables"] = 'false'
            datadict["device"] = ''
            datadict['datax'] = []
            datadict['datay'] = []
            datadict['freqcurve'] = None
            datadict['freqpoint'] = None
            self.datalisthistory.append(datadict)
