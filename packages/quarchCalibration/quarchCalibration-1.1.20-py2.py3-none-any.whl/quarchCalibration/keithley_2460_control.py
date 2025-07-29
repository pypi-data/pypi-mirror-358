#import telnetlib
import socket
import time
import logging,os
import sys

from quarchCalibration.calibrationConfig import *
from quarchCalibration.deviceHelpers import locateMdnsInstr
from quarchpy.user_interface import *

'''
Prints out a list of calibration instruments nicely onto the terminal, numbering each unit
'''
def listCalInstruments(scanDictionary):
    if (not scanDictionary):
        printText ("No instruments found to display")
    else:
        x = 1
        for k, v in scanDictionary.items():
            # these items should all be Keithley 2460 SMUs
            # form of the value is 'Keithley 2460 #04412428._http._tcp.local.'
            # we want to extract name, serial number and ip address
            ip = k
            # if we recognise the device, pull out Keithley serial number
            if "Keithley 2460 " in v[:14]:    # currently we don't get here without this being true, but that may not be the case in future
                id = v[:14] + "\t" + v[14:].split(".")[0]   # ignore the name we've just matched, and take everything up to the first '.' this should be the serial number
            else:
                id = v  # else we don't recognise the device, return the whole identifier unmodified
            printText (str(x) + " - " + id + "\t" + ip)
            x += 1

'''
Allows the user to select a test instrument
'''
def userSelectCalInstrument(scanDictionary=None, scanFilterStr="2460", title=None, message=None, tableHeaders= None, additionalOptions = None, nice=False):
    #Initiate values. Originals must be stored for the case of a rescan.
    originalOptions = additionalOptions
    if User_interface.instance != None and User_interface.instance.selectedInterface == "testcenter":
        nice = False
    if message is None: message = "Select the calibration instrument to use:"
    if title is None: title = "Select a calibration instrument"
    while(True): #breaks when valid user input given
        # Scan first, if no list is supplied
        if (scanDictionary is None):
            printText ("Scanning for instruments...")
            scanDictionary = foundDevices = locateMdnsInstr(scanFilterStr)

        deviceList = []

        if nice: #prep data for nice list selection,
            if additionalOptions is None: additionalOptions = ["Rescan", "Quit"]
            if (not scanDictionary):
                deviceList.append(["No instruments found to display"])
            else:
                for k, v in scanDictionary.items():
                    # these items should all be Keithley 2460 SMUs
                    # form of the value is 'Keithley 2460 #04412428._http._tcp.local.'
                    # we want to extract name, serial number and ip address
                    ip = k
                    # if we recognise the device, pull out Keithley serial number
                    if "Keithley 2460 " in v[:14]:  # currently we don't get here without this being true, but that may not be the case in future
                        name =v[:14]
                        serialNo = v[14:].split(".")[0]
                        deviceList.append([name,serialNo,ip])
                    else:
                        id = v  # else we don't recognise the device, return the whole identifier unmodified
                        deviceList.append([ip + "=" + id + " " + ip])
            adOp = []
            for option in additionalOptions:
                adOp.append([option]*3)
            userStr = listSelection(title=title, message=message, selectionList=deviceList, tableHeaders=["Name","Serial","IP Address"], nice=nice, indexReq=True, additionalOptions=adOp)[3] #Address will allways be 3 in this format


        else: #Prep data for test center
            if (not scanDictionary):
                deviceList.append("1=No instruments found to display")
            else:

                x = 1
                for k, v in scanDictionary.items():
                    # these items should all be Keithley 2460 SMUs
                    # form of the value is 'Keithley 2460 #04412428._http._tcp.local.'
                    # we want to extract name, serial number and ip address
                    ip = k
                    # if we recognise the device, pull out Keithley serial number
                    if "Keithley 2460 " in v[:14]:    # currently we don't get here without this being true, but that may not be the case in future
                        id = v[:14] + "\t" + v[14:].split(".")[0]   # ignore the name we've just matched, and take everything up to the first '.' this should be the serial number
                    else:
                        id = v  # else we don't recognise the device, return the whole identifier unmodified
                    deviceList.append(ip + "=" + id + "\t" + ip)
                    x += 1
            if additionalOptions is None:
                additionalOptions = "Rescan=Rescan,Quit=Quit"
            deviceList = ",".join(deviceList)
            userStr = listSelection(title=title,message=message,selectionList=deviceList, additionalOptions=additionalOptions)


            
        # Process the user response
        if (userStr == 'q' or userStr.lower() in "quit"):
            return "quit"
        elif (userStr == 'r' or userStr.lower() in "rescan"):
            scanDictionary = None
            additionalOptions = originalOptions
        else:
            # Return the address string of the selected instrument
            return userStr

'''
Class for control of Keithley source measure units for calibration purposes
'''
class keithley2460:

    currentRanges = {"1uA":1E-6,"10uA":1E-5,"100uA":1E-4,"1mA":1E-3,"10mA":1E-2,"100mA":1E-1,"1A":1,"4A":4,"5A":5,"7A":7}

    '''
    Static method to locate available instruments. Returns disctionary, "IP_ADDRESS:DESCRIPTION-TEXT"
    '''
    @staticmethod
    def locateDevices():
        return None



    '''
    Init the class
    '''
    def __init__(self, connectionString):
        self.conString = connectionString
        self.connection = None
        self.idnString = "MODEL 2460"
        self.BUFFER_SIZE = 1024
        self.TIMEOUT = 120 #Changed to allow AIC calibration due to delay of meas:curr? when calibrating leakage.
        
    '''
    Open the connection to the instrument
    '''
    def openConnection (self, connectionString = None):
        # Connect TCP
        if (connectionString is not None):
            self.conString = connectionString
        self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connection.settimeout(self.TIMEOUT)
        logging.debug(os.path.basename(__file__) + ": opening connection: " + self.conString)
        self.connection.connect((self.conString,5025))
        # Clear errors, set to default state
        response = self._sendCommand("*RST")
        # Send the IDN? command
        response = self._sendCommandQuery ("*IDN?")
        # Verify this looks like the expected instrument
        if (response.find (self.idnString) == -1):
            raise ValueError ("Connected device does not appear to be a keithley2460")
        
    '''
    Close the connection to the instrument
    '''
    def closeConnection (self):
        logging.debug(os.path.basename(__file__) + ": closing connection to Keithley ")
        self.connection.close()

    '''
    Attempts to force close any existing (LAN) socket connections
    '''
    def closeDeadConnections (self):
        deadSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        deadSocket.settimeout(self.TIMEOUT)
        deadSocket.connect((self.conString,5030))
        deadSocket.close()

        
    '''
    Send a command to the instrument and return the response from the query
    This should only be used for commands which expect a response
    '''
    def _sendCommandQuery (self, commandString):
        retries = 1
        while retries < 5:
            try:
                # Send the command
                startTime= int(round(time.time() * 1000))
                logging.debug(os.path.basename(__file__) + ": sending command: " + commandString)
                if "*STB" not in commandString:
                    logging.info("Sending Keithley Cmd: " + commandString)
                self.connection.send((commandString + "\r\n").encode('latin-1'))
                # Read back the response data
                resultStr = self.connection.recv(self.BUFFER_SIZE).decode("utf-8")
                endTime = int(round(time.time() * 1000))
                logging.debug(os.path.basename(__file__) + ": received: " + resultStr)
                logging.debug(os.path.basename(__file__) + ": Time Taken : " + str(endTime-startTime) + " mS")
                resultStr = resultStr.strip ('\r\n\t')
                # If no response came back
                if (resultStr is None or resultStr == ""):
                    logWarning("resultStr = "+ resultStr)
                    if (self.getStatusEavFlag () == True):
                        errorStr = self.getNextError ()
                        self.clearErrors ()
                        raise ValueError ("Keithley query command did not run correctly: " + errorStr)
                    else:
                        raise ValueError ("The Keithley did not return a response")
                return resultStr
            except socket.timeout:
                logging.debug(os.path.basename(__file__) + ": keithley command timed out: " + commandString + ", closing connection and retrying")
                # reset connections on Keithley
                self.closeDeadConnections()
                # reopen connection to keithley
                self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.connection.settimeout(self.TIMEOUT)
                self.connection.connect((self.conString,5025))
                # increment retry counter
                retries = retries + 1
        raise TimeoutError (os.path.basename(__file__) + ": timed out while expecting a response")
        
    
    '''
    Sends a command to the instrument where a response is not expected.
    Status byte check is used to verify that the command does not flag an error
    If an error is found, it will be flushed and the first error text returned
    'OK' is returned on success
    '''
    def _sendCommand (self, commandString, expectedResponse = True):
        retries = 1
        while retries < 5:
            try:
                # Send the command
                logging.debug(os.path.basename(__file__) + ": sending command: " + commandString)
                logging.info("Sending Keithley Cmd: " + commandString)
                self.connection.send((commandString + "\r\n").encode('latin-1'))
                # Check for errors
                if (self.getStatusEavFlag () == True):
                    errorStr = self.getNextError ()
                    logging.error(errorStr)
                    self.clearErrors ()
                    return errorStr
                else:
                    return "OK"
            except socket.timeout:
                logging.debug(os.path.basename(__file__) + ": keithley command timed out: " + commandString + ", closing connection and retrying")
                # reset connections on Keithley
                self.closeDeadConnections()
                # reopen connection to keithley
                self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.connection.settimeout(self.TIMEOUT)
                self.connection.connect((self.conString,5025))
                # increment retry counter
                retries = retries + 1
        raise TimeoutError (os.path.basename(__file__) + ": timed out while sending command to Keithley")
    
    '''
    Reset the instrument
    '''
    def reset (self):
        # Reset the Keithley to its default state
        result = self._sendCommand("*RST")
        # Send the IDN? command
        response = self._sendCommandQuery ("*IDN?")
        # Verify this looks like the expected instrument
        if (response.find (self.idnString) == -1):
            raise ValueError ("Connected device does not appear to be a keithley2460")
        return result
        
    '''
    Enable/disable the outputs
    '''
    def setOutputEnable (self, enableState, timeout=2):
        command = "OUTP ON"
        if (enableState == True):
            result = self._sendCommand(command)
        else:
            command = "OUTP OFF"
            result = self._sendCommand(command)

        # Start timer
        start_time = time.time()

        # Poll that the keithley is in the correct state
        while self.getOutputEnable() != enableState:
            elapsed_time = time.time() - start_time
            # If timeout is hit - log it and return
            if elapsed_time > timeout:
                logWarning("Error! Command: " + command + " has timed out after " + str(timeout) + " seconds.")
                printText("Error! Command: " + command + " has timed out after " + str(timeout) + " seconds.")
                raise TimeoutError("Error! Command: " + command + " has timed out after " + str(timeout) + " seconds.")

        return True
        
    '''
    Return the output enable state as a boolean
    '''
    def getOutputEnable (self):
        result = self._sendCommandQuery ("OUTP?")
        if (int(result) == 1):
            return True
        else:
            return False

    '''
    Enable/disable the outputs
    '''

    def setOutputMode(self, timeout=2, mode="HIMPedance"):
        command = "OUTP:SMOD " + mode
        result = self._sendCommand(command)

        # Start timer
        start_time = time.time()

        # Poll that the keithley is in the correct state
        while self.getOutputMode() != mode:
            elapsed_time = time.time() - start_time
            # If timeout is hit - log it and return
            if elapsed_time > timeout:
                logWarning("Error! Command: " + command + " has timed out after " + str(timeout) + " seconds.")
                printText("Error! Command: " + command + " has timed out after " + str(timeout) + " seconds.")
                raise TimeoutError("Error! Command: " + command + " has timed out after " + str(timeout) + " seconds.")

        return True

    '''
    Return the output enable state as a boolean
    '''

    def getOutputMode(self):
        result = self._sendCommandQuery("OUTP:SMOD?")
        return result

    '''
    Set the output voltage limit, in volts
    '''
    def setLoadVoltageLimit (self, voltValue, timeout=2):
        result = self._sendCommand("SOUR:CURR:VLIM " + str(voltValue))

        # Start timer
        start_time = time.time()

        # Poll that the keithley is in the correct state
        while self.getLoadVoltageLimit() != voltValue:
            elapsed_time = time.time() - start_time
            # If timeout is hit - log it and return
            if elapsed_time > timeout:
                logWarning("Error! Command: " + "SOUR:CURR:VLIM " + str(voltValue) + " has timed out after " + str(timeout) + " seconds.")
                printText("Error! Command: " + "SOUR:CURR:VLIM " + str(
                    voltValue) + " has timed out after " + str(timeout) + " seconds.")
                raise TimeoutError("Error! Command: " + "SOUR:CURR:VLIM " + str(
                    voltValue) + " has timed out after " + str(timeout) + " seconds.")
                return False
        return True
        
    '''
    Return the load voltage limit as a float
    '''
    def getLoadVoltageLimit (self):
        result = self._sendCommandQuery ("SOUR:CURR:VLIM?")
        return float(result)
        
    '''
    Switch the outputs to high impedance mode
    '''
    def setOutputMode (self, modeString, timeout=2):
        modeString = modeString.upper()
        # validate modestring
        if modeString in ["HIMP","NORMAL","ZERO"]:
            # set the mode
            result = self._sendCommand("OUTP:CURR:SMOD " + modeString)
        else:
            raise ValueError ("Invalid mode type specified: " + modeString)

        # Start timer
        start_time = time.time()

        # Poll that the keithley is in the correct state
        while self.getOutputMode() != modeString:
            elapsed_time = time.time() - start_time
            # If timeout is hit - log it and return
            if elapsed_time > timeout:
                logWarning("Error! Command: " + "OUTP:CURR:SMOD " + modeString + " has timed out after " + str(timeout) + " seconds.")
                printText(
                    "Error! Command: " + "OUTP:CURR:SMOD " + modeString + " has timed out after " + str(timeout) + " seconds.")
                raise TimeoutError(
                    "Error! Command: " + "OUTP:CURR:SMOD " + modeString + " has timed out after " + str(timeout) + " seconds.")
                return False

        return True
            
        
        
    '''
    Returns the high impedance mode as a string
    '''
    def getOutputMode (self):
        return self._sendCommandQuery("OUTP:CURR:SMOD?");
        
    '''
    Changes the instrument into the specified measurement mode
    '''
    def setMeasurementMode (self, measModeString, timeout=2):
        measModeString = measModeString.upper()
        command = ""
        if (measModeString == "VOLT"):
            command = "SENS:FUNC \"VOLT\""
            result = self._sendCommand(command)
        elif (measModeString == "CURR"):
            command = "SENS:FUNC \"CURR\""
            result = self._sendCommand(command)
        else:
            raise ValueError ("Invalid mode type specified: " + measModeString)

        # Start timer
        start_time = time.time()

        # Poll that the keithley is in the correct state
        while self.getMeasurementMode() != measModeString:
            elapsed_time = time.time() - start_time
            # If timeout is hit - log it and return
            if elapsed_time > timeout:
                logWarning("Error! Command: " + command + " has timed out after " + str(timeout) + " seconds.")
                printText("Error! Command: " + command + " has timed out after " + str(timeout) + " seconds.")
                raise TimeoutError("Error! Command: " + command + " has timed out after " + str(timeout) + " seconds.")
                return False

        return True
            
    '''
    Return the current measurement mode as a string
    '''
    def getMeasurementMode (self):
        return self._sendCommandQuery("SENS:FUNC?").strip('\"')
        
    '''
    Changes the instrument into the specified source/output mode
    '''
    def setSourceMode (self, sourceModeString, timeout=2):
        sourceModeString = sourceModeString.upper()
        if sourceModeString in ["VOLT","CURR"]:
            result = self._sendCommand("SOUR:FUNC " + sourceModeString)
        else:
            raise ValueError ("Invalid mode type specified: " + sourceModeString)

        # Start timer
        start_time = time.time()

        # Poll that the keithley is in the correct state
        while self.getSourceMode() != sourceModeString:
            elapsed_time = time.time() - start_time
            # If timeout is hit - log it and return
            if elapsed_time > timeout:
                logWarning("Error! Command: " + "SOUR:FUNC " + sourceModeString + " has timed out after " + str(timeout) + " seconds.")
                printText(
                    "Error! Command: " + "SOUR:FUNC " + sourceModeString + " has timed out after " + str(timeout) + " seconds.")
                raise TimeoutError(
                    "Error! Command: " + "SOUR:FUNC " + sourceModeString + " has timed out after " + str(timeout) + " seconds.")
                return False

        return True

    '''
    Return the source mode, as a string
    '''
    def getSourceMode (self):
        return self._sendCommandQuery("SOUR:FUNC?")
               
    '''
    Sets the number of measurements to be averaged together to return one voltage measurement
    '''
    def setAverageVoltageCount (self, measCount=1, timeout=2):
        self._sendCommand("VOLT:AVER:COUNT " + str(measCount))
        self._sendCommand("VOLT:AVER ON")

        # Start timer
        start_time = time.time()

        # Poll that the keithley is in the correct state
        while int(self.getAverageVoltageCount()) != int(measCount):
            elapsed_time = time.time() - start_time
            # If timeout is hit - log it and return
            if elapsed_time > timeout:
                logWarning("Error! Command: " + "VOLT:AVER:COUNT " + str(measCount) + " has timed out after " + str(timeout) + " seconds.")
                printText("Error! Command: " + "VOLT:AVER:COUNT " + str(
                    measCount) + " has timed out after " + str(timeout) + " seconds.")
                raise TimeoutError("Error! Command: " + "VOLT:AVER:COUNT " + str(
                    measCount) + " has timed out after " + str(timeout) + " seconds.")
                return False

        # Start timer
        start_time = time.time()

        # Poll that the keithley is in the correct state
        while self.getAverageVoltageState() is False:
            elapsed_time = time.time() - start_time
            # If timeout is hit - log it and return
            if elapsed_time > timeout:
                logWarning("Error! Command: " + "VOLT:AVER ON" + " has timed out after " + str(timeout) + " seconds.")
                printText("Error! Command: " + "VOLT:AVER ON" + " has timed out after " + str(timeout) + " seconds.")
                raise TimeoutError("Error! Command: " + "VOLT:AVER ON" + " has timed out after " + str(timeout) + " seconds.")
                return False

        return True



    '''
    Gets the number of measurements to be averaged together to return one voltage measurement
    '''
    def getAverageVoltageCount (self):
        return self._sendCommandQuery("VOLT:AVER:COUNT?")

    '''
    Gets the state of whether measurements are to be averaged together to return one voltage measurement
    '''
    def getAverageVoltageState(self):
        result = self._sendCommandQuery("VOLT:AVER?")
        if int(result) == 1:
            return True
        else:
            return False

    '''
    Sets the number of measurements to be averaged together to return one current measurement
    '''
    def setAverageCurrentCount (self, measCount=1, timeout=2):
        self._sendCommand("CURR:AVER:COUNT " + str(measCount))
        self._sendCommand("CURR:AVER ON")

        # Start timer
        start_time = time.time()

        # Poll that the keithley is in the correct state
        while int(self.getAverageCurrentCount()) != int(measCount):
            elapsed_time = time.time() - start_time
            # If timeout is hit - log it and return
            if elapsed_time > timeout:
                logWarning("Error! Command: " + "CURR:AVER:COUNT " + str(measCount) + " has timed out after " + str(timeout) + " seconds.")
                printText("Error! Command: " + "CURR:AVER:COUNT " + str(measCount) + " has timed out after " + str(timeout) + " seconds.")
                raise TimeoutError("Error! Command: " + "CURR:AVER:COUNT " + str(measCount) + " has timed out after " + str(timeout) + " seconds.")
                return False

        # Start timer
        start_time = time.time()

        # Poll that the keithley is in the correct state
        while self.getAverageCurrentState() is False:
            elapsed_time = time.time() - start_time
            # If timeout is hit - log it and return
            if elapsed_time > timeout:
                logWarning("Error! Command: " + "CURR:AVER ON" + " has timed out after " + str(timeout) + " seconds.")
                printText("Error! Command: " + "CURR:AVER ON" + " has timed out after " + str(timeout) + " seconds.")
                raise TimeoutError("Error! Command: " + "CURR:AVER ON" + " has timed out after " + str(timeout) + " seconds.")
                return False

        return True


    '''
    Gets the number of measurements to be averaged together to return one current measurement
    '''

    def getAverageCurrentCount(self):
        return self._sendCommandQuery("CURR:AVER:COUNT?")

    '''
    Gets the state of whether measurements are to be averaged together to return one current measurement
    '''

    def getAverageCurrentState(self):
        result = self._sendCommandQuery("CURR:AVER?")
        if int(result) == 1:
            return True
        else:
            return False
        
    '''
    Set the load/drain current to supply
    '''
    def setLoadCurrent (self, ampValue, timeout=2, percent_range=10):
        #load current should always be negative
        if (ampValue <= 0): 
            ampValue = -ampValue

        # set source current
        result = self._sendCommand("SOUR:CURR -" + str(ampValue))

        percent_range = percent_range/100
        load_current = self.getLoadCurrent()
        # Start timer
        start_time = time.time()
        # Poll that the keithley is in the correct state
        while float(load_current) > (float(ampValue) * (1 + percent_range)) or float(load_current) < (float(ampValue) * (1-percent_range)):
            if float(load_current) == float(ampValue):
                break
            if str(load_current).lower() == str(ampValue).lower():
                break
            elapsed_time = time.time() - start_time
            # If timeout is hit - log it and return
            if elapsed_time > timeout:
                logWarning("Error! Command: " + "SOUR:CURR " + str(ampValue) + " has timed out after " + str(timeout) + " seconds.")
                printText("Error! Command: " + "SOUR:CURR " + str(ampValue) + " has timed out after " + str(timeout) + " seconds.")
                printText("Load Current: " + str(load_current) + " Source Current: " + str(ampValue))
                raise TimeoutError("Error! Command: " + "SOUR:CURR " + str(ampValue) + " has timed out after " + str(timeout) + " seconds.")
            load_current = self.getLoadCurrent()
        return True


    '''
    Set the load/drain current sense range
    valid values for current are: 1uA, 10uA, 100uA, 1mA, 10mA, 100mA, 1A, 4A, 5A, 7A
    '''
    def setLoadCurrentRange(self, rangeValue, timeout=2):
        if rangeValue in self.currentRanges:
            # set source current range
            result = self._sendCommand("CURR:RANG " + str(self.currentRanges[rangeValue]))
        else:
            raise ValueError(str(rangeValue) + " is not a valid current range")

        # Start timer
        start_time = time.time()

        # Poll that the keithley is in the correct state
        while float(self.getLoadCurrentRange()) != float(str(self.currentRanges[rangeValue])):
            elapsed_time = time.time() - start_time
            # If timeout is hit - log it and return
            if elapsed_time > timeout:
                logWarning("Error! Command: " + "CURR:RANG " + str(self.currentRanges[rangeValue]) + " has timed out after " + str(timeout) + " seconds.")
                printText("Error! Command: " + "CURR:RANG " + str(self.currentRanges[rangeValue]) + " has timed out after " + str(timeout) + " seconds.")
                raise TimeoutError("Error! Command: " + "CURR:RANG " + str(self.currentRanges[rangeValue]) + " has timed out after " + str(timeout) + " seconds.")

        return True


    '''
    Set the load/drain current sense range
    valid values for current are: 1uA, 10uA, 100uA, 1mA, 10mA, 100mA, 1A, 4A, 5A, 7A
    '''
    def getLoadCurrentRange(self):
        return self._sendCommandQuery("CURR:RANG?")



    '''
    Set the load/drain current sense range to auto
    valid state = "ON" or "OFF"
    '''
    def setLoadCurrentRangeAuto(self,state="ON",timeout=2):
        # set source current range to auto
        if state in ["ON","OFF"]:
            result = self._sendCommand("CURR:RANG:AUTO " + state)
        else:
            raise ValueError(str(state) + " is not a valid input to setLoadCurrentRangeAuto()")

        # Start timer
        start_time = time.time()

        if state == "ON":
            state_bool = True
        else:
            state_bool = False

        # Poll that the keithley is in the correct state
        while self.getLoadCurrentRangeAuto() != state_bool:
            elapsed_time = time.time() - start_time
            # If timeout is hit - log it and return
            if elapsed_time > timeout:
                logWarning("Error! Command: " + "CURR:RANG:AUTO " + state + " has timed out after " + str(timeout) + " seconds.")
                printText(
                    "Error! Command: " + "CURR:RANG:AUTO " + state + " has timed out after " + str(timeout) + " seconds.")
                raise TimeoutError(
                    "Error! Command: " + "CURR:RANG:AUTO " + state + " has timed out after " + str(timeout) + " seconds.")
                return False

    '''
    Get the load/drain current sense range to auto
    valid state = "ON" or "OFF"
    '''
    def getLoadCurrentRangeAuto(self):
        # get source current range auto
        result = self._sendCommandQuery ("CURR:RANG:AUTO?")
        if (int(result) == 1):
            return True
        else:
            return False

    '''
    Sets the limit for the load current in Amps
    '''
    def setLoadCurrentLimit (self, ampValue, timeout=2):
        result = self._sendCommand("SOUR:VOLT:ILIM " + str(ampValue))

        # Start timer
        start_time = time.time()

        # Poll that the keithley is in the correct state
        while float(self.getLoadCurrentLimit()) != float(ampValue):
            elapsed_time = time.time() - start_time
            # If timeout is hit - log it and return
            if elapsed_time > timeout:
                logWarning("Error! Command: " + "SOUR:VOLT:ILIM " + str(ampValue) + " has timed out after " + str(timeout) + " seconds.")
                printText("Error! Command: " + "SOUR:VOLT:ILIM " + str(
                    ampValue) + " has timed out after " + str(timeout) + " seconds.")
                raise TimeoutError("Error! Command: " + "SOUR:VOLT:ILIM " + str(
                    ampValue) + " has timed out after " + str(timeout) + " seconds.")
                return False

        return True


    '''
    Gets the limit for the load current in Amps (float)
    '''
    def getLoadCurrentLimit (self):
        return self._sendCommandQuery("SOUR:VOLT:ILIM?");


    '''
    Gets the current load current, as set
    '''
    def getLoadCurrent (self):                  
        result = float((self._sendCommandQuery("SOUR:CURR?")))
        return -result
        
    '''
    Measures and returns a current value
    '''
    def measureLoadCurrent (self,count=4):
        self.setAverageCurrentCount(count)
        result = float((self._sendCommandQuery("MEAS:CURR?")))
        logging.info("Measured Load Current: " + str(-result))
        return -result
        
    '''
    Sets the load output voltage in Volts
    '''
    def setLoadVoltage (self, voltValue, timeout=2):
        result = self._sendCommand("SOUR:VOLT " + str(voltValue))
        # Start timer
        start_time = time.time()

        # Poll that the keithley is in the correct state
        while self.getLoadVoltage() != voltValue:
            elapsed_time = time.time() - start_time
            # If timeout is hit - log it and return
            if elapsed_time > timeout:
                logWarning("Error! Command: " + "SOUR:VOLT " + str(voltValue) + " has timed out after " + str(timeout) + " seconds.")
                printText("Error! Command: " + "SOUR:VOLT " + str(voltValue) + " has timed out after " + str(timeout) + " seconds.")
                raise TimeoutError("Error! Command: " + "SOUR:VOLT " + str(voltValue) + " has timed out after " + str(timeout) + " seconds.")
                return False
        return True
        
    '''
    Gets the current load voltage value
    '''
    def getLoadVoltage (self):
        result = float((self._sendCommandQuery("SOUR:VOLT?")))
        return result
        
    '''
    Measures the current load voltage value
    '''
    def measureLoadVoltage (self,count=4):    
        self.setAverageVoltageCount(count)
        result = float(self._sendCommandQuery("MEAS:VOLT?"))
        return result

    '''
    DEBUG FUNCTION - Measures the current load voltage value 
    '''
    def checkLoadVoltage (self,voltValue, timeout=5, percent_range=10):
        # Get current load voltage
        load_voltage = self.measureLoadVoltage()
        percent_range = percent_range/100
        # Start timer
        start_time = time.time()
        while float(load_voltage) > (float(voltValue) * (1 + percent_range)) or float(load_voltage) < (float(voltValue) * (1-percent_range)):
            if float(voltValue) == 0 and round(int(load_voltage) == 0):
                break
            elapsed_time = time.time() - start_time
            # If timeout is hit - log it and return
            if elapsed_time > timeout:
                logWarning("Error! Command: " + "MEAS:VOLT?" + " has timed out after " + str(timeout) + " seconds.")
                printText("Error! Command: " + "MEAS:VOLT?" + " has timed out after " + str(timeout) + " seconds.")
                printText("Expected Load Voltage: " + str(voltValue) + " Returned Load Voltage: " + str(load_voltage))
                raise TimeoutError("Error! Command: " + "MEAS:VOLT?" + " has timed out after " + str(timeout) + " seconds.")
            load_voltage = self.measureLoadVoltageNoAverage()
        return False

    '''
    Measures the current load voltage value no averaging
    '''
    def measureLoadVoltageNoAverage (self):
        result = float(self._sendCommandQuery("MEAS:VOLT?"))
        return result
        
    '''
    Returns the status byte from the instrument (the result of the *STB? command)
    This is used to tell if the module is ready or has errored
    '''
    def getStatusByte (self, retries=4):
        tryCount = 0
        while tryCount <= retries:
            tryCount +=1
            # Read status byte
            resultStr = self._sendCommandQuery ("*STB?")
            # If we get junk, try again
            try:
                statInt = int(resultStr)
                return statInt
            except:
                logging.debug("Keithley is not responding with valid data retry " + str(tryCount))

        #If we have reached here we have excepet on every try and should raise a value error
        logging.error("Keithley is not responding with valid data : " + str(resultStr))
        raise ValueError ("Keithley is not responding with valid data")

    def printInstrumentStatus (self):
        stat = self.getStatusByte ()
        if (stat&1 != 0):
            printText ("Measurement Summary Flag Set")
        if (stat&2 != 0):
            printText ("Reserved Flag 1 Set")
        if (stat&4 != 0):
            printText ("Error Available Flag Set")
        if (stat&8 != 0):
            printText ("Questionable Event Flag Set")
        if (stat&16 != 0):
            printText ("Message Available Flag Set")
        if (stat&32 != 0):
            printText ("Enabled Standard Event Flag Set")
        if (stat&64 != 0):
            printText ("Enabled Summary Bit Flag Set")
        if (stat&128 != 0):
            printText ("Enabled Operation event Flag Set")
        if (stat == 0):
            printText ("Status flags are clear")
        
    '''
    Returns the Measurement Summary Bit of the status information
    '''
    def getStatusMsbFlag (self):
        stat = self.getStatusByte ()
        # Meas bit is LSb
        if (stat&1 != 0):
            return True
        else:
            return False;
            
    '''
    Returns the Question Summary Bit of the status information
    '''
    def getStatusQsbFlag (self):
        stat = self.getStatusByte ()
        # Meas bit is LSb
        if (stat&8 != 0):
            return True
        else:
            return False;
            
    '''
    Returns the Error Available Bit of the status information
    '''
    def getStatusEavFlag (self):
        stat = self.getStatusByte ()
        # Meas bit is LSb
        if (stat&4 != 0):
            return True
        else:
            return False;
    
    '''
    Gets the next error from the instrument in a nice text form
    '''
    def getNextError (self):   
        errorStr = self._sendCommandQuery ("SYSTem:ERRor:NEXT?")
        return errorStr
    
    '''
    Clears all errors from the queue, so the status EAV flag is cleared
    '''
    def clearErrors (self):
        self._sendCommand (":SYSTem:CLEar")
        #loop = 0
        # Loop through and flush our all current errors
        #while (self.getStatusEavFlag () == True and loop < 10):
        #    print (self.getNextError ())
        #    loop += 1
    
    '''
    Sets the instrument to zero load current and returns the voltage
    Move to generic class?
    '''
    def measureNoLoadVoltage (self):
        self.setOutputEnable(False)
        self.setSourceMode("CURR")
        self.setLoadCurrent(0)
        self.setLoadVoltageLimit(15)
        self.setOutputEnable(True)
        return self.measureLoadVoltage()

    '''
    Sets the instrument load current
    Move to generic class?
    '''
    def setReferenceCurrent (self,value):
        if value >= 0:
            self.setOutputEnable(False)
            # self.setSourceMode("CURR")
            # self.setLoadVoltageLimit(15)
            self.setLoadCurrent(value)
            self.setOutputEnable(True)
        else:
            raise ValueError ("negative load current requested")

    '''
    Setup the reference current for the Keithley - ensures we do the set-up only once per cal/ver
    '''
    def initialSetupForReferenceCurrent(self):
        self.setOutputEnable(False)
        self.setSourceMode("CURR")
        self.setLoadVoltageLimit(15)

    '''
    Sets the instrument output voltage
    '''
    def setReferenceVoltage (self,value,currentLimit=1e-1,currentRange="AUTO"):
        if value >= 0:
            self.setOutputEnable(False)
            self.setLoadVoltage(value)
            self.setOutputEnable(True)
        else:
            raise ValueError ("negative voltage requested") # this is possible but a bad idea unless we really want it

    '''
    Setup the reference voltage for the Keithley - ensures we do the set-up only once per cal/ver
    '''
    def initialSetupForReferenceVoltage(self,currentLimit=1e-1,currentRange="AUTO"):
        self.setOutputEnable(False)
        self.setSourceMode("VOLT")
        self.setLoadCurrentLimit(currentLimit)
        self.setLoadVoltageLimit(15)
        if currentRange != "AUTO":
            self.setLoadCurrentRangeAuto("OFF")
            self.setLoadCurrentRange(currentRange)
        else:
            self.setLoadCurrentRangeAuto("ON")

    '''
    Puts the into a safe state
    Move to generic class?
    '''
    def disable (self):

        # Ensure Keithley Load Current is set to 0
        self.setLoadCurrent(0)
        # Ensure Keithely Load Voltage is set to 0
        self.setLoadVoltage(0)
        # Ensure Keithley is measuring 0
        # self.checkLoadVoltage(0) # Do we need this?
        # Set back to voltage mode to try and stop it blowing up! (seems to be blowing up the low-curr fet?)
        # self.setSourceMode("CURR")

        # Add a delay to ensure load voltage is measuring 0
        time.sleep(3)

        # Do not exit this method, until we are sure the load is disabled
        timeout_window = 10  # 10 seconds
        timeout = time.time() + timeout_window  # time = 10 seconds from now

        # Ensure output mode is set - default=HIMPedance
        # self.setOutputMode(self)
        # Ensure load is disabled
        while self.getOutputEnable():
            if time.time() > timeout:
                raise Exception("CRITICAL FAILURE : Can't disable Keithley, Please turn off manually and stop testing")
            self.setOutputEnable(False)
            time.sleep(0.1)
        printText("Keithley Disabled")