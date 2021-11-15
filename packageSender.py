import socket
import struct
import subprocess
import time

class DataPacket:
    def get_DATA_packetString(self, dataRef, values):
        dataRef = bytearray([dataRef, 0, 0 ,0])
        value1 = bytearray(struct.pack('f', values[0]))
        value2 = bytearray(struct.pack('f', values[1]))
        value3 = bytearray(struct.pack('f', values[2]))
        value4 = bytearray(struct.pack('f', values[3]))
        value5 = bytearray(struct.pack('f', values[4]))
        value6 = bytearray(struct.pack('f', values[5]))
        value7 = bytearray(struct.pack('f', values[6]))
        value8 = bytearray(struct.pack('f', values[7]))
        
        data = bytearray([68, 65, 84, 65, 0])
        [data.append(string) for string in dataRef]
        [data.append(string) for string in value1]
        [data.append(string) for string in value2]
        [data.append(string) for string in value3]
        [data.append(string) for string in value4]
        [data.append(string) for string in value5]
        [data.append(string) for string in value6]
        [data.append(string) for string in value7]
        [data.append(string) for string in value8]

        return data
	
    def get_DREF_packetString(self, path, value):
        dataRefValue = bytearray(struct.pack("f",value))
        dataRefPath = bytearray(path)
        padding = bytearray(468)

        data = bytearray([68, 82, 69, 70, 0])
        [data.append(string) for string in dataRefValue]
        [data.append(string) for string in dataRefPath]
        [data.append(string) for string in padding]

        return data

class PackageSender:
    def __init__(self, ip, port):
        self.UDP_IP = ip
        self.UDP_PORT = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def sendControlAndThrottleValues(self, values):
        print "Chosen Direction: ", values
		
        packetControl = DataPacket()
        packetThrottle = DataPacket()

        packetControlString = packetControl.get_DATA_packetString(8, (values[0], values[1], -999, -999, -999, -999, -999, -999))
        packetThrottleString = packetThrottle.get_DATA_packetString(25, (values[2], values[2], -999, -999, -999, -999, -999, -999))
       
	   #print(["%d" % string for string in packetControl.getPacketString()])
        self.sock.sendto(packetControlString, (self.UDP_IP, self.UDP_PORT))
        self.sock.sendto(packetThrottleString, (self.UDP_IP, self.UDP_PORT))

    def sendAirportPlacementValues(self, values):
        packetAirportX = DataPacket()
        packetAirportY = DataPacket()
        packetAirportZ = DataPacket()

        packetAirportXString = packetAirportX.get_DREF_packetString("sim/flightmodel/position/local_x", 1393.1) #EDDH Hamburg Airport
        packetAirportYString = packetAirportY.get_DREF_packetString("sim/flightmodel/position/local_y", 109.51)
        packetAirportZString = packetAirportZ.get_DREF_packetString("sim/flightmodel/position/local_z", -16306)
		
        self.sock.sendto(packetAirportXString, (self.UDP_IP, self.UDP_PORT))
        self.sock.sendto(packetAirportYString, (self.UDP_IP, self.UDP_PORT))
        self.sock.sendto(packetAirportZString, (self.UDP_IP, self.UDP_PORT))
    
    def sendAirportReset(self):
        cmd = "xdotool search --name X-System key r"
        p = subprocess.Popen(cmd , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def releaseBrakes(self):
        cmd = "xdotool search --name X-System key b"
        x = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


        
