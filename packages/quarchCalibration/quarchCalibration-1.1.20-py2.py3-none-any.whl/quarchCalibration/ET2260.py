#import select
#import time
#import sys
#import unittest
import os
import logging
import socket

'''Control class for AC PAM switch box

#http://www.rtautomation.com/technologies/modbus-tcpip/

The static parameter, if used, should be set to the IP address of the switch box being addressed.
If static is not provided the class will use discovery to find the IP address.
'''
class SwitchBoxControl:
    phase_list = ['L1', 'L2', 'L3']
    def __init__(self, name, addr=""):
        self.name = name
        self.addr = addr
        self.port = 502 # Default port is 502

    def setMux(self,phase):

        if phase == "off":
            coils = 0x00
        elif phase == "1":
            coils = 0x01
        elif phase == "2":
            coils = 0x02
        elif phase == "3":
            coils = 0x04
        else:
            raise ValueError("invalid parameter supplied to setMux(): " + str(phase))
            coils = 0x00

        #self.client = ModbusClient(self.addr, auto_open=True, auto_close=True)
        #self.client.write_multiple_coils(0, [0, 0, 0])
        # Set all phases off
        tsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tsock.settimeout(5)
        tsock.connect((self.addr,self.port))
        request = modBusWriteMultipleCoilsRequest(3,coils)
        logging.debug(os.path.basename(__file__) + ": Sending ModBus Request: " + request)
        tsock.send(request)
        while True:
            try:
                response = tsock.recv(1024)
                ogging.debug(os.path.basename(__file__) + ": Received ModBus Response: " + response)
            except:
                   break
        tsock.close()
        
        #check response
        if (response is not None):
            if response != bytes(modBusWriteMultipleCoilsResponse(3)):
                raise ConnectionError("unexpected response received")
        else:
            raise ConnectionError("no response received from: " + self.name)

    def select_phase(self, phase):
        self.client.write_multiple_coils(0, [0, 0, 0])
        if phase in self.phase_list:
            coil_index = self.phase_list.index(phase)
            self.client.write_single_coil(coil_index, 1)

    def get_phase(self):
        try:
            active = self.client.read_coils(0, 3)
            return self.phase_list[active.index(True)]
        except ValueError:
            return "None"

# Discover ET2260 devices through UDP broadcast
# returns a dictionary of ALIAS IP pairs, where NAME=ET-2260
# This function makes a lot of assumptions about the data and certainly could be a lot more robust
def discover():

    logging.debug(os.path.basename(__file__) + ": Searching for AC switch boxes: ")

    devices = {}

    ipList = socket.gethostbyname_ex(socket.gethostname())
    logging.debug(os.path.basename(__file__) + ": Discovered the following interfaces: " + ipList)

    # broadcast/listen on each interface

    responses = []

    for ip in ipList[2]:

        logging.debug(os.path.basename(__file__) + ": Broadcasting on : " + ip)

        tsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        tsock.bind((ip,53780))
        tsock.sendto('ICPDAS7188E,00'.encode("UTF-8"), ('255.255.255.255', 57188))
        tsock.close()

        rsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # wait 1 second for a response
        rsock.settimeout(1)
        rsock.bind((ip, 54321))

        # Receive messages until timeout.
        while True:
            try:
                responses.append(rsock.recvfrom(1024))
            except:
                break

        rsock.close()


    logging.debug(os.path.basename(__file__) + ": Received the following responses: " + responses)

    # for each response received
    for response in responses:
        try:
            # we assume each response should have the payload in [0], the senders address in [1], in this case we only look at the payload which we assume is comma delimited, and contain [parameter]=[value] pairs
            # split the payload at the commas, to get the pairs
            strmsg = response[0].decode("utf8").split(",")
            # create a dictionary from each pair
            strdict = {y[0]: y[1] for y in [x.split("=") for x in strmsg[2:]]}
        except:
            # malformed data received
            break

        # if this is an ET-2260 device
        if strdict["NAME"] == "ET-2260":
            # create a dictionary entry from the alias and ip address
            devices[strdict['ALIAS']] = strdict['IP']

    return devices

def modBusWriteMultipleCoilsRequest(bitCount,bits,transactionID=0,protocolID=0,unitID=1,referenceNumber=0):
    
    try:
        bitCount_bytes=int(bitCount).to_bytes(2,'big')
    except:
        raise ValueError("ModBus bitCount invalid")

    try:
        byteCount = int((bitCount+7)/8)
        byteCount_bytes=int(byteCount).to_bytes(1,'big')
    except:
        raise ValueError("ModBus byteCount invalid")
    
    try:
        transactionID_bytes = int(transactionID).to_bytes(2,'big')
    except:
        raise ValueError("ModBus transactionID invalid")

    try:
        protocolID_bytes = int(protocolID).to_bytes(2,'big')
    except:
        raise ValueError("ModBus protocolID invalid")

    try:
        commandLength_bytes=int(byteCount+7).to_bytes(2,'big')
    except:
        raise ValueError("ModBus commandLength invalid")

    try:
        unitID_bytes = int(unitID).to_bytes(1,'big')
    except:
        raise ValueError("ModBus unitID invalid")

    try:
        referenceNumber_bytes = int(referenceNumber).to_bytes(2,'big')
    except:
        raise ValueError("ModBus referenceNumber invalid")

    try:
        bits_bytes = int(bits).to_bytes(1,'big')
    except:
        raise ValueError("ModBus bits invalid")

    return transactionID_bytes + protocolID_bytes + commandLength_bytes + unitID_bytes + b'\x0f' + referenceNumber_bytes + bitCount_bytes + byteCount_bytes + bits_bytes

def modBusWriteMultipleCoilsResponse(bitCount,transactionID=0,protocolID=0,unitID=1,referenceNumber=0):
    
    try:
        bitCount_bytes=int(bitCount).to_bytes(2,'big')
    except:
        raise ValueError("ModBus bitCount invalid")
    
    try:
        transactionID_bytes = int(transactionID).to_bytes(2,'big')
    except:
        raise ValueError("ModBus transactionID invalid")

    try:
        protocolID_bytes = int(protocolID).to_bytes(2,'big')
    except:
        raise ValueError("ModBus protocolID invalid")

    try:
        unitID_bytes = int(unitID).to_bytes(1,'big')
    except:
        raise ValueError("ModBus unitID invalid")

    try:
        referenceNumber_bytes = int(referenceNumber).to_bytes(2,'big')
    except:
        raise ValueError("ModBus referenceNumber invalid")

    return transactionID_bytes + protocolID_bytes + b'\x00\x06' + unitID_bytes + b'\x0f' + referenceNumber_bytes + bitCount_bytes
    