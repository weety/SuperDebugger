# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 22:18:35 2018

@author: weety
"""

import sys
import platform
import logging
from PyQt5 import QtGui,QtCore
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog,QColorDialog,\
    QFileDialog
#from ui_Login import Ui_Dialog
from PyQt5.uic import loadUi
import pyqtgraph as pg
import numpy as np
import array
import SerialLib as serlib

if platform.system() == "Windows":
    from serial.tools import list_ports
else:
    import glob
    import os
    import re

class MainWindow(QMainWindow):  
    def __init__(self, parent = None):  
        super(MainWindow, self).__init__(parent)
        
        self.serialHandle = None
        loadUi('SuperDebugger.ui', self)
        self.waveWidgetInit()
        self.pushButtonColorSel1.clicked.connect(self.funSelectColor1)
        self.pushButtonColorSel2.clicked.connect(self.funSelectColor2)
        self.pushButtonColorSel3.clicked.connect(self.funSelectColor3)
        self.pushButtonColorSel4.clicked.connect(self.funSelectColor4)
        self.pushButtonColorSel5.clicked.connect(self.funSelectColor5)
        
        self.serial_listbox = list()
        self.detect_all_devices()
        
        self.pushButtonOpenSerial.clicked.connect(self.openSerial)
        self.pushButtonCloseSerial.clicked.connect(self.closeSerial)
        self.pushButtonSend.clicked.connect(self.SerialSendMsg)
        self.pushButtonRecvClear.clicked.connect(self.RecvClear)
        self.pushButtonSendClear.clicked.connect(self.SendClear)
        self.pushButtonSave.clicked.connect(self.RecvDataSave)
        self.pushButtonLoad.clicked.connect(self.LoadDataFile)
        
    
    def waveWidgetInit(self):
        self.pw = pg.PlotWidget(name='Plot1')  ## giving the plots names allows us to link their axes together
        self.waveverticalLayout.addWidget(self.pw)
        
        ## Create an empty plot curve to be filled later, set its pen
        self.p1 = self.pw.plot()
        self.p1.setPen((255,0,0))
        #self.p1.setPen(self.pushButtonColorSel1.palette.color())
        
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
        self.p2.setPen((255,255,127))
        
        self.idx2 = 0
        self.N2 = 100
        self.data2 = array.array('d')
        
        ## Start a timer to rapidly update the plot in pw
        self.t2 = QtCore.QTimer()
        self.t2.timeout.connect(self.plotData2)
        self.t2.start(20)
        
        self.p3 = self.pw.plot()
        self.p3.setPen((0,170,0))
        
        self.p4 = self.pw.plot()
        self.p4.setPen((0,85,255))
        
        self.p5 = self.pw.plot()
        self.p5.setPen((255,85,255))

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
    
    def funSelectColor1(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.pushButtonColorSel1.setStyleSheet("QPushButton{background-color:%s}" % col.name())
            self.p1.setPen(col.name())

    def funSelectColor2(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.pushButtonColorSel2.setStyleSheet("QPushButton{background-color:%s}" % col.name())
            self.p2.setPen(col.name())
            
    def funSelectColor3(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.pushButtonColorSel3.setStyleSheet("QPushButton{background-color:%s}" % col.name())
            self.p3.setPen(col.name())
  
            
    def funSelectColor4(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.pushButtonColorSel4.setStyleSheet("QPushButton{background-color:%s}" % col.name())
            self.p4.setPen(col.name())
            
    def funSelectColor5(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.pushButtonColorSel5.setStyleSheet("QPushButton{background-color:%s}" % col.name())
            self.p5.setPen(col.name())
    
    def detect_all_devices(self):
        self.detect_all_serial_devices()
        #self.start_thread_timer(self.find_all_devices, 1)
        self.tDevDetect = QtCore.QTimer()
        self.tDevDetect.timeout.connect(self.detect_all_serial_devices)
        self.tDevDetect.start(1000)

    def detect_all_serial_devices(self):
        try:
            if platform.system() == "Windows":
                self.temp_serial = list()
                for com in list(list_ports.comports()):
                    try:
                        strCom = com[0] #+ ": " + com[1][:-7]
                    except:
                        strCom = com.device #+ ": " + com.description
                    self.temp_serial.append(strCom)
                for item in self.temp_serial:
                    if item not in self.serial_listbox:
                        self.portName.addItem(item)
                        #self.serial_frm.frm_left_listbox.insert("end", item)
                for item in self.serial_listbox:
                    if item not in self.temp_serial:
                        size = self.portName.count()
                        for index in range(size):
                            if item == self.portName.itemText(index):
                                self.portName.removeItem(index)

                self.serial_listbox = self.temp_serial

            elif platform.system() == "Linux":
                self.temp_serial = list()
                self.temp_serial = self.find_usb_tty()
                for item in self.temp_serial:
                    if item not in self.serial_listbox:
                        self.portName.addItem(item)
                for item in self.serial_listbox:
                    if item not in self.temp_serial:
                        size = self.portName.count()
                        for index in range(size):
                            if item == self.portName.itemText(index):
                                self.portName.removeItem(index)
                self.serial_listbox = self.temp_serial
        except Exception as e:
            logging.error(e)
    
    def openSerial(self):
        Port = self.portName.currentText()
        BaudRate = self.baudRate.currentText()
        ByteSize = self.dataBits.currentText()
        Parity = self.parityCom.currentText()[0]
        Stopbits = self.stopBit.currentText()
        print('Open serial:{}'.format((Port, BaudRate, ByteSize, Parity, Stopbits)))
        self.serialHandle = serlib.SerialLib(Port=Port, BaudRate=BaudRate, ByteSize=ByteSize, Parity=Parity, Stopbits=Stopbits)
        self.serialHandle.open()
        self.serialHandle.serial_device_monitor(self.serialMonitor)
        #self.serialHandle.data_received_func_register(self.serialReceived)
        self.pushButtonOpenSerial.setEnabled(False)
        self.pushButtonCloseSerial.setEnabled(True)
        # 启动线程
        self.serialThread = SerialReceiveThread(self.serialHandle.serial, self.dispContent)
        self.serialThread.start()
    
    def closeSerial(self):
        if self.serialHandle.serial.isOpen() == True:
            self.serialThread.quit()
        self.serialHandle.close()
        self.pushButtonOpenSerial.setEnabled(True)
        self.pushButtonCloseSerial.setEnabled(False)
    
    def serialWrite(self, data):
        self.serialHandle.write(data)
        print('send:')
        print(data)

    def serialMonitor(self, is_exit):
        if is_exit is False:
            print("serial device not found")
            self.serialHandle.close()
        else:
            print("closeed")

    def serialReceived(self, data):
        self.reciveData.setText(data.decode('ascii'))
        print('received:')
        print(data)
    
    def SerialSendMsg(self):
        data = self.sendDataEdit.toPlainText()
        self.serialWrite(data.encode('ascii'))
    
    def SendClear(self):
        self.sendDataEdit.clear()
    
    # 显示收发数据
    def dispContent(self, argvStr):
        isHexDisp = self.radioButtonRecvHex.isChecked()
        argvStr = str(argvStr)
        if isHexDisp == False:
            self.reciveData.insertPlainText(argvStr)
        else:
            s = ""
            for i in range(len(argvStr)):
                hval = ord(argvStr[i])
                hhex = "%02x" % hval
                s += hhex + ' '
            self.reciveData.insertPlainText(s)
            # self.contentDispText.append(r'\n')
            # 获取到text光标
            #textCursor = self.reciveData.textCursor()
            #滚动到底部
            #textCursor.movePosition(textCursor.End)
            #设置光标到text中去
        self.reciveData.moveCursor(QtGui.QTextCursor.End)
        #self.reciveData.scrollToBottom()
    
    def RecvClear(self):
        self.reciveData.clear()
    
    def RecvDataSave(self):
        try:
            filename, filetype = QFileDialog.getSaveFileName()
            fp = open(filename, 'w')
            strText = self.reciveData.toPlainText()
            fp.write('{}'.format(str(strText)))
            fp.close()
        except Exception as e:
            print(e)

    def LoadDataFile(self):
        try:
            filename, filetype = QFileDialog.getOpenFileName()
            fp = open(filename, 'r')
            data = fp.read()
            self.serialWrite(data.encode('ascii'))
            fp.close()
        except Exception as e:
            print(e)
    
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
    
    def closeEvent(self, event):
        if self.serialHandle:
            if self.serialHandle.serial.isOpen() == True:
                self.serialThread.quit()
                #self.serialHandle.close()
    
class SerialReceiveThread(QtCore.QThread):
    def __init__(self, Serial, dispContent):
        super(SerialReceiveThread, self).__init__()
        self.Serial = Serial
        self.dispContent = dispContent
        print ("创建线程")

    def run(self):
        print ("启动线程")
        while True:
            # 获得接收到的字符
            count = self.Serial.inWaiting()
            if count != 0:
                dealStr = ""
                # 读串口数据
                recv = self.Serial.read(count)
                # 在这里将接收到数据进行区分：hex 或 字符串
                # hex 格式：\xYY\xYY\xYY，如果接收到的字符是这种格式，则说明是hex字符，我们需要将
                # \x去除掉，取出YY，然后组成字符串返回
                # 如果接收到的是字符串，则使用decode进行解码
                print ("接收到的数据 %s \n类型为: %s\n" % (recv,  type(recv)))
                try:
                    dealStr = recv.decode()
                except (TypeError,  UnicodeDecodeError):
                    for i in range(len(recv)):
                        print ("不可以吗")
                        print (hex(recv[i])[2:])
                        dealStr += hex(recv[i])[2:]
                        dealStr +=' '
                    
                print ("处理后的数据 %s \n类型为: %s\n" % (dealStr,  type(dealStr)))
                
                # 显示接收到的数据
                self.dispContent(dealStr)
                # 清空接收缓冲区
                #self.Serial.flushInput()
            #time.sleep(0.1)
            if self.Serial.isOpen() == False:
                print ("关闭线程")
                self.quit()
                return

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
