'''
Quarch Power Module Calibration Functions
Written for Python 3.6 64 bit

M Dearman April 2019
Edited k McRobert September 2021
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
    data = device.sendCommand("read 0x1000 to 0x1007")
    #release measurement
    response = device.sendCommand("read 0x0000")
    device.sendCommand("write 0x0000 " + clearBit(response,3))

    if (channel == "12V V"):
        return parseFixtureData(data,0,16)
    elif (channel == "12V A"):
        return parseFixtureData(data,16,25)
    elif (channel == "3V3_AUX V"):
        return parseFixtureData(data,41,16)
    elif (channel == "3V3_AUX A"):
        return parseFixtureData(data,57,20)



class QTL2673 (PowerModule):

    # Fixture Register Addresses
    CAL_ADDRESSES = {    
    '12V_LOW_MULTIPLIER'            : '0xA10C',
    '12V_LOW_OFFSET'                : '0xA10D',
    '12V_HIGH_MULTIPLIER'           : '0xA10E',
    '12V_HIGH_OFFSET'               : '0xA10F',
    '12V_VOLT_MULTIPLIER'           : '0xA110',
    '12V_VOLT_OFFSET'               : '0xA111',
    '12V_LEAKAGE_MULTIPLIER'        : '0xA112',
	
    '3V3_AUX_LOW_MULTIPLIER'        : '0xA113',
    '3V3_AUX_LOW_OFFSET'            : '0xA114',
    '3V3_AUX_VOLT_MULTIPLIER'		: '0xA115',
    '3V3_AUX_VOLT_OFFSET'			: '0xA116',
    '3V3_AUX_LEAKAGE_MULTIPLIER'    : '0xA117',
    'CALIBRATION_COMPLETE'          : '0xA118'
    }

    CONTROL_ADDRESSES = {
    'CALIBRATION_MODE'             	            : '0xA100',
    'CALIBRATION_CONTROL'          	            : '0xA101', 
    '12V_LOW_CALIBRATION_CONTROL_SETTING'       : '0x00F5',      # set manual range, full averaging, 12V low current mode,
    '12V_HIGH_CALIBRATION_CONTROL_SETTING'      : '0x00FA',      # set manual range, full averaging, 12V high current mode,
    '3V3_AUX_LOW_CALIBRATION_CONTROL_SETTING'   : '0x00F0',   # no range switching on 3V3_AUX, leave the module in auto mode
    '3V3_AUX_HIGH_CALIBRATION_CONTROL_SETTING'  : '0x00F0'  # no range switching on 3V3_AUX, leave the module in auto mode
    }

    LOAD_VOLTAGE                    = 12000

    host_switchbox_title = "Switchbox"
    host_switchbox_message = "Select the switch box which connects a 12V supply and Keithley Load to the fixture:"
    host_switchbox_mapping = {'12V':'A','12V_SUPPLY':'1','3V3_AUX_SUPPLY':'3','LOAD':'B','12V_LOAD':'4','3V3_AUX_LOAD':'6'}

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
    waitComplete = False
    checkedWiring = False

    def __init__(self,dut):

        # set the name of this module
        self.name = "EDSFF Power Measurement Fixture"
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
        # populate 12V channel with calibrations
        self.calibrations["12V"] = {
            "Voltage":self.QTL2673_VoltageCalibration(self,"12V"),
            #"Leakage":self.QTL2673_LeakageCalibration(self,"12V"),
            "Low Current":self.QTL2673_LowCurrentCalibration(self,"12V"),
            "High Current":self.QTL2673_HighCurrentCalibration(self,"12V")
            }
        # populate 3V3_AUX channel with calibrations
        self.calibrations["3.3V Aux"] = {
            "Voltage":self.QTL2673_VoltageCalibration(self,"3V3_AUX"),
            #"Leakage":self.QTL2673_LeakageCalibration(self,"3V3_AUX"),
            "Current":self.QTL2673_LowCurrentCalibration(self,"3V3_AUX")
            }

        self.verifications = {}
        # populate 12V channel with verifications
        self.verifications["12V"] = {
            "Voltage":self.QTL2673_VoltageVerification(self,"12V"),
            "Low Current":self.QTL2673_LowCurrentVerification(self,"12V"),
            "High Current":self.QTL2673_HighCurrentVerification(self,"12V")
            }
        # populate 3V3_AUX channel with verifications
        self.verifications["3.3V Aux"] = {
            "Voltage":self.QTL2673_VoltageVerification(self,"3V3_AUX"),
            "Current":self.QTL2673_LowCurrentVerification(self,"3V3_AUX")
            }


    def specific_requirements(self):

        reportText=""

        # select the host switchbox to use for calibration
        if "host_switchbox" in calibrationResources.keys():
            self.host_switchbox = calibrationResources["host_switchbox"]
        else:
            self.host_switchbox = get_switchbox(self.host_switchbox_message,self.host_switchbox_title,self.host_switchbox_mapping)
            calibrationResources["host_switchbox"] = self.host_switchbox

        if self.checkedWiring != True:
            self.host_switchbox.checkWiring()

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
            reportText += self.wait_for_up_time(desired_up_time=600, command="conf:runtime:fix:sec?")
            self.waitComplete = True

        return reportText

    def open_module(self):

        # set unit into calibration mode
        self.dut.sendCommand("write " + self.CONTROL_ADDRESSES["CALIBRATION_MODE"] + " 0xaa55")
        self.dut.sendCommand("write " + self.CONTROL_ADDRESSES["CALIBRATION_MODE"] + " 0x55aa")

    def clear_calibration(self):

        # set unit into calibration mode
        self.dut.sendCommand("write " + self.CONTROL_ADDRESSES["CALIBRATION_MODE"] + " 0xaa55")
        self.dut.sendCommand("write " + self.CONTROL_ADDRESSES["CALIBRATION_MODE"] + " 0x55aa")

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

    class QTL2673Calibration (Calibration):

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
            self.powerModule.dut.sendCommand("write " + self.powerModule.CONTROL_ADDRESSES["CALIBRATION_MODE"] + " 0xaa55")   # will not verify
            self.powerModule.dut.sendCommand("write " + self.powerModule.CONTROL_ADDRESSES["CALIBRATION_MODE"] + " 0x55aa")   # will not verify

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


            # turn dut to autoranging
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CONTROL_ADDRESSES["CALIBRATION_CONTROL"] + " 0x00F0")

        def report(self,action,data):

            report = []

            # send to report file
            report.append("          Pass Level  +/-(" + str(self.absErrorLimit) + str(self.units) +" + " + str(self.relErrorLimit) + "%) \n")


            # check errors and generate report
            report.append('\n')

            if action == "calibrate":
               report.append("\t" + '{0:>11}'.format('Reference ')+ self.units + '   ' + '{0:>10}'.format('Raw Value ')+ self.units + '   ' + '{0:>10}'.format('Result ')+ self.units + '   ' + '{0:>10}'.format('Error ')+ self.units + '   ' + '{0:>13}'.format('+/-(Abs Error,% Error)') + ' ' + '{0:>10}'.format('Pass'))
            elif action == "verify":
                report.append("\t" + '{0:>11}'.format('Reference ')+ self.units + '   ' + '{0:>10}'.format('Result ')+ self.units + '   ' + '{0:>10}'.format('Error ')+ self.units + '   ' + '{0:>13}'.format('+/-(Abs Error,% Error)') + '   ' + '{0:>10}'.format('Pass'))

            report.append("==================================================================================================")

            # zero worst case error vars
            worstAbsError = 0
            worstRelError = 0
            worstRef = None
            overallResult = True

            # for each calibration reference
            for thisLine in data:
                reference = thisLine[1]
                ppmValue = thisLine[0]

                # for calibration, replace value with calibrated result
                if action =="calibrate":
                    calibratedValue = self.getResult(ppmValue)
                # otherwise just use ppmValue directly
                else:
                    calibratedValue = ppmValue

                # work out errors
                (actError,errorSign,absError,relError,result) = getError(reference,calibratedValue,self.absErrorLimit,self.relErrorLimit)

                # compare/replace with running worst case
                if absError >= worstAbsError:
                    if relError >= worstRelError:
                        worstAbsError = absError
                        worstRelError = relError
                        worstCase = errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(relError) + "%) @ " + '{:.3f}'.format(reference) + self.units

                # update overall pass/fail
                if result != True:
                    overallResult = False

                #generate report
                passfail = lambda x: "Pass" if x else "Fail"
                if action == "calibrate":
                    report.append("\t" + '{:>11.3f}'.format(reference) + '     ' + '{:>10.1f}'.format(ppmValue) + '     ' + '{:>10.1f}'.format(calibratedValue) + '     ' + "{:>10.3f}".format(actError) + '     ' + '{0:>16}'.format(errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(relError) + "%)") + '     ' + '{0:>10}'.format(passfail(result)))
                elif action == "verify":
                    report.append("\t" + '{:>11.3f}'.format(reference) + '     ' + '{:>10.1f}'.format(ppmValue) + '     ' + "{:>10.3f}".format(actError) + '     ' + '{0:>16}'.format(errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(relError) + "%)") + '     ' + '{0:>10}'.format(passfail(result)))

            report.append("==================================================================================================")
            report.append('\n')

            if action == "calibrate":
                report.append("Calculated Multiplier: " + str(self.multiplier.originalValue()) + ", Calculated Offset: " + str(self.offset.originalValue()))
                report.append("Stored Multiplier: " + str(self.multiplier.storedValue()) + ", Stored Offset: " + str(self.offset.storedValue()))
                report.append("Multiplier Register: " + self.multiplier.hexString(4) + ", Offset Register: " + self.offset.hexString(4))

            report.append("" + '{0:<35}'.format(self.title)+ '     '  +'{0:>10}'.format("Passed : ")+ '  '  + '{0:<5}'.format(str(overallResult))+ '     ' + '{0:>11}'.format( "worst case:")+ '  '  +'{0:>11}'.format(worstCase))
            report.append("\n\n\n")
            
            #Add to Test Summary? Do this here?
            passfail = lambda x: "Passed" if x else "Failed"

            return {"title":self.title,"result":overallResult,"worst case":worstCase,"report":('\n'.join(report))}

    class QTL2673_VoltageCalibration (QTL2673Calibration):

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

            self.powerModule.host_switchbox.setConnections([("12V",None),("LOAD",self.thisChannel + "_LOAD")])

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

    class QTL2673_LowCurrentCalibration (QTL2673Calibration):

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

            #set manual range, full averaging, [thisChannel] low current mode, other channels all off (so we can detect we're connected to the wrong channel
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CONTROL_ADDRESSES["CALIBRATION_CONTROL"] + " " + self.powerModule.CONTROL_ADDRESSES[self.thisChannel + "_LOW_CALIBRATION_CONTROL_SETTING"])
            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_LOW_MULTIPLIER"] + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_LOW_OFFSET"] + " 0x0000")

            self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_SUPPLY'),("LOAD",self.thisChannel + '_LOAD')])

            # Setup Keithley
            self.setup()

            # Check Host Power is present
            while (super().checkLoadVoltage(self.powerModule.LOAD_VOLTAGE,1000) != True):
                showDialog(message="Host Power not detected, please check the connections",title="Check Connections")
                self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_SUPPLY'),("LOAD",self.thisChannel + '_LOAD')])

        def setup(self):

            self.powerModule.calInstrument.initialSetupForReferenceCurrent()

        def setRef(self,value):

            self.powerModule.calInstrument.setReferenceCurrent(value/1000000)

        def readRef(self):

            # read device voltage and add leakage current to the reference
            #voltage = getFixtureData(self.powerModule.dut,self.thisChannel + " V")
            #leakage = voltage*self.powerModule.calibrations["POWER_1"]["Leakage"].multiplier.originalValue() + self.powerModule.calibrations["POWER_1"]["Leakage"].offset.originalValue()
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

    class QTL2673_HighCurrentCalibration (QTL2673Calibration):

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
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CONTROL_ADDRESSES["CALIBRATION_CONTROL"] + " " + self.powerModule.CONTROL_ADDRESSES[self.thisChannel + "_HIGH_CALIBRATION_CONTROL_SETTING"])
            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_HIGH_MULTIPLIER"] + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + self.powerModule.CAL_ADDRESSES[self.thisChannel + "_HIGH_OFFSET"] + " 0x0000")

            self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_SUPPLY'),("LOAD",self.thisChannel + '_LOAD')])

            # Setup Keithley
            self.setup()

            # Check Host Power is present
            while (super().checkLoadVoltage(self.powerModule.LOAD_VOLTAGE,1000) != True):
                showDialog(message="Host Power not detected, please check the connections",title="Check Connections")
                self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_SUPPLY'),("LOAD",self.thisChannel + '_LOAD')])

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

    class QTL2673_VoltageVerification (QTL2673Calibration):

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

            self.powerModule.host_switchbox.setConnections([("12V",None),("LOAD",self.thisChannel + "_LOAD")])

            # Setup Keithley
            self.setup()

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

    class QTL2673_LowCurrentVerification (QTL2673Calibration):

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

            self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_SUPPLY'),("LOAD",self.thisChannel + '_LOAD')])

            # Setup Keithley
            self.setup()

            # Check Host Power is present
            while (super().checkLoadVoltage(self.powerModule.LOAD_VOLTAGE,1000) != True):
                showDialog(message="Host Power not detected, please check the connections",title="Check Connections")
                self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_SUPPLY'),("LOAD",self.thisChannel + '_LOAD')])

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

    class QTL2673_HighCurrentVerification (QTL2673Calibration):

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

            self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_SUPPLY'),("LOAD",self.thisChannel + '_LOAD')])

            # Setup Keithley
            self.setup()

            # Check Host Power is present
            while (super().checkLoadVoltage(self.powerModule.LOAD_VOLTAGE,1000) != True):
                showDialog(message="Host Power not detected, please check the connections",title="Check Connections")
                self.powerModule.host_switchbox.setConnections([("12V",self.thisChannel + '_SUPPLY'),("LOAD",self.thisChannel + '_LOAD')])

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