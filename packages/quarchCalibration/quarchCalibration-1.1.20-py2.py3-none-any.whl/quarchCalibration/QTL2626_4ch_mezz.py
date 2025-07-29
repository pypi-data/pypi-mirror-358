'''
Quarch Power Module Calibration Functions
Written for Python 3.6 64 bit

M Dearman April 2019
'''

'''
Calibration Flow
    Connect to PAM Fixture 
    Connect to Keithley
    step through a set of values and get ADC vs Reference Value
    evaluate results vs defined limits

'''

#Imports QuarchPy library, providing the functions needed to use Quarch modules
from .PowerModuleCalibration import *
from .calibrationConfig import *
from .keithley_2460_control import *
from .QTL2536_6_way_switchbox import *
from quarchpy.device.device import *
from quarchpy.device.scanDevices import userSelectDevice
from quarchpy.user_interface import *
from quarchpy.user_interface import logSimpleResult
from quarchpy.utilities.BitManipulation import *
from .pamHelpers import bcdString

def parseFixtureData(response,start,length):

    # split the multiline response into a list
    response = response.splitlines()
    result = ""
    # for each line
    for line in response:
        # remove 0x, swap bytes
        line = line[4:6] + line[2:4]
        # convert 4 char Hex to 16 bit binary string
        line = "{0:016b}".format(int(line,16))
        # concatenate all the strings
        result += line
    # pick out the section we want
    result = int(result[start:(start+length)],2)
    # convert two's compliment
    if (result >= 2**(length-1)):
        result -= 2**length
    return result

def getFixtureData(device,channel):
    #hold measurement
    response = device.sendCommand("read 0x0000")
    device.sendCommand("write 0x0000 " + setBit(response,3))
    #read measurement
    data = device.sendCommand("read 0x1000 to 0x1008")
    #release measurement
    response = device.sendCommand("read 0x0000")
    device.sendCommand("write 0x0000 " + clearBit(response,3))

    if (channel == "POWER_1 V"):
        return parseFixtureData(data,0,16)
    elif (channel == "POWER_1 A"):
        return parseFixtureData(data,16,16)
    elif (channel == "POWER_2 V"):
        return parseFixtureData(data,32,16)
    elif (channel == "POWER_2 A"):
        return parseFixtureData(data,48,16)
    elif (channel == "POWER_3 V"):
        return parseFixtureData(data,64,16)
    elif (channel == "POWER_3 A"):
        return parseFixtureData(data,80,16)
    elif (channel == "POWER_4 V"):
        return parseFixtureData(data,96,16)
    elif (channel == "POWER_4 A"):
        return parseFixtureData(data,112,16)


class QTL2626 (PowerModule):

    # Fixture Register Addresses
    CAL_ADDRESSES = {
    #'SERIAL_1'						: '0xA102',	-- Mezzanine Serial Number
    #'SERIAL_2'						: '0xA103',	-- Mezzanine Serial Number
    #'SERIAL_3'						: '0xA104',	-- Mezzanine Serial Number
    'POWER_1_VOLT_MULTIPLIER'       : '0xA105',
    'POWER_1_VOLT_OFFSET'           : '0xA106',
    'POWER_1_CURR_MULTIPLIER'       : '0xA107',
    'POWER_1_CURR_OFFSET'           : '0xA108',
    #'POWER_1_LEAKAGE_MULTIPLIER'   : '0xA109',	-- Not used in 4-Channel Mezzanine
    'POWER_2_VOLT_MULTIPLIER'       : '0xA10A',
    'POWER_2_VOLT_OFFSET'           : '0xA10B',
    'POWER_2_CURR_MULTIPLIER'       : '0xA10C',
    'POWER_2_CURR_OFFSET'           : '0xA10D',
    #'POWER_2_LEAKAGE_MULTIPLIER'   : '0xA10E',	-- Not used in 4-Channel Mezzanine
    'POWER_3_VOLT_MULTIPLIER'       : '0xA10F',
    'POWER_3_VOLT_OFFSET'           : '0xA110',
    'POWER_3_CURR_MULTIPLIER'       : '0xA111',
    'POWER_3_CURR_OFFSET'           : '0xA112',
    #'POWER_3_LEAKAGE_MULTIPLIER'   : '0xA113',	-- Not used in 4-Channel Mezzanine
    'POWER_4_VOLT_MULTIPLIER'       : '0xA114',
    'POWER_4_VOLT_OFFSET'           : '0xA115',
    'POWER_4_CURR_MULTIPLIER'       : '0xA116',
    'POWER_4_CURR_OFFSET'           : '0xA117',
    'CALIBRATION_COMPLETE'          : '0xA118'
    }

    CAL_CONTROL_SETTINGS = {
    'POWER_1_CALIBRATION_CONTROL_SETTING'	: '0x00F0',	#set full averaging
    'POWER_2_CALIBRATION_CONTROL_SETTING'	: '0x00F0',	#set full averaging
    'POWER_3_CALIBRATION_CONTROL_SETTING'	: '0x00F0',	#set full averaging
    'POWER_4_CALIBRATION_CONTROL_SETTING'	: '0x00F0'	#set full averaging
	}

    CALIBRATION_MODE_ADDR           = '0xA100'
    CALIBRATION_CONTROL_ADDR        = '0xA101'
    LOAD_VOLTAGE					= 12000

    host_switchbox_title = "12V Switchbox"
    host_switchbox_message = "Select the switch box which connects a 12V supply to POWER IN:"
    host_switchbox_mapping = {'12V':'A','POWER_1_IN':'1','POWER_2_IN':'2','POWER_3_IN':'3','POWER_4_IN':'4'}

    load_switchbox_title = "Load Switchbox"
    load_switchbox_message = "Select the switch box which connects a Keithley 2460 SourceMeter to POWER OUT:"
    load_switchbox_mapping = {'LOAD':'A','POWER_1_OUT':'1','POWER_2_OUT':'2','POWER_3_OUT':'3','POWER_4_OUT':'4'}

    # Fixture Information
    PAMSerial = None
    FixtureSerial = None
    calObjectSerial = None     # The serial number of the device that is being calibrated, i.e QTL1944 in HD PPM, Fixture in PAM
    idnStr = None
    Firmware = None
    Fpga = None
    calInstrument = None
    calInstrumentId = None
    host_switchbox = None
    load_switchbox = None
    waitComplete = False
    checkedWiring = False

    def __init__(self,dut):

        # set the name of this module
        self.name = "4-Channel Power Measurement Fixture"
        self.dut = dut
        
        # Serial numbers (ensure QTL at start)
        self.enclosureSerial = self.dut.sendCommand("*ENCLOSURE?")
        if (self.enclosureSerial.find ("QTL") == -1):
            self.enclosureSerial = "QTL" + self.enclosureSerial
        # fetch the enclosure position
        self.enclosurePosition = self.dut.sendCommand("*POSITION?")
        self.PAMSerial = self.dut.sendCommand ("*SERIAL?")
        if (self.PAMSerial.find ("QTL") == -1):
            self.PAMSerial = "QTL" + self.PAMSerial
        # Fixture Serial
        # fixture serial is retrieved as BCD, we need to convert and pad it
        self.FixtureSerial = "QTL" + bcdString(dut.sendCommand("read 0xA102"),4) + "-" + bcdString(dut.sendCommand("read 0xA103"),2) + "-" + bcdString(dut.sendCommand("read 0xA104"),3) # TODO: this should be replaced with fix:serial? command when implemented
        # calObjectSerial Serial
        self.calObjectSerial = self.FixtureSerial
        # Filename String
        self.filenameString = self.FixtureSerial
        # Code version (FPGA)
        self.idnStr = dut.sendCommand ("*IDN?")
        pos = self.idnStr.upper().find ("FPGA 1:")
        if (pos != -1):
            versionStr = self.idnStr[pos+7:]
            pos = versionStr.find ("\n")
            if (pos != -1):
                versionStr = versionStr[:pos].strip()
            else:
                pass
        else:
            versionStr = "NOT-FOUND"    
        self.Fpga = versionStr.strip()
    
        # Code version (FW)    
        pos = self.idnStr.upper().find ("PROCESSOR:")
        if (pos != -1):
            versionStr = self.idnStr[pos+10:]
            pos = versionStr.find ("\n")
            if (pos != -1):
                versionStr = versionStr[:pos].strip()            
            else:
                pass
        else:
            versionStr = "NOT-FOUND"    
        self.Firmware = versionStr.strip()

        self.calibrations = {}
        # populate POWER_1 channel with calibrations
        self.calibrations["POWER_1"] = {
            "Voltage":self.QTL2626_VoltageCalibration(self,"POWER_1"),
            "Current":self.QTL2626_CurrentCalibration(self,"POWER_1")
            }
        # populate POWER_2 channel with calibrations
        self.calibrations["POWER_2"] = {
            "Voltage":self.QTL2626_VoltageCalibration(self,"POWER_2"),
            "Current":self.QTL2626_CurrentCalibration(self,"POWER_2")
            }
        # populate POWER_3 channel with calibrations
        self.calibrations["POWER_3"] = {
            "Voltage":self.QTL2626_VoltageCalibration(self,"POWER_3"),
            "Current":self.QTL2626_CurrentCalibration(self,"POWER_3")
            }
        # populate POWER_4 channel with calibrations
        self.calibrations["POWER_4"] = {
            "Voltage":self.QTL2626_VoltageCalibration(self,"POWER_4"),
            "Current":self.QTL2626_CurrentCalibration(self,"POWER_4")
            }

        self.verifications = {}
        # populate POWER_1 channel with verifications
        self.verifications["POWER_1"] = {
            "Voltage":self.QTL2626_VoltageVerification(self,"POWER_1"),
            "Current":self.QTL2626_CurrentVerification(self,"POWER_1")
            }
        self.verifications["POWER_2"] = {
            "Voltage":self.QTL2626_VoltageVerification(self,"POWER_2"),
            "Current":self.QTL2626_CurrentVerification(self,"POWER_2")
            }
        self.verifications["POWER_3"] = {
            "Voltage":self.QTL2626_VoltageVerification(self,"POWER_3"),
            "Current":self.QTL2626_CurrentVerification(self,"POWER_3")
            }
        self.verifications["POWER_4"] = {
            "Voltage":self.QTL2626_VoltageVerification(self,"POWER_4"),
            "Current":self.QTL2626_CurrentVerification(self,"POWER_4")
            }

    def specific_requirements(self):

        reportText=""

        # select the host switchbox to use for calibration
        if "host_switchbox" in calibrationResources.keys():
            self.host_switchbox = calibrationResources["host_switchbox"]
        else:
            self.host_switchbox = get_switchbox(self.host_switchbox_message,self.host_switchbox_title,self.host_switchbox_mapping)
            calibrationResources["host_switchbox"] = self.host_switchbox

        # select the load switchbox to use for calibration
        if "load_switchbox" in calibrationResources.keys():
            self.load_switchbox = calibrationResources["load_switchbox"]
        else:
            self.load_switchbox = get_switchbox(self.load_switchbox_message,self.load_switchbox_title,self.load_switchbox_mapping)
            calibrationResources["load_switchbox"] = self.load_switchbox
        
        if self.checkedWiring != True:
            self.host_switchbox.checkWiring()
            self.load_switchbox.checkWiring()
            self.checkedWiring = True

        # Select a Keithley SMU
        # If no calibration instrument is provided, request it
        while (True):
            if (calibrationResources["loadString"] == None):
                loadString = userSelectCalInstrument(scanFilterStr="Keithley 2460", nice=True)
                # quit if necessary
                if loadString == 'quit':
                    printText("no module selected, exiting...")
                    sys.exit(0)
                else:
                    calibrationResources["loadString"] = loadString
            try:
                # Connect to the calibration instrument
                self.calInstrument = keithley2460(calibrationResources["loadString"])
                # Open the connection
                self.calInstrument.openConnection()
                self.calInstrumentId = self.calInstrument._sendCommandQuery ("*IDN?")
                break
            # In fail, allow the user to try again with a new selection
            except:
                printText("Unable to communicate with selected instrument!")
                printText("")
                calibrationResources["loadString"] = None

        # Write module specific report header to file
        reportText += "Quarch Power Analysis Module: "
        reportText += self.PAMSerial + "\n"
        reportText += "Quarch Fixture: "
        reportText += self.FixtureSerial + "\n"
        reportText += "Quarch FW Versions: "
        reportText += "FW:" + self.Firmware + ", FPGA: " + self.Fpga + "\n"
        reportText += "\n"
        reportText += "Calibration Instruments#:\n"
        reportText += self.calInstrumentId + "\n"

        # perform uptime check and write to file
        if self.waitComplete != True:
            reportText += self.wait_for_up_time(desired_up_time=600)
            self.waitComplete = True

        return reportText

    def open_module(self):

        # set unit into calibration mode
        self.dut.sendCommand("write " + self.CALIBRATION_MODE_ADDR + " 0xaa55")
        self.dut.sendCommand("write " + self.CALIBRATION_MODE_ADDR + " 0x55aa")

    def clear_calibration(self):

        # set unit into calibration mode
        self.dut.sendCommand("write " + self.CALIBRATION_MODE_ADDR + " 0xaa55")
        self.dut.sendCommand("write " + self.CALIBRATION_MODE_ADDR + " 0x55aa")

        # clear all calibration registers
        for address in self.CAL_ADDRESSES.values():
            self.dut.sendAndVerifyCommand("write " + address + " 0x0000")
        
        # write 0xaa55 to register to calibration complete register to tell module it is calibrated
        self.dut.sendAndVerifyCommand("write " + self.CAL_ADDRESSES["CALIBRATION_COMPLETE"] + " 0xaa55")
        
    def write_calibration(self):

        # write the calibration registers
        # erase the tag memory
        printText("Erasing TAG memory..")
        self.dut.sendCommand("write 0xa200 0x0020")
        # TODO: should check for completion here...
        # wait for 2 seconds for erase to complete
        # check busy
        while checkBit(self.dut.sendCommand("read 0xa200"),8):
            time.sleep(0.1)
        # write the tag memory
        printText("Programming TAG memory...")
        self.dut.sendCommand("write 0xa200 0x0040")        
        # check busy
        while checkBit(self.dut.sendCommand("read 0xa200"),8):
            time.sleep(0.1)

    def close_module(self):

        # reset the fixture FPGA
        self.dut.sendCommand("fixture:reset")

        #close the connection to the calibration instrument
        self.calInstrument.closeConnection()

    def close_all(self):

        #close all attached devices
        self.calInstrument.disable()
        self.calInstrument.closeConnection()
        self.host_switchbox.disable()
        self.host_switchbox.closeConnection()
        self.load_switchbox.disable()
        self.load_switchbox.closeConnection()

    class QTL2626Calibration (Calibration):

        def __init__(self):
            super().__init__()

        def init_cal(self,voltage):

            # TODO: No Power control at the moment
            # power up
            #self.powerModule.dut.sendAndVerifyCommand("power up")

            # set averaging to max
            self.powerModule.dut.sendAndVerifyCommand("rec:ave 32k")

            #Turn off compression and power up
            self.powerModule.dut.sendAndVerifyCommand("write 0xA010 0x0011")

            # set module into calibration mode (again?)
            self.powerModule.dut.sendCommand("write " + self.powerModule.CALIBRATION_MODE_ADDR + " 0xaa55")   # will not verify
            self.powerModule.dut.sendCommand("write " + self.powerModule.CALIBRATION_MODE_ADDR + " 0x55aa")   # will not verify

            #Reset Keithley
            self.powerModule.calInstrument.reset()

        # check connections to host power and load
        def checkLoadVoltage(self,voltage,tolerance):

            self.powerModule.calInstrument.setReferenceCurrent(0)
            result = self.powerModule.calInstrument.measureLoadVoltage()*1000   # *1000 because we use mV but keithley uses volts
            # check result is in required range
            if (result >= voltage-tolerance) and (result <= voltage+tolerance):
                return True
            else:
                return False

        def finish_cal(self):

            #turn off load
            self.powerModule.calInstrument.disable()

            #turn off switch
            self.powerModule.host_switchbox.setConnections([]) #sendCommand("connect off")
            self.powerModule.load_switchbox.setConnections([]) #sendCommand("connect off")

            # turn dut to autoranging
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CALIBRATION_CONTROL_ADDR + " 0x00F0")

        def report(self, action, data):
            report = []
            reportTable = []

            # Add report header
            report.append(
                "\tPass Level  +/-(" + str(self.absErrorLimit) + self.units + " + " + str(self.relErrorLimit) + "%)\n")

            # Determine table headers based on action type
            if action == "calibrate":
                tableHeaders = ['Set Value', 'Reference', 'Raw Value', 'Result', 'Error', '+/-(Abs Error,% Error)',
                                'Pass']
            elif action == "verify":
                tableHeaders = ['Set Value', 'Reference', 'Result', 'Error', '+/-(Abs Error,% Error)', 'Pass']

            # Initialize worst-case error tracking
            worstAbsError = 0
            worstRelError = 0
            worstCase = ""
            overallResult = True

            # Process each entry in the data
            for thisLine in data:
                setValue = thisLine[2]  # Assuming thisLine[2] contains the "Set Value"
                reference = thisLine[1]
                ppmValue = thisLine[0]

                # For calibration, replace value with calibrated result
                if action == "calibrate":
                    calibratedValue = self.getResult(ppmValue)
                else:
                    calibratedValue = ppmValue

                # Calculate errors
                (actError, errorSign, absError, relError, result) = getError(reference, calibratedValue,
                                                                             self.absErrorLimit, self.relErrorLimit)

                # Update worst-case error
                if absError >= worstAbsError:
                    if relError >= worstRelError:
                        worstAbsError = absError
                        worstRelError = relError
                        worstCase = errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(
                            relError) + "%) @ " + '{:.3f}'.format(reference) + self.units

                # Update overall result
                if not result:
                    overallResult = False

                # Add data row for the table
                passfail = lambda x: "Pass" if x else "Fail"
                if action == "calibrate":
                    reportTable.append([
                        "{:.3f}".format(setValue),
                        "{:.3f}".format(reference),
                        "{:.1f}".format(ppmValue),
                        "{:.1f}".format(calibratedValue),
                        "{:.3f}".format(actError),
                        errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(relError) + "%)",
                        passfail(result)
                    ])
                elif action == "verify":
                    reportTable.append([
                        "{:.3f}".format(setValue),
                        "{:.3f}".format(reference),
                        "{:.1f}".format(ppmValue),
                        "{:.3f}".format(actError),
                        errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(relError) + "%)",
                        passfail(result)
                    ])

            # Format table into a string
            reportTable = displayTable(tableHeaders=tableHeaders, tableData=reportTable, printToConsole=False,
                                       indexReq=False, align="r")
            report.append(reportTable)

            # Add calibration details if applicable
            if action == "calibrate":
                report.append(
                    "Calculated Multiplier: " + str(self.multiplier.originalValue()) + ", Calculated Offset: " + str(
                        self.offset.originalValue()))
                report.append("Stored Multiplier: " + str(self.multiplier.storedValue()) + ", Stored Offset: " + str(
                    self.offset.storedValue()))
                report.append("Multiplier Register: " + self.multiplier.hexString(
                    4) + ", Offset Register: " + self.offset.hexString(4))

            # Add final summary
            report.append(
                "" + '{0:<35}'.format(self.title) + '     ' + '{0:>10}'.format("Passed : ") + '  ' + '{0:<5}'.format(
                    str(overallResult)) + '     ' + '{0:>11}'.format("worst case:") + '  ' + '{0:>11}'.format(
                    worstCase))
            report.append("\n\n\n")

            # Return structured report data
            return {"title": self.title, "result": overallResult, "worst case": worstCase, "report": '\n'.join(report)}

    class QTL2626_VoltageCalibration (QTL2626Calibration):

        def __init__(self,powerModule,thisChannel):

            self.thisChannel = thisChannel
            self.title = thisChannel + " Voltage Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 2                  # 2mV
            self.relErrorLimit = 1                  # 1%
            self.test_min = 40                      # 40mV
            self.test_max = 14400                   # 14.4V
            self.test_steps = 20
            self.units = "mV"
            self.scaling = 4
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = True
            self.offset_int_width = 10
            self.offset_frac_width = 6

        def init(self):

            super().init_cal(self.thisChannel)

            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_VOLT_MULTIPLIER"] + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_VOLT_OFFSET"] + " 0x0000")

            self.powerModule.host_switchbox.setConnections([("12V",None)])
            self.powerModule.load_switchbox.setConnections([("LOAD",self.thisChannel + '_OUT')])

            # Setup Keithley
            self.setup()

            # Check Host Power is present
            #while (super().checkLoadVoltage(500,500) != True):
            #    self.powerModule.setConnections("POWER_1",None,reset=True)

        def setup(self):
            self.powerModule.calInstrument.initialSetupForReferenceVoltage(currentLimit="1e-1")

        def setRef(self,value):

            self.powerModule.calInstrument.setReferenceVoltage(value/1000,currentLimit="1e-1")

        def readRef(self):

            return self.powerModule.calInstrument.measureLoadVoltage()*1000

        def readVal(self):

            return getFixtureData(self.powerModule.dut,self.thisChannel + " V")

        def setCoefficients(self):

            result1 = self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_VOLT_MULTIPLIER"] + " " + self.multiplier.hexString(4))
            result2 = self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_VOLT_OFFSET"] + " " + self.offset.hexString(4))
            if result1 and result2:
                result = True
            else:
                result = False
            logSimpleResult("Set " + self.thisChannel + " voltage", result)

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get voltage multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_VOLT_MULTIPLIER"])
            # get voltage offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_VOLT_OFFSET"])
            return coefficients

        def writeCoefficients(self,coefficients):

            # write voltage multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_VOLT_MULTIPLIER"] + " " + coefficients["multiplier"])
            # write voltage offset
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_VOLT_OFFSET"] + " " + coefficients["offset"])

    class QTL2626_CurrentCalibration (QTL2626Calibration):

        def __init__(self,powerModule,thisChannel):

            self.thisChannel = thisChannel
            self.title = thisChannel + " Current Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 10                 # 10mA
            self.relErrorLimit = 1                  # 1%
            self.test_min = 10                      # 10mA
            self.test_max = 4000                    # 4000mA
            self.test_steps = 20
            self.units = "mA"
            self.scaling = 4
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = True
            self.offset_int_width = 10
            self.offset_frac_width = 6

        def init(self):

            super().init_cal(self.thisChannel)

            #set manual range, full averaging, [thisChannel] current range
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CALIBRATION_CONTROL_ADDR + " " + self.powerModule.CAL_CONTROL_SETTINGS[self.thisChannel + "_CALIBRATION_CONTROL_SETTING"])
            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_CURR_MULTIPLIER"] + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_CURR_OFFSET"] + " 0x0000")

            self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_IN')])
            self.powerModule.load_switchbox.setConnections([("LOAD",self.thisChannel + '_OUT')])

            # Setup Keithley
            self.setup()

            # Check Host Power is present
            while (super().checkLoadVoltage(self.powerModule.LOAD_VOLTAGE,1000) != True):
                showDialog(message="Host Power not detected, please check the connections",title="Check Connections")
                self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_IN')],reset=True)
                self.powerModule.load_switchbox.setConnections([("LOAD",self.thisChannel + '_OUT')],reset=True)

        def setup(self):
            self.powerModule.calInstrument.initialSetupForReferenceCurrent()

        def setRef(self,value):

            self.powerModule.calInstrument.setReferenceCurrent(value/1000)

        def readRef(self):

            return self.powerModule.calInstrument.measureLoadCurrent()*1000# + leakage

        def readVal(self):

            return getFixtureData(self.powerModule.dut,self.thisChannel + " A")

        def setCoefficients(self):

            result1 = self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_CURR_MULTIPLIER"] + " " + self.multiplier.hexString(4))
            result2 = self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_CURR_OFFSET"] + " " + self.offset.hexString(4))
            if result1 and result2:
                result = True
            else:
                result = False
            logSimpleResult("Set " + self.thisChannel + " current", result)

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get current multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_CURR_MULTIPLIER"])
            # get current offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_CURR_OFFSET"])
            return coefficients

        def writeCoefficients(self,coefficients):

            # write current multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_CURR_MULTIPLIER"] + " " + coefficients["multiplier"])
            # write current offset
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_CURR_OFFSET"] + " " + coefficients["offset"])

    class QTL2626_VoltageVerification (QTL2626Calibration):

        def __init__(self,powerModule,thisChannel):

            self.thisChannel = thisChannel
            self.title = thisChannel + " Voltage Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 2      # 2mV
            self.relErrorLimit = 1      # 1%
            self.test_min = 40          # 40mV
            self.test_max = 14400       # 14.4V
            self.test_steps = 20
            self.units = "mV"

        def init(self):

            super().init_cal(self.thisChannel)

            self.powerModule.host_switchbox.setConnections([("12V",None)])
            self.powerModule.load_switchbox.setConnections([("LOAD",self.thisChannel + '_OUT')])

            # Setup Keithley
            self.setup()

            # Check Host Power is present
            #while (super().checkLoadVoltage(500,500) != True):
                #self.powerModule.setConnections(self.thisChannel,None,reset=True)

        def setup(self):
            self.powerModule.calInstrument.initialSetupForReferenceVoltage(currentLimit="1e-1")

        def setRef(self,value):

            self.powerModule.calInstrument.setReferenceVoltage(value/1000,currentLimit="1e-1")

        def readRef(self):

            return self.powerModule.calInstrument.measureLoadVoltage()*1000

        def readVal(self):

            return getFixtureData(self.powerModule.dut,self.thisChannel + " V")

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class QTL2626_CurrentVerification (QTL2626Calibration):

        def __init__(self,powerModule,thisChannel):

            self.thisChannel = thisChannel
            self.title = thisChannel + " Current Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 10     # 25mA  - Deliberately higher than calibration limit
            self.relErrorLimit = 1      # 1% tolerance
            self.test_min = 10          # 10mA
            self.test_max = 4000        # 4000mA
            self.test_steps = 20
            self.units = "mA"

        def init(self):

            super().init_cal(self.thisChannel)

            self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_IN')])
            self.powerModule.load_switchbox.setConnections([("LOAD",self.thisChannel + '_OUT')])

            # Setup Keithley
            self.setup()

            # Check Host Power is present
            while (super().checkLoadVoltage(self.powerModule.LOAD_VOLTAGE,1000) != True):
                showDialog(message="Host Power not detected, please check the connections",title="Check Connections")
                self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_IN')],reset=True)
                self.powerModule.load_switchbox.setConnections([("LOAD",self.thisChannel + '_OUT')],reset=True)

        def setup(self):
            self.powerModule.calInstrument.initialSetupForReferenceCurrent()

        def setRef(self,value):

            self.powerModule.calInstrument.setReferenceCurrent(value/1000)

        def readRef(self):

            return self.powerModule.calInstrument.measureLoadCurrent()*1000

        def readVal(self):

            return getFixtureData(self.powerModule.dut,self.thisChannel + " A")

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)