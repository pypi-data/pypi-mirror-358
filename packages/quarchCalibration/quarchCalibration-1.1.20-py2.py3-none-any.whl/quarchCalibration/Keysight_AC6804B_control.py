import socket
import time
import logging
import os
import re
from typing import Union, Optional, List, Tuple, Dict, Any


class KeysightAC6804B:
    """
    Enhanced class for control of Keysight AC6804B Power Sources
    with improved command verification and polling
    """

    # Constants for error handling and validation
    TIMEOUT = 10  # Socket timeout in seconds
    BUFFER_SIZE = 4096  # Socket buffer size
    COMMAND_DELAY = 0.05  # Delay between commands to prevent errors
    MAX_RETRIES = 5  # Maximum number of retries for commands
    POLL_INTERVAL = 0.1  # Time between polls in seconds
    POLL_TIMEOUT = 30  # Maximum time to wait for an operation in seconds

    # Command verification flags
    VERIFY_NONE = 0  # No verification
    VERIFY_ERROR = 1  # Check for errors after command
    VERIFY_VALUE = 2  # Check returned value against expected value
    VERIFY_COMPLETE = 3  # Wait for operation to complete

    # Valid parameter ranges
    VALID_VOLTAGE_RANGE = (0.0, 310.0)  # Min and max voltage in volts
    VALID_CURRENT_RANGE = (0.0, 15.0)  # Min and max current in amps
    VALID_FREQUENCY_RANGE = (40.0, 500.0)  # Min and max frequency in Hz
    VALID_RANGE_SETTINGS = ["155", "310", "AUTO"]  # Valid range settings

    @staticmethod
    def getCurrentError(reading: float) -> float:
        """Returns the instruments error for a specified current reading"""
        return (reading * 0.005) + 0.04

    @staticmethod
    def discover() -> List[List[str]]:
        """
        Discover AC6804B devices through mDNS
        Returns a list of [ALIAS,IP] lists from mDNS
        """
        from quarchCalibration.deviceHelpers import locateMdnsInstr

        logging.debug(f"{os.path.basename(__file__)}: Searching for AC6804B AC Power Sources")

        # Look for matching mDNS devices
        responses = locateMdnsInstr("AC6804B", serviceType="_scpi-raw._tcp.local.", scanTime=3)
        logging.debug(f"{os.path.basename(__file__)}: Received responses: {responses}")

        # Create a list of names and IP addresses
        devices = []
        for response in responses:
            try:
                devices.append([responses[response], response])
            except Exception as e:
                logging.error(f"Error processing discovery response: {e}")
                continue

        return devices

    def __init__(self, addr: str):
        """Initialize the connection to a Keysight AC6804B"""
        self.connection = None
        self.addr = addr
        self.measurementType = "RMS"
        self.measurementTypeList = ["PEAK", "RMS"]
        self.maxCurrentLimit = 8.0
        self.isOpen = False
        self.lastResult = None
        self.conString = None
        self._operation_complete = False
        self._last_command_timestamp = 0
        self._command_queue = []
        self._parameter_validation = True  # Enable parameter validation by default

    def openConnection(self, connectionString: Optional[str] = None) -> None:
        """Open a connection to the instrument"""
        try:
            if connectionString is not None:
                self.conString = connectionString
            else:
                self.conString = self.addr

            logging.debug(f"{os.path.basename(__file__)}: Opening connection to: {self.conString}")

            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.settimeout(self.TIMEOUT)
            self.connection.connect((self.conString, 5025))
            self.isOpen = True

            # Reset the device and clear status
            self._send_raw_command("*RST")
            self._send_raw_command("*CLS")
            self._send_raw_command("*ESE 255")  # Enable all standard event status bits

            # Set up the service request (SRQ) for operation complete
            self._send_raw_command("*SRE 32")  # Enable event status bit

            logging.info(f"Connected to AC6804B at {self.conString}")

        except socket.timeout:
            logging.error(f"Timeout while connecting to AC6804B at {self.conString}")
            raise ConnectionError(f"Unable to connect to AC6804B at {self.conString}")
        except Exception as e:
            logging.error(f"Error connecting to AC6804B: {e}")
            raise ConnectionError(f"Unable to connect to AC6804B: {e}")

    def closeConnection(self) -> None:
        """Close the connection to the instrument"""
        if self.isOpen and self.connection:
            try:
                logging.debug(f"{os.path.basename(__file__)}: Closing connection to AC6804B")
                self.connection.close()
                self.isOpen = False
            except Exception as e:
                logging.error(f"Error closing connection: {e}")
        self.connection = None

    def closeDeadConnections(self) -> None:
        """Attempts to force close any existing (LAN) socket connections"""
        try:
            deadSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            deadSocket.settimeout(self.TIMEOUT)
            deadSocket.connect((self.conString, 5030))
            deadSocket.close()
            logging.debug("Closed dead connections")
        except Exception as e:
            logging.warning(f"Error closing dead connections: {e}")

    def _send_raw_command(self, command: str) -> None:
        """Send a raw command string to the instrument without any processing"""
        if not self.isOpen:
            raise ConnectionError("Connection is not open")

        # Ensure command delay to prevent errors
        current_time = time.time()
        time_since_last = current_time - self._last_command_timestamp
        if time_since_last < self.COMMAND_DELAY:
            time.sleep(self.COMMAND_DELAY - time_since_last)

        self.connection.send(f"{command}\r\n".encode('latin-1'))
        self._last_command_timestamp = time.time()

    def _receive_response(self) -> str:
        """Receive a response from the instrument"""
        if not self.isOpen:
            raise ConnectionError("Connection is not open")

        response = self.connection.recv(self.BUFFER_SIZE).decode("utf-8")
        return response.strip('\r\n\t')

    def sendCommandQuery(self, commandString: str, verify: int = VERIFY_ERROR) -> str:
        """
        Send a command to the instrument and return the response

        Args:
            commandString: The command to send
            verify: Verification level (VERIFY_NONE, VERIFY_ERROR, VERIFY_VALUE)

        Returns:
            The response string from the instrument
        """
        if not self.isOpen:
            self.openConnection()

        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                # Send the command
                start_time = time.time()
                logging.debug(f"{os.path.basename(__file__)}: Sending query: {commandString}")
                self._send_raw_command(commandString)

                # Read back the response data
                result_str = self._receive_response()
                end_time = time.time()

                logging.debug(f"{os.path.basename(__file__)}: Received: {result_str}")
                logging.debug(f"{os.path.basename(__file__)}: Time taken: {int((end_time - start_time) * 1000)} ms")

                # Check for empty response
                if not result_str:
                    if verify >= self.VERIFY_ERROR:
                        logging.warning("Empty response received")
                        if self.getStatusEavFlag():
                            errors = self.getAllErrors()
                            logging.error(f"Instrument errors: {errors}")
                            raise ValueError(f"The AC6804B reported errors: {errors}")
                    retries += 1
                    continue

                # Store the last result
                self.lastResult = result_str

                # Check for errors if verification is requested
                if verify >= self.VERIFY_ERROR and self.getStatusEavFlag():
                    errors = self.getAllErrors()
                    logging.error(f"Instrument errors: {errors}")
                    raise ValueError(f"The AC6804B reported errors: {errors}")

                return result_str

            except socket.timeout:
                logging.warning(f"Command timed out: {commandString}, retrying ({retries + 1}/{self.MAX_RETRIES})")
                self._reconnect()
                retries += 1

            except Exception as e:
                logging.error(f"Error during command execution: {e}")
                retries += 1

        # If we get here, we've exhausted all retries
        raise TimeoutError(f"Command failed after {self.MAX_RETRIES} attempts: {commandString}")

    def sendCommand(self, commandString: str, verify: int = VERIFY_ERROR, verify_command: str = "", expected_value: Any = None) -> str:
        """
        Send a command to the instrument where a response is not expected

        Args:
            commandString: The command to send
            verify: Verification level (VERIFY_NONE, VERIFY_ERROR, VERIFY_VALUE, VERIFY_COMPLETE)
            verify_command: Command used to verify the value of the command sent.
            expected_value: Expected value for verification

        Returns:
            "OK" on success, or the error message if verification fails
        """
        if not self.isOpen:
            self.openConnection()

        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                # Send the command
                logging.debug(f"{os.path.basename(__file__)}: Sending command: {commandString}")
                self._send_raw_command(commandString)

                # Handle verification
                if verify == self.VERIFY_NONE:
                    return "OK"

                elif verify == self.VERIFY_ERROR:
                    # Check for errors
                    if self.getStatusEavFlag():
                        errors = self.getAllErrors()
                        logging.error(f"Instrument errors: {errors}")
                        raise ValueError(f"The AC6804B reported errors: {errors}")
                    return "OK"

                elif verify == self.VERIFY_VALUE:
                    # If expected value is provided, verify it
                    if expected_value is not None:
                        query_cmd = commandString + "?"
                        if verify_command != "":
                            query_cmd = verify_command
                        actual_value = self.sendCommandQuery(query_cmd, self.VERIFY_ERROR)

                        # Convert to float for numeric comparison if needed
                        try:
                            if isinstance(expected_value, (int, float)):
                                actual_value = float(actual_value)
                                if abs(actual_value - expected_value) > 0.01 * expected_value:  # Check within 1% tolerance
                                    raise ValueError(
                                        f"Value verification failed: expected {expected_value}, got {actual_value}")
                            elif str(actual_value) != str(expected_value):
                                raise ValueError(
                                    f"Value verification failed: expected {expected_value}, got {actual_value}")
                        except ValueError as e:
                            logging.error(f"Value verification error: {e}")
                            raise e
                    return "OK"

                elif verify == self.VERIFY_COMPLETE:
                    # Wait for operation to complete
                    self._operation_complete = False
                    self._send_raw_command("*OPC")

                    # Poll for operation complete
                    start_time = time.time()
                    while not self._operation_complete:
                        # Check if operation is complete
                        if int(self.sendCommandQuery("*ESR?")) & 1:  # Check OPC bit
                            self._operation_complete = True
                            break

                        # Check for timeout
                        if time.time() - start_time > self.POLL_TIMEOUT:
                            raise TimeoutError(f"Operation timed out after {self.POLL_TIMEOUT} seconds")

                        # Check for errors
                        if self.getStatusEavFlag():
                            errors = self.getAllErrors()
                            logging.error(f"Instrument errors during operation: {errors}")
                            raise ValueError(f"The AC6804B reported errors: {errors}")

                        time.sleep(self.POLL_INTERVAL)

                    return "OK"

                return "OK"

            except socket.timeout:
                logging.warning(f"Command timed out: {commandString}, retrying ({retries + 1}/{self.MAX_RETRIES})")
                self._reconnect()
                retries += 1

            except Exception as e:
                logging.error(f"Error during command execution: {e}")
                retries += 1

        # If we get here, we've exhausted all retries
        raise TimeoutError(f"Command failed after {self.MAX_RETRIES} attempts: {commandString}")

    def _reconnect(self) -> None:
        """Reconnect to the instrument after a timeout or error"""
        try:
            # Close the existing connection
            self.closeConnection()

            # Try to close any dead connections
            self.closeDeadConnections()

            # Open a new connection
            self.openConnection()

        except Exception as e:
            logging.error(f"Error during reconnection: {e}")
            raise ConnectionError(f"Failed to reconnect to instrument: {e}")

    def _validate_parameter(self, param: Any, param_name: str, valid_range: Tuple = None,
                            valid_values: List = None) -> None:
        """Validate parameters against specified ranges or allowed values"""
        if not self._parameter_validation:
            return

        if valid_range is not None:
            if not isinstance(param, (int, float)):
                raise ValueError(f"{param_name} must be a number")

            min_val, max_val = valid_range
            if param < min_val or param > max_val:
                raise ValueError(f"{param_name} must be between {min_val} and {max_val}")

        if valid_values is not None:
            if param not in valid_values:
                raise ValueError(f"{param_name} must be one of {valid_values}")

    def getAllErrors(self) -> List[str]:
        """Get all errors from the instrument's error queue"""
        errors = []
        error_count = self.getErrorCount()

        for _ in range(error_count):
            error_str = self._send_raw_command("SYSTem:ERRor:NEXT?")
            response = self._receive_response()
            errors.append(response)

        return errors

    def getErrorCount(self) -> int:
        """Gets the error count from the instrument"""
        try:
            result = self.sendCommandQuery("SYSTem:ERRor:COUNT?", self.VERIFY_NONE)
            return int(result)
        except Exception as e:
            logging.error(f"Error getting error count: {e}")
            return 0

    def getNextError(self) -> str:
        """Gets the next error from the instrument"""
        return self.sendCommandQuery("SYSTem:ERRor:NEXT?", self.VERIFY_NONE)

    def getStatusByte(self, retries: int = 4) -> int:
        """
        Returns the status byte from the instrument (*STB?)
        Used to tell if the module is ready or has errors
        """
        for try_count in range(1, retries + 1):
            try:
                result_str = self.sendCommandQuery("*STB?", self.VERIFY_NONE)
                return int(result_str)
            except ValueError:
                logging.debug(f"AC6804B is not responding with valid data retry {try_count}")

        logging.error("AC6804B is not responding with valid data")
        raise ValueError("AC6804B is not responding with valid data")

    def getStatusEavFlag(self) -> bool:
        """Returns the Error Available Flag from the status byte"""
        try:
            stat = self.getStatusByte()
            return (stat & 4) != 0
        except Exception:
            # If we can't get the status byte, assume there's an error
            return True

    def getStatusMsbFlag(self) -> bool:
        """Returns the Measurement Summary Bit of the status information"""
        stat = self.getStatusByte()
        return (stat & 1) != 0

    def getStatusQsbFlag(self) -> bool:
        """Returns the Question Summary Bit of the status information"""
        stat = self.getStatusByte()
        return (stat & 8) != 0

    def printInstrumentStatus(self) -> None:
        """Print the current status of the instrument"""
        from quarchpy.user_interface import printText

        stat = self.getStatusByte()

        if (stat & 1) != 0:
            printText("Reserved[0] Flag Set")
        if (stat & 2) != 0:
            printText("Reserved[1] Flag Set")
        if (stat & 4) != 0:
            printText("Error Available Flag Set")
        if (stat & 8) != 0:
            printText("Questionable Event Flag Set")
        if (stat & 16) != 0:
            printText("Message Available Flag Set")
        if (stat & 32) != 0:
            printText("Event Status Flag Set")
        if (stat & 64) != 0:
            printText("Request Service Flag Set")
        if (stat & 128) != 0:
            printText("Operation Status Flag Set")
        if stat == 0:
            printText("Status flags are clear")

    def waitForOperation(self, timeout: float = None) -> bool:
        """
        Wait for the current operation to complete

        Args:
            timeout: Maximum time to wait in seconds (None for default)

        Returns:
            True if operation completed, False if timed out
        """
        if timeout is None:
            timeout = self.POLL_TIMEOUT

        # Send *OPC? to wait for operation complete
        try:
            # Set a timeout for the command
            self.connection.settimeout(timeout)

            # Send OPC? command which will block until operation complete
            result = self.sendCommandQuery("*OPC?", self.VERIFY_NONE)

            # Reset timeout
            self.connection.settimeout(self.TIMEOUT)

            return result == "1"
        except Exception as e:
            logging.error(f"Error waiting for operation: {e}")

            # Reset timeout
            self.connection.settimeout(self.TIMEOUT)
            return False

    # Command methods with enhanced verification
    def reset(self) -> str:
        """Reset the instrument and wait for completion"""
        return self.sendCommand("*RST", self.VERIFY_COMPLETE)

    def setOutputEnable(self, enableState: bool) -> str:
        """Enable/disable the outputs with verification"""
        command = "OUTP ON" if enableState else "OUTP OFF"
        expected = "1" if enableState else "0"
        return self.sendCommand(command, self.VERIFY_VALUE, "OUTP?", expected)

    def getOutputEnable(self) -> bool:
        """Return the output enable state as a boolean"""
        result = self.sendCommandQuery("OUTP?")
        return int(result) == 1

    def setSupplyVoltageLimit(self, voltRMSValue: float) -> str:
        """
        Set the output voltage limit in volts

        Args:
            voltRMSValue: Voltage limit in volts

        Returns:
            "OK" on success
        """
        self._validate_parameter(voltRMSValue, "Voltage limit", self.VALID_VOLTAGE_RANGE)

        # Set both upper and lower limits
        self.sendCommand(f"VOLT:LIM:LOW {voltRMSValue}", self.VERIFY_VALUE, "VOLT:LIM:LOW?", voltRMSValue)
        return self.sendCommand(f"VOLT:LIM:UPP {voltRMSValue}", self.VERIFY_VALUE, "VOLT:LIM:UPP?", voltRMSValue)

    def getSupplyVoltageLimit(self) -> float:
        """Return the output voltage limit as a float"""
        result = self.sendCommandQuery("VOLT:LIM:UPP?")
        return float(result)

    def setSupplyCurrentLimit(self, ampRMSValue: float) -> bool:
        """
        Set the output current limit in amps

        Args:
            ampRMSValue: Current limit in amps

        Returns:
            True on success
        """
        self._validate_parameter(ampRMSValue, "Current limit", self.VALID_CURRENT_RANGE)

        self.sendCommand(f"CURR {ampRMSValue}", self.VERIFY_VALUE, "CURR?", ampRMSValue)
        return self.sendCommand("CURR:PROT:STATE ON", self.VERIFY_VALUE, "CURR:PROT:STATE?", "1") == "OK"

    def getSupplyCurrentLimit(self) -> float:
        """Return the output current limit as a float"""
        result = self.sendCommandQuery("CURR?")
        return float(result)

    def setAverageCount(self, measCount: int = 1) -> str:
        """Sets the number of measurements to be averaged"""
        self._validate_parameter(measCount, "Measurement count", (1, 100))
        return self.sendCommand(f"SENS:AVER {measCount}", self.VERIFY_VALUE, "SENS:AVER?", measCount)

    def setACSupplyVoltage(self, voltValue: float) -> str:
        """
        Sets the AC Supply output voltage in Volts

        Args:
            voltValue: Voltage value in volts

        Returns:
            "OK" on success
        """
        self._validate_parameter(voltValue, "Voltage", self.VALID_VOLTAGE_RANGE)
        return self.sendCommand(f"SOUR:VOLT {voltValue}", self.VERIFY_VALUE, "SOUR:VOLT?", voltValue)

    def getACSupplyVoltage(self) -> float:
        """Gets the AC Supply output voltage in volts"""
        result = self.sendCommandQuery("SOUR:VOLT?")
        return float(result)

    def setACSupplyRange(self, rangeString: str) -> str:
        """
        Sets the AC Supply Range "155|310|AUTO"

        Args:
            rangeString: Range setting (155, 310, or AUTO)

        Returns:
            "OK" on success
        """
        self._validate_parameter(rangeString, "AC supply range", valid_values=self.VALID_RANGE_SETTINGS)

        if rangeString == "AUTO":
            return self.sendCommand("SOUR:VOLT:RANGE:AUTO ON", self.VERIFY_VALUE, "SOUR:VOLT:RANGE:AUTO?", "1")
        else:
            self.sendCommand("SOUR:VOLT:RANGE:AUTO OFF", self.VERIFY_VALUE, "SOUR:VOLT:RANGE:AUTO?", "0")
            return self.sendCommand(f"SOUR:VOLT:RANGE {rangeString}", self.VERIFY_VALUE, "SOUR:VOLT:RANGE?", rangeString)

    def setACSupplyFrequency(self, hertzValue: float) -> str:
        """
        Sets the AC Supply frequency in Hz

        Args:
            hertzValue: Frequency in Hz

        Returns:
            "OK" on success
        """
        self._validate_parameter(hertzValue, "Frequency", self.VALID_FREQUENCY_RANGE)
        return self.sendCommand(f"SOUR:FREQ {hertzValue}", self.VERIFY_VALUE, "SOUR:FREQ?", hertzValue)

    def getACSupplyFrequency(self) -> float:
        """Gets the AC Supply frequency in Hz"""
        result = self.sendCommandQuery("SOUR:FREQ?")
        return float(result)

    def measureSupplyVoltage(self, count: int = 4) -> float:
        """
        Measures the current load voltage value

        Args:
            count: Number of measurements to average

        Returns:
            Measured voltage in volts
        """
        self.setAverageCount(count)
        result = self.sendCommandQuery("MEAS:VOLT:AC?")
        return float(result)

    def measureSupplyCurrent(self, count: int = 4) -> float:
        """
        Measures the current load current value

        Args:
            count: Number of measurements to average

        Returns:
            Measured current in amps
        """
        self.setAverageCount(count)
        result = self.sendCommandQuery("MEAS:CURR:AC?")
        return float(result)

    def disable(self) -> bool:
        """
        Puts the instrument into a safe state

        Returns:
            True if successful
        """
        try:
            return self.setOutputEnable(False) == "OK"
        except Exception as e:
            logging.error(f"Error disabling instrument: {e}")
            return False