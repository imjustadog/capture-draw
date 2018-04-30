# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from Ui_MplMainWindow import Ui_MainWindow
import os

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

filepath = "D:\data"

hostIP = '127.0.0.1'
hostPort = 50000

channelchoosed = '通道 1'
datechoosed = ''


class Code_MainWindow(Ui_MainWindow):
    signal_getDateparam = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(Code_MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.cmdlnkbtn_realrhis.setText(_translate("MainWindow", "查看历史", None))
        self.dateEdit.hide()
        self.lbl_choosedate.hide()
        self.lbl_choosedate_2.hide()
        self.comboBox_chselect.hide()
        self.btn_showhis.hide()
        self.mplCanvas.startPlot()

        self.cmdlnkbtn_realrhis.clicked.connect(self.realtimeorhistory)
        self.btn_showhis.clicked.connect(self.getDate)
        self.dateEdit.setDate(QtCore.QDate.currentDate())

        global filepath
        path = filepath.split("\\")
        path = [x + os.path.sep for x in path]
        filepath = ''.join(path)

        global datechoosed
        datechoosed = QtCore.QDate.currentDate()

        # self.OpenServer()
        self.mplCanvas.host.startthread()
    
    def realtimeorhistory(self):
        if(self.cmdlnkbtn_realrhis.text().toUtf8() == "实时显示"):
            self.cmdlnkbtn_realrhis.setText(_translate("MainWindow", "查看历史", None))
            self.dateEdit.hide()
            self.lbl_choosedate.hide()
            self.lbl_choosedate_2.hide()
            self.comboBox_chselect.hide()
            self.btn_showhis.hide()
            self.mplCanvas.startPlot()  
        else:
            global datechoosed
            datechoosed = QtCore.QDate.currentDate()
            self.dateEdit.setDate(QtCore.QDate.currentDate())
            self.cmdlnkbtn_realrhis.setText(_translate("MainWindow", "实时显示", None))
            self.dateEdit.show()
            self.lbl_choosedate.show()
            self.lbl_choosedate_2.show()
            self.comboBox_chselect.show()
            self.btn_showhis.show()
            self.mplCanvas.pausePlot()
       
    def releasePlot(self):
        '''stop and release thread'''
        self.mplCanvas.host.releasethread()

    def closeEvent(self, event):
        result = QtGui.QMessageBox.question(self,
                      "Confirm Exit...",
                      "Are you sure you want to exit ?",
                      QtGui.QMessageBox.Yes| QtGui.QMessageBox.No)
        event.ignore()

        if result == QtGui.QMessageBox.Yes:
            self.releasePlot()  # release thread's resouce
            event.accept()

    def OpenServer(self):
        global serverIP
        global serverPort
        self.mplCanvas.host.setremote(hostIP, hostPort)
        self.mplCanvas.host.open()

    def getDate(self):  # show history data
        global datechoosed
        global channelchoosed
        global filepath
        channelchoosed = self.comboBox_chselect.currentText()
        datechoosed = self.dateEdit.date().toString('yyyy-MM-dd')
        dates = datechoosed.split('-')
        year = dates[0]
        month = str(int(dates[1]))
        day = dates[2]
        path = day
        self.mplCanvas.gethistorydata(path)

if __name__ == "__main__":
    import sys
    reload(sys)
    sys.setdefaultencoding("utf-8")
    app = QtGui.QApplication(sys.argv)
    ui_main = Code_MainWindow()
    ui_main.show()
    sys.exit(app.exec_())
