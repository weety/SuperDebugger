# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 22:18:35 2018

@author: weety
"""

import sys
from PyQt5 import QtGui,QtCore
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog
#from ui_Login import Ui_Dialog
from PyQt5.uic import loadUi
import pyqtgraph as pg
import numpy as np
import array


class MainWindow(QMainWindow):  
    def __init__(self, parent = None):  
        super(MainWindow, self).__init__(parent)
        loadUi('SuperDebugger.ui', self)
        
        self.pw = pg.PlotWidget(name='Plot1')  ## giving the plots names allows us to link their axes together
        self.waveverticalLayout.addWidget(self.pw)
        
        ## Create an empty plot curve to be filled later, set its pen
        self.p1 = self.pw.plot()
        self.p1.setPen((200,200,100))
        
        ## Add in some extra graphics
        #rect = QtGui.QGraphicsRectItem(QtCore.QRectF(0, 0, 1, 1))
        #rect.setPen(pg.mkPen(100, 200, 100))
        #self.pw.addItem(rect)
        
        self.pw.showGrid(x=True, y=True)
        
        self.pw.setLabel('left', 'Value', units='V')
        self.pw.setLabel('bottom', 'Time', units='s')
        self.pw.setXRange(0, 2)
        self.pw.setYRange(0, 1e-10)
        
        #self.p1.setPen(pen='y')
        
        self.idx = 0
        self.N = 200
        self.data = array.array('d')
        
        self.pw.setXRange(0, self.N-1)
        self.pw.setYRange(-1.2, 1.2)
        
        ## Start a timer to rapidly update the plot in pw
        self.t = QtCore.QTimer()
        self.t.timeout.connect(self.plotData)
        self.t.start(10)
        #updateData()
        
        self.p2 = self.pw.plot()
        self.p2.setPen((100,200,200))
        
        self.idx2 = 0
        self.N2 = 100
        self.data2 = array.array('d')
        
        ## Start a timer to rapidly update the plot in pw
        self.t2 = QtCore.QTimer()
        self.t2.timeout.connect(self.plotData2)
        self.t2.start(20)

    def plotData(self):
        #print('plotData%d'% self.idx)
        tmp = np.sin(np.pi / 50 * self.idx)
        if len(self.data) < self.N:
            self.data.append(tmp)
        else:
            self.data[:-1] = self.data[1:]
            self.data[-1] = tmp
        self.p1.setData(self.data)
        self.idx += 1
        
    def plotData2(self):
        #print('plotData%d'% self.idx)
        tmp = np.sin(np.pi / 25 * self.idx2)
        if len(self.data2) < self.N2:
            self.data2.append(tmp)
        else:
            self.data2[:-1] = self.data2[1:]
            self.data2[-1] = tmp
        self.p2.setData(self.data2)
        self.idx2 += 1
    
    def slotCancel(self):
        self.t.stop()
        self.reject()
    
    def rand(n):
        data = np.random.random(n)
        data[int(n*0.1):int(n*0.13)] += .5
        data[int(n*0.18)] += 2
        data[int(n*0.1):int(n*0.13)] *= 5
        data[int(n*0.18)] *= 20
        data *= 1e-12
        return data, np.arange(n, n+len(data)) / float(n)
    
    def updateData():
        yd, xd = rand(10000)
        p1.setData(y=yd, x=xd)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
