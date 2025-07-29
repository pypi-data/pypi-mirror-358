'''
Quarch Power Module Calibration Functions
Written for Python 3.6 64 bit

M Dearman April 2019
'''
import time

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
    data = device.sendCommand("read 0x1000 to 0x1007")
    #release measurement
    response = device.sendCommand("read 0x0000")
    device.sendCommand("write 0x0000 " + clearBit(response,3))

    if (channel == "POWER_1 V"):
        return parseFixtureData(data,0,16)
    elif (channel == "POWER_1 A"):
        return parseFixtureData(data,16,25)
    elif (channel == "POWER_2 V"):
        return parseFixtureData(data,41,16)
    elif (channel == "POWER_2 A"):
        return parseFixtureData(data,57,25)


class QTL2621 (PowerModule):

    # Fixture Register Addresses
    CAL_ADDRESSES = {
    #'SERIAL_1'						: '0xA102',	-- Mezzanine Serial Number
    #'SERIAL_2'						: '0xA103',	-- Mezzanine Serial Number
    #'SERIAL_3'						: '0xA104',	-- Mezzanine Serial Number
    'POWER_1_VOLT_MULTIPLIER'		: '0xA105',
    'POWER_1_VOLT_OFFSET'			: '0xA106',
    'POWER_1_HIGH_MULTIPLIER'		: '0xA107',
    'POWER_1_HIGH_OFFSET'			: '0xA108',
    #'POWER_1_LEAKAGE_MULTIPLIER'	: '0xA109',	-- Not used in 2-Channel Mezzanine
    'POWER_2_VOLT_MULTIPLIER'		: '0xA10A',
    'POWER_2_VOLT_OFFSET'			: '0xA10B',
    'POWER_2_HIGH_MULTIPLIER'		: '0xA10C',
    'POWER_2_HIGH_OFFSET'			: '0xA10D',
    #'POWER_2_LEAKAGE_MULTIPLIER'	: '0xA10E',	-- Not used in 2-Channel Mezzanine
    #'POWER_3_VOLT_MULTIPLIER'		: '0xA10F',	-- Not used in 2-Channel Mezzanine
    #'POWER_3_VOLT_OFFSET'			: '0xA110',	-- Not used in 2-Channel Mezzanine
    'POWER_1_LOW_MULTIPLIER'		: '0xA111',
    'POWER_1_LOW_OFFSET'			: '0xA112',
    #'POWER_3_LEAKAGE_MULTIPLIER'   : '0xA113',	-- Not used in 2-Channel Mezzanine
    #'POWER_4_VOLT_MULTIPLIER'		: '0xA114',	-- Not used in 2-Channel Mezzanine
    #'POWER_4_VOLT_OFFSET'			: '0xA115',	-- Not used in 2-Channel Mezzanine
    'POWER_2_LOW_MULTIPLIER'		: '0xA116',
    'POWER_2_LOW_OFFSET'			: '0xA117',
    'CALIBRATION_COMPLETE'			: '0xA118'
    }

    CAL_CONTROL_SETTINGS = {
    'POWER_1_LOW_CALIBRATION_CONTROL_SETTING'   : '0x00F1',  #set manual range, full averaging, POWER_1 low current mode, POWER_2 auto
    'POWER_2_LOW_CALIBRATION_CONTROL_SETTING'   : '0x00F4',  #set manual range, full averaging, POWER_2 low current mode, POWER_1 auto
    'POWER_1_HIGH_CALIBRATION_CONTROL_SETTING'  : '0x00F2',  #set manual range, full averaging, POWER_1 high current mode, POWER_2 auto
    'POWER_2_HIGH_CALIBRATION_CONTROL_SETTING'  : '0x00F8'  #set manual range, full averaging, POWER_2 high current mode, POWER_1 auto
	}

    CALIBRATION_MODE_ADDR           = '0xA100'
    CALIBRATION_CONTROL_ADDR        = '0xA101'
    LOAD_VOLTAGE					= 12000

    # Dictionaries to set limits for noise test
    has_noise_test = True
    channel_dict_delta_limits = {"POWER_1 mV":"20", "POWER_2 mV":"20", "POWER_1 uA" : "1500","POWER_2 uA":"1500"}
    channel_dict_average_limits = {"POWER_1 mV":"2", "POWER_2 mV":"2", "POWER_1 uA" : "200","POWER_2 uA":"200"}
    channel_dict_rms_limits = {"POWER_1 mV":"8", "POWER_2 mV":"8", "POWER_1 uA" : "700","POWER_2 uA":"300"}

    host_switchbox_title = "12V Switchbox"
    host_switchbox_message = "Select the switch box which connects a 12V supply to POWER IN:"
    host_switchbox_mapping = {'12V':'A','POWER_1_IN':'1','POWER_2_IN':'2','LOAD':'B','POWER_1_OUT':'4','POWER_2_OUT':'5'}

    load_switchbox_title = "Load Switchbox"
    load_switchbox_message = "Select the switch box which connects a Keithley 2460 SourceMeter to POWER OUT:"
    load_switchbox_mapping = {'LOAD':'A','POWER_1_OUT':'1','POWER_2_OUT':'2'}

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
        self.name = "2-Channel Power Measurement Fixture"
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
            "Voltage":self.QTL2621_VoltageCalibration(self,"POWER_1"),
            "Low Current":self.QTL2621_LowCurrentCalibration(self,"POWER_1"),
            "High Current":self.QTL2621_HighCurrentCalibration(self,"POWER_1")
            }
        # populate POWER_2 channel with calibrations
        self.calibrations["POWER_2"] = {
            "Voltage":self.QTL2621_VoltageCalibration(self,"POWER_2"),
            "Low Current":self.QTL2621_LowCurrentCalibration(self,"POWER_2"),
            "High Current":self.QTL2621_HighCurrentCalibration(self,"POWER_2")
            }

        self.verifications = {}
        # populate POWER_1 channel with verifications
        self.verifications["POWER_1"] = {
            "Voltage":self.QTL2621_VoltageVerification(self,"POWER_1"),
            "Low Current":self.QTL2621_LowCurrentVerification(self,"POWER_1"),
            "High Current":self.QTL2621_HighCurrentVerification(self,"POWER_1")
            }
        # populate POWER_2 channel with verifications
        self.verifications["POWER_2"] = {
            "Voltage":self.QTL2621_VoltageVerification(self,"POWER_2"),
            "Low Current":self.QTL2621_LowCurrentVerification(self,"POWER_2"),
            "High Current":self.QTL2621_HighCurrentVerification(self,"POWER_2")
            }

    def specific_requirements(self):

        reportText=""

        # select the host switchbox to use for calibration
        if "host_switchbox" in calibrationResources.keys():
            self.host_switchbox = calibrationResources["host_switchbox"]
        else:
            self.host_switchbox = get_switchbox(self.host_switchbox_message,self.host_switchbox_title,self.host_switchbox_mapping)
            calibrationResources["host_switchbox"] = self.host_switchbox

        # DEPRECATED - The 2-Channel Mezzanine device class was changed to use only one switchbox.
        # # select the load switchbox to use for calibration
        # if "load_switchbox" in calibrationResources.keys():
        #     self.load_switchbox = calibrationResources["load_switchbox"]
        # else:
        #     self.load_switchbox = get_switchbox(self.load_switchbox_message,self.load_switchbox_title,self.load_switchbox_mapping)
        #     calibrationResources["load_switchbox"] = self.load_switchbox
        
        if self.checkedWiring != True:
            self.host_switchbox.checkWiring()
            # self.load_switchbox.checkWiring()
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

    class QTL2621Calibration (Calibration):

        def __init__(self):
            super().__init__()

        def init_cal(self,voltage):

            # TODO: No Power control at the moment
            # power up
            # self.powerModule.dut.sendAndVerifyCommand("power up")

            # set averaging to max
            # Check that rec:ave 32k can be set (module could be streaming on QPS?)
            try:
                self.powerModule.dut.sendAndVerifyCommand("rec:ave 32k")
            except:
                logWarning("Warning! Unable to set record averaging.")

            # Turn off compression and power up
            self.powerModule.dut.sendAndVerifyCommand("write 0xA010 0x0011")

            # set module into calibration mode (again?)
            self.powerModule.dut.sendCommand("write " + self.powerModule.CALIBRATION_MODE_ADDR + " 0xaa55")   # will not verify
            self.powerModule.dut.sendCommand("write " + self.powerModule.CALIBRATION_MODE_ADDR + " 0x55aa")   # will not verify

            # Reset Keithley
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
            # self.powerModule.add_comment("Set connections off for 12V switchbox")
            # self.powerModule.host_switchbox.setConnections([]) #sendCommand("connect off")
            # self.powerModule.add_comment("Set connections off for Load switchbox")
            # self.powerModule.load_switchbox.setConnections([]) #sendCommand("connect off")
            #turn off switch
            self.powerModule.host_switchbox.setConnections([]) #sendCommand("connect off")

            # Default averaging (32k)
            default_aver = "0x00F0"
            # turn dut to autoranging
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CALIBRATION_CONTROL_ADDR + " " + str(default_aver))

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

            # Zero worst-case error variables
            worstAbsError = 0
            worstRelError = 0
            worstCase = ""
            overallResult = True

            # Process each line in the data
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

                # Compare and update worst-case error
                if absError >= worstAbsError:
                    if relError >= worstRelError:
                        worstAbsError = absError
                        worstRelError = relError
                        worstCase = errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(
                            relError) + "%) @ " + '{:.3f}'.format(reference) + self.units

                # Update overall pass/fail status
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

            # Add calibration details if action is "calibrate"
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

            # Return final report
            return {"title": self.title, "result": overallResult, "worst case": worstCase, "report": '\n'.join(report)}

    class QTL2621_VoltageCalibration (QTL2621Calibration):

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

            # Ensure it's set to auto range
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CALIBRATION_CONTROL_ADDR + " " + "0x00F0")

            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_VOLT_MULTIPLIER"] + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_VOLT_OFFSET"] + " 0x0000")

            # DEPRECATED - changed to use only one switchbox...
            # self.powerModule.add_comment("Setting Connections for 12V Switchbox")
            # self.powerModule.host_switchbox.setConnections([("12V",None)])
            # self.powerModule.add_comment("Setting Connections for Load Switchbox")
            # self.powerModule.load_switchbox.setConnections([("LOAD",self.thisChannel + '_OUT')])

            self.powerModule.host_switchbox.setConnections([("12V",None),("LOAD",self.thisChannel + "_OUT")])

            self.setup()

            # Check Host Power is present
            # while (super().checkLoadVoltage(500,500) != True):
            #    self.powerModule.setConnections("POWER_1",None,reset=True)

            # Setup moved to init
            self.powerModule.calInstrument.setAverageVoltageCount(4)

        def setup(self):
            self.powerModule.calInstrument.initialSetupForReferenceVoltage(currentLimit="1e-1")

        def setRef(self, value):

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

    class QTL2621_LowCurrentCalibration (QTL2621Calibration):

        def __init__(self,powerModule,thisChannel):

            self.thisChannel = thisChannel
            self.title = thisChannel + " Low Current Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 15                 # 15uA
            self.relErrorLimit = 1                  # 1%
            self.test_min = 10                      # 10uA
            self.test_max = 85000                   # 85mA
            self.test_steps = 20
            self.units = "uA"
            self.scaling = 32
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = True
            self.offset_int_width = 10
            self.offset_frac_width = 6

        def init(self):

            super().init_cal(self.thisChannel)
            # Default averaging (32k)
            default_aver = self.powerModule.CAL_CONTROL_SETTINGS[self.thisChannel + "_LOW_CALIBRATION_CONTROL_SETTING"]
            # turn dut to autoranging
            # set manual range, full averaging, [thisChannel] current range
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CALIBRATION_CONTROL_ADDR + " " + default_aver)
            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_LOW_MULTIPLIER"] + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_LOW_OFFSET"] + " 0x0000")

            # self.powerModule.add_comment("Setting connection for 12V switchbox")
            # self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_IN')])
            # self.powerModule.add_comment("Setting connection for Load switchbox")
            # self.powerModule.load_switchbox.setConnections([("LOAD", self.thisChannel + '_OUT')])
            self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_IN'),("LOAD",self.thisChannel + '_OUT')])

            # turn off switch
            # self.powerModule.host_switchbox.setConnections([])  # sendCommand("connect off")
            # self.powerModule.load_switchbox.setConnections([]) # sendCommand("connect off"
            self.setup()

            # Check Host Power is present
            while (super().checkLoadVoltage(self.powerModule.LOAD_VOLTAGE,1000) != True):
                showDialog(message="Host Power not detected, please check the connections",title="Check Connections")
                # self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_IN')],reset=True)
                # self.powerModule.load_switchbox.setConnections([("LOAD",self.thisChannel + '_OUT')],reset=True)
                self.powerModule.host_switchbox.setConnections([("12V", self.thisChannel + '_IN'), ("LOAD", self.thisChannel + '_OUT')])

            self.powerModule.calInstrument.setAverageCurrentCount(measCount=4)

        def setup(self):

            self.powerModule.calInstrument.initialSetupForReferenceCurrent()

        def setRef(self,value):

            self.powerModule.calInstrument.setReferenceCurrent(value/1000000)

        def readRef(self):

            return self.powerModule.calInstrument.measureLoadCurrent()*1000000# + leakage

        def readVal(self):

            return getFixtureData(self.powerModule.dut,self.thisChannel + " A")

        def setCoefficients(self):

            result1 = self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_LOW_MULTIPLIER"] + " " + self.multiplier.hexString(4))
            result2 = self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_LOW_OFFSET"] + " " + self.offset.hexString(4))
            if result1 and result2:
                result = True
            else:
                result = False
            logSimpleResult("Set " + self.thisChannel + " low current", result)

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get low current multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_LOW_MULTIPLIER"])
            # get low current offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_LOW_OFFSET"])
            return coefficients

        def writeCoefficients(self,coefficients):

            # write low current multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_LOW_MULTIPLIER"] + " " + coefficients["multiplier"])
            # write low current offset
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_LOW_OFFSET"] + " " + coefficients["offset"])

    class QTL2621_HighCurrentCalibration (QTL2621Calibration):

        def __init__(self,powerModule,thisChannel):

            self.thisChannel = thisChannel
            self.title = thisChannel + " High Current Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 2000               # 2mA
            self.relErrorLimit = 1                  # 1%
            self.test_min = 1000                    # 1mA
            self.test_max = 4000000                 # 4A
            self.test_steps = 20
            self.units = "uA"
            self.scaling = 2048
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = True
            self.offset_int_width = 10
            self.offset_frac_width = 6

        def init(self):

            super().init_cal(self.thisChannel)

            #set manual range, full averaging, [thisChannel] high current mode, other channels all off (so we can detect we're connected to the wrong channel
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CALIBRATION_CONTROL_ADDR + " " + self.powerModule.CAL_CONTROL_SETTINGS[self.thisChannel + "_HIGH_CALIBRATION_CONTROL_SETTING"])
            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_HIGH_MULTIPLIER"] + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_HIGH_OFFSET"] + " 0x0000")

            # self.powerModule.add_comment("Setting connection for 12V switchbox")
            # self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_IN')])
            # self.powerModule.add_comment("Setting connection for Load switchbox")
            # self.powerModule.load_switchbox.setConnections([("LOAD",self.thisChannel + '_OUT')])
            self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_IN'),("LOAD",self.thisChannel + '_OUT')])

            # Setup Keithley
            self.setup()

            # Check Host Power is present
            while (super().checkLoadVoltage(self.powerModule.LOAD_VOLTAGE,1000) != True):
                showDialog(message="Host Power not detected, please check the connections",title="Check Connections")
                # self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_IN')],reset=True)
                # self.powerModule.load_switchbox.setConnections([("LOAD",self.thisChannel + '_OUT')],reset=True)
                self.powerModule.host_switchbox.setConnections([("12V", self.thisChannel + '_IN'), ("LOAD", self.thisChannel + '_OUT')])

            # Additional Keithley setup
            self.powerModule.calInstrument.setAverageCurrentCount(measCount=4)

        def setup(self):

            self.powerModule.calInstrument.initialSetupForReferenceCurrent()

        def setRef(self,value):

            self.powerModule.calInstrument.setReferenceCurrent(value/1000000)

        def readRef(self):

            # read device voltage and add leakage current to the reference
            #voltage =  getFixtureData(self.powerModule.dut,self.thisChannel + " V")
            #leakage = voltage*self.powerModule.calibrations["POWER_1"]["Leakage"].multiplier.originalValue() + self.powerModule.calibrations["POWER_1"]["Leakage"].offset.originalValue()
            return self.powerModule.calInstrument.measureLoadCurrent()*1000000# + leakage

        def readVal(self):

            return getFixtureData(self.powerModule.dut,self.thisChannel + " A")

        def setCoefficients(self):

            result1 = self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_HIGH_MULTIPLIER"] + " " + self.multiplier.hexString(4))
            result2 = self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_HIGH_OFFSET"] + " " + self.offset.hexString(4))
            if result1 and result2:
                result = True
            else:
                result = False
            logSimpleResult("Set " + self.thisChannel + " high current", result)


        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get high current multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_HIGH_MULTIPLIER"])
            # get high current offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_HIGH_OFFSET"])
            return coefficients

        def writeCoefficients(self,coefficients):

            # write high current multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_HIGH_MULTIPLIER"] + " " + coefficients["multiplier"])
            # write high current offset
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_HIGH_OFFSET"] + " " + coefficients["offset"])

    class QTL2621_VoltageVerification (QTL2621Calibration):

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

            # self.powerModule.host_switchbox.setConnections([("12V",None)])
            # self.powerModule.load_switchbox.setConnections([("LOAD",self.thisChannel + '_OUT')])

            self.powerModule.host_switchbox.setConnections([("12V",None),("LOAD",self.thisChannel + '_OUT')])

            self.setup()

            self.powerModule.calInstrument.setAverageVoltageCount(4)

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

    class QTL2621_LowCurrentVerification (QTL2621Calibration):

        def __init__(self,powerModule,thisChannel):

            self.thisChannel = thisChannel
            self.title = thisChannel + " Low Current Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 25     # 25uA  - Deliberately higher than calibration limit
            self.relErrorLimit = 1      # 1%
            self.test_min = 100         # 100uA
            self.test_max = 1000        # 1mA
            self.test_steps = 20
            self.units = "uA"

        def init(self):

            super().init_cal(self.thisChannel)

            # self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_IN')])
            # self.powerModule.load_switchbox.setConnections([("LOAD",self.thisChannel + '_OUT')])

            self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_IN'),("LOAD",self.thisChannel + '_OUT')])

            self.setup()

            # Check Host Power is present
            while (super().checkLoadVoltage(self.powerModule.LOAD_VOLTAGE,1000) != True):
                showDialog(message="Host Power not detected, please check the connections",title="Check Connections")
                # self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_IN')],reset=True)
                # self.powerModule.load_switchbox.setConnections([("LOAD",self.thisChannel + '_OUT')],reset=True)
                self.powerModule.host_switchbox.setConnections([("12V", self.thisChannel + '_IN'), ("LOAD", self.thisChannel + '_OUT')])

            self.powerModule.calInstrument.setAverageCurrentCount(4)

        def setup(self):
            self.powerModule.calInstrument.initialSetupForReferenceCurrent()

        def setRef(self,value):

            self.powerModule.calInstrument.setReferenceCurrent(value/1000000)

        def readRef(self):

            return self.powerModule.calInstrument.measureLoadCurrent()*1000000

        def readVal(self):

            return getFixtureData(self.powerModule.dut,self.thisChannel + " A")

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class QTL2621_HighCurrentVerification (QTL2621Calibration):

        def __init__(self,powerModule,thisChannel):

            self.thisChannel = thisChannel
            self.title = thisChannel + " High Current Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 2000       # 2mA
            self.relErrorLimit = 1          # 1% tolerance
            self.test_min = 1000            # 1mA
            self.test_max = 4000000         # 4A
            self.test_steps = 20
            self.units = "uA"

        def init(self):

            super().init_cal(self.thisChannel)

            # self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_IN')])
            # self.powerModule.load_switchbox.setConnections([("LOAD",self.thisChannel + '_OUT')])

            self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_IN'),("LOAD",self.thisChannel + '_OUT')])

            self.setup()

            # Check Host Power is present
            while (super().checkLoadVoltage(self.powerModule.LOAD_VOLTAGE,1000) != True):
                showDialog(message="Host Power not detected, please check the connections",title="Check Connections")
                # self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_IN')],reset=True)
                # self.powerModule.load_switchbox.setConnections([("LOAD",self.thisChannel + '_OUT')],reset=True)
                self.powerModule.host_switchbox.setConnections([("12V", self.thisChannel + '_IN'), ("LOAD", self.thisChannel + '_OUT')])

            self.powerModule.calInstrument.setAverageCurrentCount(4)

        def setup(self):
            self.powerModule.calInstrument.initialSetupForReferenceCurrent()

        def setRef(self,value):

            self.powerModule.calInstrument.setReferenceCurrent(value/1000000)

        def readRef(self):

            return self.powerModule.calInstrument.measureLoadCurrent()*1000000

        def readVal(self):

            return getFixtureData(self.powerModule.dut,self.thisChannel + " A")

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)