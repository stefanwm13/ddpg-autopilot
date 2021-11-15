import socket
import struct

PACKET_LENGTH = 41
REDUCED_P_LENGTH = 36
BEGINNING_BYTES = 5

class DataRefs:
    NONE, TIMES, SPEED, CONTROLS, ANGULAR, HEADING, POSITION, THROTTLE, RPM, ILS, GPS, WARNING = range(12)

class PackageReceiver:
    def __init__(self, ip, port):
        self.UDP_IP = ip
        self.UDP_PORT = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.currentDataRef = DataRefs.NONE

    def getIndex(self, index):
        trueIndex = ((self.currentDataRef * REDUCED_P_LENGTH) + BEGINNING_BYTES - 32) + index

        return trueIndex

    def getPacketData(self, data):
        fourByteFloatValue = ''.join(chr(ord(i)) for i in data)
        floatValue = struct.unpack('f', fourByteFloatValue)

        return floatValue

    def getValue(self, dataRef):
        data, addr = self.sock.recvfrom(1024)
        self.currentDataRef = dataRef
        dataLength = len(data)

        useData = [0] * 8

        useData[0] = self.getPacketData(data[self.getIndex(0):self.getIndex(4)])
        useData[1] = self.getPacketData(data[self.getIndex(4):self.getIndex(8)])
        useData[2] = self.getPacketData(data[self.getIndex(8):self.getIndex(12)])
        useData[3] = self.getPacketData(data[self.getIndex(12):self.getIndex(16)])
        useData[4] = self.getPacketData(data[self.getIndex(16):self.getIndex(20)])
        useData[5] = self.getPacketData(data[self.getIndex(20):self.getIndex(24)])
        useData[6] = self.getPacketData(data[self.getIndex(24):self.getIndex(28)])
        useData[7] = self.getPacketData(data[self.getIndex(28):self.getIndex(32)])

        return (
        useData[0], 
        useData[1],
        useData[2],
        useData[3],
        useData[4],
        useData[5],
        useData[6],
        useData[7])

