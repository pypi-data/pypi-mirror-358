import socket
from quarchCalibration.deviceHelpers import locateMdnsInstr
from quarchpy.user_interface import *

'''
Prints out a list of calibration instruments nicely onto the terminal, numbering each unit
'''
#def listCalInstruments(scanDictionary):
#    if (not scanDictionary):
#        printText ("No instruments found to display")
#    else:
#        x = 1
#        for k, v in scanDictionary.items():
#            # these items should all be Keysight DMM6500 AC Power Sources
#            # form of the value is '._scpi-raw._tcp.local.'
#            # we want to extract name, serial number and ip address
#            ip = k
#            # if we recognise the device, pull out the serial number
#            if "Keithley 2460 " in v[:14]:    # currently we don't get here without this being true, but that may not be the case in future
#                id = v[:14] + "\t" + v[14:].split(".")[0]   # ignore the name we've just matched, and take everything up to the first '.' this should be the serial number
#            else:
#                id = v  # else we don't recognise the device, return the whole identifier unmodified
#            printText (str(x) + " - " + id + "\t" + ip)
#            x += 1

'''
Allows the user to select a test instrument
'''
def userSelectCalInstrument(scanDictionary=None, scanFilterStr="DMM6500", title=None, message=None, tableHeaders= None, additionalOptions = None, nice=False):
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
                    # these items should all be Keysight AC6804B AC Power Sources
                    # form of the value is 'Keithley 2460 #04412428._http._tcp.local.'
                    # we want to extract name, serial number and ip address
                    ip = k
                    # if we recognise the device, pull out the serial number
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

class KeithleyDMM6500:

    ACCurrentRanges = {"1mA":1E-3,"10mA":10E-3,"100mA":100E-3,"1A":1,"3A":3,"10A":10}
    CurrentRange = ""
    ACVoltageRanges = {"100mV":100E-3,"1V":1,"10V":10,"750V":750}
    VoltageRange = ""

    # Discover DMM6500 devices through mDNS
    # returns a list of [ALIAS,IP] lists from mDNS, where the name includes "DMM6500" and the service type is scpi-raw
    @staticmethod
    def discover():
        logging.debug(os.path.basename(__file__) + ": Searching for DMM6500 Multimeters: ")
        # Look for matching mDNS devices
        responses = locateMdnsInstr("DMM6500",serviceType="_scpi-raw._tcp.local.")
        logging.debug(os.path.basename(__file__) + ": Received the following responses: " + str(responses))
        #create a list of names and ip addresses to match the standard return type for this function
        devices = []
        for response in responses:
            try:
                devices.append([responses[response],response])
            except:
                raise ValueError()
        return devices

    def __init__(self, addr):
        self.TIMEOUT = 10
        self.BUFFER_SIZE = 4096
        self.connection = None
        self.addr = addr
        self.measurementType = "RMS"
        self.measurementTypeList = ["PEAK", "RMS"]
        self.maxCurrentLimit = 8.0
        self.isOpen = False
        self.commandDelay = 0.05 # It errors on back to back comms, delay needed.
        self.lastResult = None
        self.CurrentRange = ""
        self.conString = None
        self.moduleName = None
        self.MAX_RETRIES = 5
        self.POLL_INTERVAL = 0.1  # seconds
        self.MAX_POLL_ATTEMPTS = 50  # maximum number of polling attempts

    def openConnection(self, connectionString=None):
        logging.debug(os.path.basename(__file__) + ": Opening connection to: " + str(self.addr))
        if (connectionString is not None):
            self.conString = connectionString
        else:
            self.conString = self.addr

        tries = 0
        while tries < self.MAX_RETRIES:
            try:
                self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connection.settimeout(self.TIMEOUT)
                self.connection.connect((self.conString, 5025))
                self.isOpen = True

                # Reset the device and set language on connection
                self.connection.send("*LANG SCPI\r\n".encode('latin-1'))
                time.sleep(self.commandDelay)
                self.connection.send("*RST\r\n".encode('latin-1'))
                time.sleep(self.commandDelay)

                # Verify the connection is working
                result = self.sendCommandQuery("*IDN?")
                if "KEITHLEY" in result:
                    logging.debug(os.path.basename(__file__) + ": Connection established and verified")
                    return True
                else:
                    logging.error(os.path.basename(__file__) + ": Could not verify connection")
                    self.closeConnection()
                    tries += 1

            except socket.error as e:
                logging.error(os.path.basename(__file__) + f": Connection error: {e}")
                tries += 1
                time.sleep(1)

        raise ConnectionError(f"Failed to establish connection to {self.conString} after {self.MAX_RETRIES} attempts")

    def closeConnection(self):
        logging.debug(os.path.basename(__file__) + ": closing connection to DMM6500 ")
        if self.isOpen and self.connection:
            try:
                self.connection.close()
                self.isOpen = False
            except:
                logging.error(os.path.basename(__file__) + ": Error closing connection")

    def closeDeadConnections(self):
        logging.debug(os.path.basename(__file__) + ": Attempting to close dead connections")
        try:
            deadSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            deadSocket.settimeout(self.TIMEOUT)
            deadSocket.connect((self.conString, 5030))
            deadSocket.close()
            logging.debug(os.path.basename(__file__) + ": Dead connections closed")
        except:
            logging.error(os.path.basename(__file__) + ": Error closing dead connections")

    def getCurrentError(self, reading):
        if self.CurrentRange in KeithleyDMM6500.ACCurrentRanges.keys():
            if reading == 0:
                sign = 1
            else:
                sign = reading/abs(reading)
            return (reading*0.004)+KeithleyDMM6500.ACCurrentRanges[self.CurrentRange]*0.0006*sign
        else:
            raise ValueError("Can't return error as no range has been set")

    def _checkForErrors(self):
        """
        Check if there are any errors in the error queue
        Returns a list of error messages or an empty list if no errors
        """
        errors = []
        if self.getStatusEavFlag():
            error_count = self.getErrorCount()
            for _ in range(error_count):
                error_msg = self.getNextError()
                errors.append(error_msg)
                logging.error(os.path.basename(__file__) + f": DMM6500 Error: {error_msg}")
        return errors

    def verifyCommand(self, command, expected_response=None):
        """
        Verify if a command was executed successfully by checking the error queue
        and optionally comparing the response with an expected response
        """
        errors = self._checkForErrors()
        if errors:
            error_msg = "; ".join(errors)
            raise ValueError(f"Command '{command}' failed with errors: {error_msg}")

        if expected_response is not None:
            response = self.sendCommandQuery(command)
            if response != expected_response:
                raise ValueError(f"Command '{command}' returned unexpected response: {response}")

        return True

    def pollUntilComplete(self, condition_func, timeout=None, poll_interval=None):
        """
        Poll until a condition is met or timeout occurs

        Parameters:
        condition_func: function that returns True when condition is met
        timeout: maximum time to poll in seconds (defaults to self.TIMEOUT)
        poll_interval: time between polls (defaults to self.POLL_INTERVAL)

        Returns:
        True if condition is met, False if timeout occurs
        """
        if timeout is None:
            timeout = self.TIMEOUT
        if poll_interval is None:
            poll_interval = self.POLL_INTERVAL

        start_time = time.time()
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            time.sleep(poll_interval)

        return False

    def sendCommandQuery(self, commandString, timeoutAllowed=False, max_retries=None):
        """
        Send a command to the instrument and return the response

        Parameters:
        commandString: The command to send
        timeoutAllowed: If True, return None on timeout instead of raising an exception
        max_retries: Maximum number of retries (defaults to self.MAX_RETRIES)

        Returns:
        The response from the instrument
        """
        if max_retries is None:
            max_retries = self.MAX_RETRIES

        if not self.isOpen:
            self.openConnection()

        retries = 0
        while retries < max_retries:
            try:
                # Send the command
                startTime = int(round(time.time() * 1000))
                logging.debug(os.path.basename(__file__) + ": sending command: " + commandString)
                self.connection.send((commandString + "\r\n").encode('latin-1'))

                # Read back the response data
                resultStr = self.connection.recv(self.BUFFER_SIZE).decode("utf-8")
                endTime = int(round(time.time() * 1000))
                logging.debug(os.path.basename(__file__) + ": received: " + resultStr)
                logging.debug(os.path.basename(__file__) + ": Time Taken : " + str(endTime-startTime) + " mS")
                resultStr = resultStr.strip('\r\n\t')

                # If no response came back
                if (resultStr is None or resultStr == ""):
                    logging.error("resultStr = " + str(resultStr))
                    # Check for errors
                    errors = self._checkForErrors()
                    if errors:
                        error_msg = "; ".join(errors)
                        raise ValueError(f"The DMM6500 reported errors: {error_msg}")
                    else:
                        raise ValueError("The DMM6500 did not return a response")

                return resultStr

            except socket.timeout:
                if timeoutAllowed:
                    logging.debug(os.path.basename(__file__) + ": DMM6500 command timed out: " + commandString +
                                 ", returning None as timeoutAllowed is set to True")
                    return None
                else:
                    logging.debug(os.path.basename(__file__) + ": DMM6500 command timed out: " + commandString +
                                 ", closing connection and retrying")
                    # Reset connections
                    self.closeConnection()
                    self.closeDeadConnections()
                    # Reopen connection
                    self.openConnection()
                    retries += 1

        raise TimeoutError(os.path.basename(__file__) + f": Timed out after {max_retries} attempts while expecting a response for command: {commandString}")

    def sendCommand(self, commandString, verify=True, expectedResponse=True):
        """
        Sends a command to the instrument where a response is not expected

        Parameters:
        commandString: The command to send
        verify: If True, verify the command execution by checking the error queue
        expectedResponse: If True, expect the command to execute successfully

        Returns:
        "OK" on success, or raises an exception on error
        """
        if not self.isOpen:
            self.openConnection()

        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                # Send the command
                logging.debug(os.path.basename(__file__) + ": sending command: " + commandString)
                self.connection.send((commandString + "\r\n").encode('latin-1'))
                time.sleep(self.commandDelay)  # Add delay to prevent back-to-back command errors

                # Check for errors if verification is requested
                if verify:
                    errors = self._checkForErrors()
                    if errors:
                        error_msg = "; ".join(errors)
                        raise ValueError(f"Command '{commandString}' failed with errors: {error_msg}")

                return "OK"

            except socket.timeout:
                logging.debug(os.path.basename(__file__) + ": DMM6500 command timed out: " + commandString +
                             ", closing connection and retrying")
                # Reset connections
                self.closeConnection()
                self.closeDeadConnections()
                # Reopen connection
                self.openConnection()
                retries += 1

        raise TimeoutError(os.path.basename(__file__) + f": Timed out after {self.MAX_RETRIES} attempts while sending command: {commandString}")

    def reset(self):
        """Reset the instrument and verify the reset was successful"""
        result = self.sendCommand("*RST", verify=True)
        # Additional verification: check if the instrument is in a known state after reset
        self.sendCommand("*CLS")  # Clear status registers
        self.sendCommand("*ESE 0")  # Disable event status register

        # Verify basic state
        self.verifyCommand("*ESR?", "0")  # Event Status Register should be 0
        return result

    def waitForOperationComplete(self, timeout=None):
        """
        Wait for the current operation to complete using *OPC? query

        Parameters:
        timeout: Maximum time to wait in seconds (defaults to self.TIMEOUT)

        Returns:
        True if operation completed successfully, False otherwise
        """
        if timeout is None:
            timeout = self.TIMEOUT

        def operation_complete():
            try:
                result = self.sendCommandQuery("*OPC?", timeoutAllowed=True)
                return result == "1"
            except:
                return False

        return self.pollUntilComplete(operation_complete, timeout=timeout)

    def measureACCurrent(self, range="AUTO", readings=1):
        """
        Measures AC Current with improved polling and verification

        Parameters:
        range: Current range to use ("AUTO" or a specific range from ACCurrentRanges)
        readings: Number of readings to take

        Returns:
        Average of the readings
        """
        # Set the range, if required
        if range != self.CurrentRange:
            if range in self.ACCurrentRanges.keys():
                self.sendCommand(f"SENS:CURR:AC:RANG {self.ACCurrentRanges[range]}")
                self.CurrentRange = range
            else:
                self.sendCommand("SENS:CURR:AC:RANG:AUTO ON")
                self.CurrentRange = "AUTO"

        # Clear the trace buffer and set up measurement
        self.sendCommand("TRAC:CLEAR")
        self.sendCommand(f"SENS:COUNT {readings}")
        self.sendCommand("STAT:OPER:MAP 0, 4917, 4918")

        # Initiate measurement
        self.sendCommandQuery("MEAS:CURR:AC?", timeoutAllowed=True)

        # Poll until measurement is complete
        def measurement_complete():
            result = self.sendCommandQuery("STAT:OPER?", timeoutAllowed=True)
            return result == "0"

        if not self.pollUntilComplete(measurement_complete):
            raise TimeoutError("Timeout waiting for AC current measurement to complete")

        # Verify measurement count
        count = int(self.sendCommandQuery("TRAC:ACT?"))
        if count != readings:
            logging.warning(f"Expected {readings} readings but got {count}")

        # Get result
        result = float(self.sendCommandQuery("TRACE:STAT:AVER?"))
        return result

    def measureACVoltage(self, range="AUTO", readings=1):
        """
        Measures AC Voltage with improved polling and verification

        Parameters:
        range: Voltage range to use ("AUTO" or a specific range from ACVoltageRanges)
        readings: Number of readings to take

        Returns:
        Average of the readings
        """
        # Set the range, if required
        if range != self.VoltageRange:
            if range in self.ACVoltageRanges.keys():
                self.sendCommand(f"SENS:VOLT:AC:RANG {self.ACVoltageRanges[range]}")
                self.VoltageRange = range
            else:
                self.sendCommand("SENS:VOLT:AC:RANG:AUTO ON")
                self.VoltageRange = "AUTO"

        # Clear the trace buffer and set up measurement
        self.sendCommand("TRAC:CLEAR")
        self.sendCommand(f"SENS:COUNT {readings}")
        self.sendCommand("STAT:OPER:MAP 0, 4917, 4918")

        # Initiate measurement
        self.sendCommandQuery("MEAS:VOLT:AC?", timeoutAllowed=True)

        # Poll until measurement is complete
        def measurement_complete():
            result = self.sendCommandQuery("STAT:OPER?", timeoutAllowed=True)
            return result == "0"

        if not self.pollUntilComplete(measurement_complete):
            raise TimeoutError("Timeout waiting for AC voltage measurement to complete")

        # Verify measurement count
        count = int(self.sendCommandQuery("TRAC:ACT?"))
        if count != readings:
            logging.warning(f"Expected {readings} readings but got {count}")

        # Get result
        result = float(self.sendCommandQuery("TRACE:STAT:AVER?"))
        return result

    def resetTrace(self):
        """Reset the trace buffer and verify it was cleared"""
        self.sendCommand("TRAC:CLE")
        time.sleep(self.commandDelay)
        self.sendCommand("TRAC:CLE")

        # Verify the trace buffer is empty
        count = int(self.sendCommandQuery("TRAC:ACT?"))
        if count != 0:
            raise ValueError(f"Failed to clear trace buffer: {count} points remain")

        return True

    def returnTraceMin(self):
        """Returns Trace Minimum Value"""
        result = float(self.sendCommandQuery("TRAC:STAT:MIN?"))
        return result

    def returnTraceMax(self):
        """Returns Trace Maximum Value"""
        result = float(self.sendCommandQuery("TRAC:STAT:MAX?"))
        return result

    def getStatusByte(self, retries=4):
        """
        Returns the status byte from the instrument
        Improved retry mechanism and validation
        """
        for tryCount in range(1, retries + 1):
            try:
                # Read status byte
                resultStr = self.sendCommandQuery("*STB?")

                # Validate the result
                statInt = int(resultStr)
                return statInt

            except (ValueError, TypeError):
                logging.debug(f"DMM6500 is not responding with valid data retry {tryCount}")
                time.sleep(0.5)

        # If we've reached here, we've exhausted all retries
        logging.error("DMM6500 is not responding with valid status byte data")
        raise ValueError("DMM6500 is not responding with valid status byte data")

    def printInstrumentStatus(self):
        """Print the instrument status in a human-readable format"""
        stat = self.getStatusByte()
        status_map = {
            1: "Reserved[0]",
            2: "Reserved[1]",
            4: "Error Available",
            8: "Questionable Event",
            16: "Message Available",
            32: "Event Status",
            64: "Request Service",
            128: "Operation Status"
        }

        status_found = False
        for bit, name in status_map.items():
            if (stat & bit) != 0:
                printText(f"{name} Flag Set")
                status_found = True

        if not status_found:
            printText("Status flags are clear")

        return stat

    def getStatusMsbFlag(self):
        """Returns the Measurement Summary Bit of the status information"""
        stat = self.getStatusByte()
        return (stat & 1) != 0

    def getStatusQsbFlag(self):
        """Returns the Question Summary Bit of the status information"""
        stat = self.getStatusByte()
        return (stat & 8) != 0

    def getStatusEavFlag(self):
        """Returns the Error Available Bit of the status information"""
        stat = self.getStatusByte()
        return (stat & 4) != 0

    def getErrorCount(self):
        """Gets the error count from the instrument"""
        errorCount = int(self.sendCommandQuery("SYSTem:ERRor:COUNT?"))
        return errorCount

    def getNextError(self):
        """Gets the next error from the instrument"""
        errorStr = self.sendCommandQuery("SYSTem:ERRor:NEXT?")
        return errorStr

    def clearErrors(self):
        """Clear all errors from the error queue"""
        while self.getErrorCount() > 0:
            self.getNextError()

        # Verify error queue is empty
        if self.getErrorCount() > 0:
            raise ValueError("Failed to clear all errors")

        return True

    def disable(self):
        """Puts the device into a safe state"""
        # Nothing to do here for this device type
        pass

    def checkOperationStatus(self):
        """Check if the instrument is busy with an operation"""
        status = int(self.sendCommandQuery("STAT:OPER?"))
        return status != 0

    def waitForOperation(self, timeout=None):
        """Wait for any ongoing operation to complete"""
        if timeout is None:
            timeout = self.TIMEOUT

        def operation_complete():
            return not self.checkOperationStatus()

        return self.pollUntilComplete(operation_complete, timeout=timeout)