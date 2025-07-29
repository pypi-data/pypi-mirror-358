import socket
import unittest
import time
import logging
import os
import re
import threading
from enum import Enum


class CommandStatus(Enum):
    IDLE = 0
    EXECUTING = 1
    COMPLETED = 2
    ERROR = 3


class ElpaSine:
    def __init__(self, addr):
        self.TIMEOUT = 10
        self.BUFFER_SIZE = 4096
        self.connection = None
        self.addr = addr
        self.numeric = re.compile("(\+|-)([0-9\.]+)")
        self.measurementType = "RMS"
        self.measurementTypeList = ["PEAK", "RMS"]
        self.maxCurrentLimit = 10.0
        self.isOpen = False
        self.commandDelay = 0.05  # Basic delay between commands
        self.pollInterval = 0.1  # Interval for polling command status
        self.maxPollAttempts = 50  # Maximum number of polling attempts
        self.lastResult = None
        self.conString = None
        self.commandStatus = CommandStatus.IDLE
        self.commandLock = threading.Lock()  # Lock for command execution
        self.validCommands = {
            "MEAS:TYPE": ["PEAK", "RMS"],
            "STAT:MODE": ["CC", "CV", "CR", "CP", "LIN"],
            "PRES:FREQ": ["AUTO", "50", "60"],
            "STAT:LOAD": ["ON", "OFF"],
        }

    def validateCommand(self, command):
        """Validate command syntax and parameters"""
        parts = command.split()
        baseCmd = parts[0]

        # Check if command contains a parameter
        if len(parts) > 1 and ":" in baseCmd:
            cmdPrefix = baseCmd.split(":")[0] + ":" + baseCmd.split(":")[1]
            if cmdPrefix in self.validCommands:
                param = parts[1]
                if param not in self.validCommands[cmdPrefix]:
                    logging.warning(
                        f"Parameter '{param}' not in valid list for command '{cmdPrefix}': {self.validCommands[cmdPrefix]}")
                    # Still proceed with the command - just warn

        # Check for numeric range on current setting
        if "PRES:CC:A" in command or "PRES:LIN:A" in command:
            try:
                value = float(parts[1])
                if value > self.maxCurrentLimit:
                    raise ValueError(f"Current setting {value}A exceeds maximum limit of {self.maxCurrentLimit}A")
            except IndexError:
                raise ValueError(f"Missing value for current setting command: {command}")
            except ValueError as e:
                if "exceeds maximum" in str(e):
                    raise
                raise ValueError(f"Invalid numeric value in command: {command}")

        return True

    def openConnection(self, connectionString=None):
        logging.info("Opening connection to ELPA-SINE")
        if connectionString is not None:
            self.conString = connectionString
        else:
            self.conString = self.addr

        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.settimeout(self.TIMEOUT)
        try:
            self.connection.connect((self.conString, 4001))
            self.isOpen = True

            # ELPA-SINE ignores first command, so send a dummy command to wake it up
            self.sendCommandQuery("MEAS:TYPE " + self.measurementType, response=False)

            # Verify connection is working by requesting device ID
            id_response = self.sendCommandQuery("*IDN?")
            if not id_response or "ELPA-SINE" not in id_response:
                logging.error(f"Failed to verify ELPA-SINE connection: {id_response}")
                self.closeConnection()
                raise ConnectionError("Failed to verify ELPA-SINE connection")

            logging.info(f"Connected to {id_response}")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to ELPA-SINE at {self.conString}: {str(e)}")
            if self.connection:
                self.connection.close()
            self.isOpen = False
            raise

    def closeConnection(self):
        logging.info("Closing connection to ELPA-SINE")
        if self.isOpen and self.connection:
            self.connection.close()
        self.isOpen = False

    def closeDeadConnections(self):
        """Close any dead connections"""
        # This method was referenced in the original but not implemented
        # Here's a basic implementation
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
        self.connection = None
        self.isOpen = False

    def sendCommandQuery(self, commandString, response=True, verify=True):
        """Send a command and optionally wait for a response"""
        if not self.isOpen:
            self.openConnection()

        try:
            # Validate the command
            # if verify:
            #     self.validateCommand(commandString)
            with self.commandLock:
                self.commandStatus = CommandStatus.EXECUTING

                # Apply command delay
                time.sleep(self.commandDelay)

                # Send the command
                startTime = int(round(time.time() * 1000))
                logging.debug(f"{os.path.basename(__file__)}: sending command: {commandString}")
                self.connection.send((commandString + "\r\n").encode('latin-1'))

                # If no response is expected, return immediately
                if not response:
                    self.commandStatus = CommandStatus.COMPLETED
                    return None

                # Read back the response data
                self.connection.settimeout(self.TIMEOUT)
                resultStr = self.connection.recv(self.BUFFER_SIZE).decode("utf-8")
                self.lastResult = resultStr
                endTime = int(round(time.time() * 1000))

                logging.debug(f"{os.path.basename(__file__)}: received: {resultStr}")
                logging.debug(f"{os.path.basename(__file__)}: Time Taken: {endTime - startTime} mS")

                resultStr = resultStr.strip('\r\n\t')

                # If no response came back
                if resultStr is None or resultStr == "":
                    self.commandStatus = CommandStatus.ERROR
                    logging.error(f"Empty response for command: {commandString}")
                    raise ValueError("The ELPA-SINE did not return a response")

                self.commandStatus = CommandStatus.COMPLETED
                return resultStr

        except socket.timeout:
            self.commandStatus = CommandStatus.ERROR
            logging.warning(f"{os.path.basename(__file__)}: ELPA-SINE command timed out: {commandString}")
            # Handle timeout by trying to reconnect
            self._reconnect()
            raise TimeoutError(
                f"{os.path.basename(__file__)}: timed out while expecting a response for command: {commandString}")
        except Exception as e:
            self.commandStatus = CommandStatus.ERROR
            logging.error(f"Error executing command '{commandString}': {str(e)}")
            raise

    def _reconnect(self):
        """Attempt to reconnect to the device"""
        logging.info("Attempting to reconnect to ELPA-SINE")
        try:
            if self.isOpen:
                self.closeConnection()
            self.closeDeadConnections()
            self.openConnection()
            return True
        except Exception as e:
            logging.error(f"Failed to reconnect: {str(e)}")
            return False

    def waitForCommandCompletion(self, timeout=5):
        """Poll for command completion based on device status"""
        start_time = time.time()
        polling_attempts = 0

        while time.time() - start_time < timeout and polling_attempts < self.maxPollAttempts:
            # Check if the command is completed
            if self.commandStatus == CommandStatus.COMPLETED:
                return True

            # Check if the command resulted in an error
            if self.commandStatus == CommandStatus.ERROR:
                logging.error("Command execution failed")
                return False

            # Poll the device status
            try:
                status = self.sendCommandQuery("STAT?", verify=False)
                # Check if the device is in a stable state (implementation depends on device behavior)
                # For ELPA-SINE, we need to check the status response format
                if status and ("READY" in status or "IDLE" in status):
                    self.commandStatus = CommandStatus.COMPLETED
                    return True
            except Exception as e:
                logging.warning(f"Failed to poll device status: {str(e)}")

            time.sleep(self.pollInterval)
            polling_attempts += 1

        logging.warning("Command completion polling timed out")
        return False

    def executeCommand(self, command, response=False, verify=True, wait_for_completion=True):
        """Execute a command with verification and optional waiting for completion"""
        result = self.sendCommandQuery(command, response=response, verify=verify)

        if wait_for_completion:
            self.waitForCommandCompletion()

        return result

    def getMeasurement(self, command, measType="RMS"):
        """Get a measurement with the specified type"""
        # If selected measurement type is not the current measurement type, switch the measurement mode
        if self.measurementType != measType and measType in self.measurementTypeList:
            self.measurementType = measType
            self.executeCommand(f"MEAS:TYPE {measType}", response=False)

        # Make sure averaging is set properly
        self.executeCommand("PRES:AVG 16", response=False)

        # Get the measurement
        result = self.executeCommand(command, response=True)

        # Parse the result
        mobj = self.numeric.match(result.strip())
        if mobj:
            if mobj.group(1) == "-":
                return -float(mobj.group(2))
            else:
                return float(mobj.group(2))
        else:
            raise ValueError(
                f"{os.path.basename(__file__)}: unable to parse numeric value {result.strip()} from ELPA-SINE")

    def getVoltageMeasurement(self, measType="RMS"):
        """Get voltage measurement"""
        return self.getMeasurement("MEAS:VOLT?", measType=measType)

    def getCurrentMeasurement(self, measType="RMS"):
        """Get current measurement"""
        rv = self.getMeasurement("MEAS:CURR?", measType=measType)
        return rv

    def getPowerMeasurement(self, measType="Active"):
        """Get power measurement"""
        rv = self.getMeasurement("MEAS:POW?")
        return rv

    def setLoadCurrent(self, value):
        """Set the load current"""
        if value > self.maxCurrentLimit:
            raise ValueError(f"ERROR - ELPA-SINE should not be set to more than {self.maxCurrentLimit} A")
        else:
            # Execute commands in sequence with validation
            self.executeCommand("STAT:MODE:CC", response=False)
            self.executeCommand("PRES:FREQ AUTO", response=False)
            self.executeCommand("PRES:CC:A {0:3.1f}".format(value), response=False)

            # Verify the current was set correctly
            time.sleep(0.5)  # Allow time for the setting to take effect
            actual_current = self.getCurrentMeasurement()
            if abs(actual_current) < 0.1 and value > 0.1:
                logging.warning(f"Current setting verification failed: Expected ~{value}A, got {actual_current}A")

            return actual_current

    def setOutputEnable(self, enableState):
        """Enable/disable the outputs"""
        if enableState:
            # Turn on the load
            self.executeCommand("STAT:LOAD ON", response=False)

            # Verify load is on
            attempts = 3
            while attempts > 0:
                if self.getOutputEnable():
                    return True
                time.sleep(0.5)
                attempts -= 1

            logging.warning("Failed to verify load is enabled")
            return False
        else:
            # Turn off the load
            self.executeCommand("STAT:LOAD OFF", response=False)

            # Verify load is off
            attempts = 3
            while attempts > 0:
                if not self.getOutputEnable():
                    return True
                time.sleep(0.5)
                attempts -= 1

            logging.warning("Failed to verify load is disabled")
            return False

    def getOutputEnable(self):
        """Return the output enable state as a boolean"""
        result = self.executeCommand("STAT:LOAD?", response=True)
        try:
            return int(result) == 1
        except ValueError:
            logging.error(f"Invalid response for output state: {result}")
            return False

    def reset(self):
        """Reset the device to a known state"""
        # Added for compatibility with Keithley, but implemented for ELPA-SINE
        logging.info("Resetting ELPA-SINE")
        try:
            # Ensure load is off
            self.setOutputEnable(False)

            # Reset measurement settings
            self.executeCommand("MEAS:TYPE RMS", response=False)
            self.executeCommand("PRES:AVG 16", response=False)
            self.executeCommand("PRES:FREQ AUTO", response=False)

            # Reset operating mode
            self.executeCommand("STAT:MODE:CC", response=False)
            self.executeCommand("PRES:CC:A 0.0", response=False)

            return True
        except Exception as e:
            logging.error(f"Error during reset: {str(e)}")
            return False

    def getDeviceStatus(self):
        """Get the current device status"""
        try:
            status = self.executeCommand("STAT?", response=True)
            return status
        except Exception as e:
            logging.error(f"Error getting device status: {str(e)}")
            return None

    def waitForStableReading(self, measurement_func, target_value=None, tolerance=0.1, timeout=10):
        """Wait for a stable reading from the specified measurement function"""
        start_time = time.time()
        last_readings = []

        while time.time() - start_time < timeout:
            try:
                reading = measurement_func()
                last_readings.append(reading)

                # Keep only the last 3 readings
                if len(last_readings) > 3:
                    last_readings.pop(0)

                # Check if we have enough readings
                if len(last_readings) >= 3:
                    # Check if readings are stable
                    if max(last_readings) - min(last_readings) < tolerance:
                        # If target value is provided, check if readings are close to target
                        if target_value is None or abs(
                                sum(last_readings) / len(last_readings) - target_value) < tolerance:
                            return sum(last_readings) / len(last_readings)

            except Exception as e:
                logging.warning(f"Error during stable reading wait: {str(e)}")

            time.sleep(0.5)

        logging.warning("Timed out waiting for stable reading")
        if last_readings:
            return sum(last_readings) / len(last_readings)
        return None

    @staticmethod
    def discover():
        """Discover Elpa-sine devices through UDP broadcast"""
        logging.info("Searching for Elpa-Sine AC loads")

        devices = []
        ipList = socket.gethostbyname_ex(socket.gethostname())
        logging.debug(f"{os.path.basename(__file__)}: Discovered interfaces: {ipList}")

        responses = []

        for ip in ipList[2]:
            logging.debug(f"{os.path.basename(__file__)}: Broadcasting on: {ip}")

            try:
                tsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                tsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                tsock.settimeout(1)
                tsock.bind((ip, 56732))
                tsock.sendto(b'C!09               \n', ('255.255.255.255', 36))

                # Receive messages until timeout
                while True:
                    try:
                        responses.append(tsock.recvfrom(1024))
                    except socket.timeout:
                        break
                    except Exception as e:
                        logging.error(f"Error receiving discovery response: {str(e)}")
                        break

            except Exception as e:
                logging.error(f"Error during discovery on interface {ip}: {str(e)}")
            finally:
                try:
                    tsock.close()
                except:
                    pass

        logging.debug(f"{os.path.basename(__file__)}: Received responses: {responses}")

        # Parse each response
        for response in responses:
            try:
                data = response[0]
                if len(data) < 20:
                    logging.warning(f"Discovery response too short: {data}")
                    continue

                prefix = data[0:4]
                ip_addr = ".".join([str(x) for x in data[4:8]])
                mask = ".".join([str(x) for x in data[8:12]])
                mac = ":".join([format(x, '02X') for x in data[12:18]])
                device = (int(data[18]) << 8) + int(data[19])

                if prefix == b'C!09':
                    devices.append({"prefix": prefix, "ip": ip_addr, "mask": mask, "mac": mac, "device": device})
                else:
                    logging.warning(f"Unknown prefix in discovery response: {prefix}")
            except Exception as e:
                logging.error(f"Error parsing discovery response: {str(e)}")

        return devices