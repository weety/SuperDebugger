# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 14:57:54 2018

@author: weety
"""

import sys
import time
import serial
import logging
import binascii
import platform
import threading

if platform.system() == "Windows":
    from  serial.tools import list_ports
else:
    import glob, os, re

class SerialLib(object):
    def __init__(self, Port="COM1", BaudRate="9600", ByteSize="8", Parity="N", Stopbits="1"):
        self.port = Port
        self.baudrate = BaudRate
        self.bytesize = ByteSize
        self.parity = Parity
        self.stopbits = Stopbits
        self.receive_data = ""

        self.serial = None
        self.is_opened = False
        self.is_exist = False

    def open(self, timeout=2):
        self.serial = serial.Serial()
        self.serial.port = self.port
        self.serial.baudrate = self.baudrate
        self.serial.bytesize = int(self.bytesize)
        self.serial.parity = self.parity
        self.serial.stopbits = int(self.stopbits)
        self.serial.timeout = timeout

        try:
            self.serial.open()
            if self.serial.isOpen():
                self.is_opened = True
        except Exception as e:
            self.is_opened = False
            logging.error(e)

    def close(self):
        if self.serial:
            self.is_opened = False
            self.serial.close()

    def write(self, data):
        if self.is_opened:
            #if isHex:
            #    data = binascii.unhexlify(data)
            #self.serial.write(bytes(data))
            self.serial.write(data)

    def serial_device_monitor(self, func):
        tmonitor = threading.Thread(target=self.serial_device_monitor_thread, args=(func, ))
        tmonitor.setDaemon(True)
        tmonitor.start()

    def serial_device_monitor_thread(self, func):
        while True:
            self.is_exist = False
            if platform.system() == "Windows":
                for com in list_ports.comports():
                    if com[0] == self.port:
                        self.is_exist = True
                        break
            elif platform.system() == "Linux":
                if self.port in self.find_usb_serial():
                    self.is_exist = True

            if self.is_exist is False:
                func(self.is_exist)
            time.sleep(0.8)

    def data_received_func_register(self, func):
        tDataReceived = threading.Thread(target=self.data_received_thread, args=(func, ))
        tDataReceived.setDaemon(True)
        tDataReceived.start()
    
    def data_received_thread(self, func):
        while True:
            if self.is_opened:
                try:
                    number = self.serial.inWaiting()
                    if number > 0:
                        data = self.serial.read(number)
                        if data:
                            func(data)
                except Exception as e:
                    self.is_opened = False
                    self.serial = None
                    break

    def find_usb_serial(self, vendor_id=None, product_id=None):
        '''
        Find serial device for linux
        '''
        tty_devs = list()
        for dn in glob.glob('/sys/bus/usb/devices/*') :
            try:
                vid = int(open(os.path.join(dn, "idVendor" )).read().strip(), 16)
                pid = int(open(os.path.join(dn, "idProduct")).read().strip(), 16)
                if  ((vendor_id is None) or (vid == vendor_id)) and ((product_id is None) or (pid == product_id)) :
                    dns = glob.glob(os.path.join(dn, os.path.basename(dn) + "*"))
                    for sdn in dns :
                        for fn in glob.glob(os.path.join(sdn, "*")) :
                            if  re.search(r"\/ttyUSB[0-9]+$", fn) :
                                tty_devs.append(os.path.join("/dev", os.path.basename(fn)))
            except Exception as ex:
                pass
        return tty_devs

class testSerialLib(object):
    def __init__(self):
        self.serialport = SerialLib(Port="COM6", BaudRate="57600")
        self.serialport.open()
        self.serialport.serial_device_monitor(self.myserial_device_monitor)
        self.serialport.data_received_func_register(self.myserial_data_received)

    def write(self, data):
        self.serialport.write(data)

    def myserial_device_monitor(self, is_exit):
        if is_exit is False:
            print("serial device not found")
            self.serialport.close()
        else:
            print("closeed")

    def myserial_data_received(self, data):
        print(data)

if __name__ == '__main__':
    serialport = testSerialLib()

    time.sleep(1)
    serialport.write("Hello, just for test".encode('ascii'))
    count = 0
    while count < 9:
        print("Count: %s"%count)
        time.sleep(1)
        count += 1
