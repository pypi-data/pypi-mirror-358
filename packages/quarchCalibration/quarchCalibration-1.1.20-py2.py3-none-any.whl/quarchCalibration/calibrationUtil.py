#!/usr/bin/env python
'''
This example runs the calibration process for a HD PPM
It products a calibrated PPM and a calibration file for later use

########### VERSION HISTORY ###########

05/04/2019 - Andy Norrie     - First Version

########### INSTRUCTIONS ###########

1- Connect the PPM on LAN and power up
2- Connect the Keithley 2460 until on LAN, power up and check its IP address
3- Connect the calibration switch unit to the output ports of the PPM and Keithley

####################################
'''
# Global resources
import logging
import json
import sys
import warnings

# Filter the specific warning from runpy about quarchCalibration.calibrationUtil
warnings.filterwarnings(
    "ignore",
    message=".*'quarchCalibration.calibrationUtil' found in sys.modules.*",
    category=RuntimeWarning,
    module="runpy"  # Or potentially the module where the import happens if not runpy
)

# Calibration control
from quarchCalibration import calCodeVersion
from quarchCalibration.QTL1944_06_hd_plus_ppm import QTL1944_06
from quarchCalibration.QTL1944_hd_ppm import *
from quarchCalibration.QTL2347_pcie import *
from quarchCalibration.QTL2525_sff import *
from quarchCalibration.QTL2582_3ph_ac import *
from quarchCalibration.QTL2621_2ch_mezz import *
from quarchCalibration.QTL2626_4ch_mezz import *
from quarchCalibration.QTL2631_ext_mezz import *
# from quarchCalibration.QTL2628_ext_mezz_dimm import *
from quarchCalibration.QTL2631_pcie import *
from quarchCalibration.QTL2673_edsff import *
from quarchCalibration.QTL2843_iec_ac import *
from quarchCalibration.calibrationConfig import *
from quarchpy.debug.SystemTest import get_quarchpy_version

# UI functions
from quarchpy.user_interface import *
# TestCenter functions
from quarchpy.utilities import TestCenter

# import qis
from quarchpy.qis import isQisRunning, closeQis
from quarchpy.connection_specific.connection_QIS import QisInterface as qisInterface

# Devices that will show up in the module scan dialog
scanFilterStr = ["QTL1999", "QTL1995", "QTL1944", "QTL2312", "QTL2098", "QTL2582", "QTL2751", "QTL2789", "QTL2843"]
my_close_qis = False

supported_python_version = (3, 11, 9)


# Performs a standard calibration of the PPM
def runCalibration(loadAddress=None, calPath=None, moduleAddress=None, logLevel="warning", calAction=None,
                   switchboxAddress=None, resultsPath=None, extra_args=None):
    myPpmDevice = None
    listOfFailures = []
    try:
        # Display the app title to the user
        print("\n")
        displayTable(["Quarch Technology Calibration System", "(C) 2019-2021, All rights reserved", "V" + calCodeVersion], align="c")

        # Check for headless QIS
        if isQisRunning():
            myQIS = qisInterface()
            version = myQIS.sendAndReceiveCmd(cmd="$version")
            user_input = showYesNoDialog("", "QIS " + version + " is already running, should we close this first? (recommended)")
            printText(user_input)
            if user_input.lower() == "yes":
                closeQis()

        # Check Python Version
        if not check_python_version():
            printText("Exiting the script...")
            sys.exit()

        # Process parameters
        calPath = get_check_valid_calPath(calPath)

        calibrationResources["moduleString"] = moduleAddress
        calibrationResources["loadString"] = loadAddress
        calibrationResources["switchboxStr"] = switchboxAddress
        calibrationResources["calPath"] = calPath

        # Need boolean to check whether the report path has already been set
        cal_path_set = False

        while True:  # While doing any calibration task

            if myPpmDevice == None:  # If no ppmDevice for the DUT
                dut, myPpmDevice = create_dut_object()

            if not cal_path_set:
                # Need another check here for the report path to create sub-folder for specific module
                # Update calPath to include the module sub-folder
                calibrationResources["calPath"] = os.path.join(calibrationResources["calPath"], get_path_from_module_address(dut.filenameString))
                # Ensure the directory structure exists
                os.makedirs(calibrationResources["calPath"], exist_ok=True)
                cal_path_set = True

            # Cal Action Parsing
            if (calAction == None):
                if User_interface.instance.selectedInterface == "testcenter":
                    # Close connection to module
                    dut.close_module()
                    dut.dut.closeConnection()
                    if resultsPath is not None:
                        with open(resultsPath, 'w') as json_file:
                            json.dump(listOfFailures, json_file)
                    return listOfFailures  # Return failures to parent script for processing.
                else:  # If no calibration action is selected, request one
                    # Clear the list of failures as we are starting a new action
                    listOfFailures = []
                    calAction = show_action_menu(calAction)
            if (calAction == 'quit'):
                sys.exit(0)

            elif (calAction == 'calibrate') or (calAction == 'verify'):
                # Perform the Calibration or Verification
                # get CalibrationTime
                calTime = datetime.datetime.now()

                # open report for writing and write system header
                fileName = calibrationResources["calPath"] + "\\" + dut.filenameString + " [" + calTime.strftime("%d-%m-%y %H-%M") + "] " + calAction + ".txt"
                # Store report path in cal resources
                calibrationResources["reportPath"] = fileName
                printText("")
                printText("Report file: " + fileName)
                reportFile = open(fileName, "a+", encoding='utf-8')
                reportFile.write("\n")
                reportFile.write("Quarch Technology Calibration Report\n" if "cal" in str(
                    calAction).lower() else "Quarch Technology Verification Report\n")
                reportFile.write("\n")
                reportFile.write("---------------------------------\n")
                reportFile.write("\n")
                reportFile.write("Device Under Test:\n")
                reportFile.write(dut.dut.sendCommand("*IDN?").replace("\r\n", "\n") + "\n")
                if "fixture:" in dut.dut.sendCommand("*IDN?").lower():
                    reportFile.write("Fixture IDN:\n")
                    reportFile.write(dut.dut.sendCommand("fix IDN?").replace("\r\n", "\n") + "\n")
                reportFile.write("\n")
                reportFile.write("System Information:\n")
                reportFile.write("\n")
                try:
                    reportFile.write("QuarchPy Version: " + get_quarchpy_version() + "\n")
                except:
                    reportFile.write("QuarchPy Version: unknown\n")
                reportFile.write("Calibration Version: " + str(calCodeVersion) + "\n")
                reportFile.write("Calibration Time: " + str(calTime.replace(microsecond=0)) + "\n")
                reportFile.write("\n")
                reportFile.write("---------------------------------\n")
                reportFile.write("\n")
                reportFile.flush()

                # get required instruments etc
                reportFile.write("Device Specific Information:\n")
                reportFile.write("\n")
                reportFile.write(dut.specific_requirements())
                reportFile.write("\n")
                reportFile.write("---------------------------------\n")
                reportFile.write("\n")
                reportFile.flush()

                # Perform the Calibration or Verification
                listOfTestResults = dut.calibrateOrVerify(calAction, reportFile)
                for testResult in listOfTestResults:
                    if testResult["result"] is False:
                        listOfFailures.append(testResult)

                addOverviewSectionToReportFile(reportFile, listOfTestResults, calAction, calculateTestPass(listOfFailures))
                reportFile.close()

                tst_result = True

                if calAction == 'calibrate':
                    # Check output of *TST?
                    tst_result = True
                    # response = dut.dut.sendCommand('*TST?')
                    # if response != "OK":
                    #     logSimpleResult("Device test failed", 'false')
                    #     tst_result = False
                    # else:
                    #     logSimpleResult('Device test passed', 'true')

                if calculateTestPass(listOfFailures) == True and tst_result:  # IF the test has passed go to next step.
                    if 'calibrate' in calAction:
                        calAction = "verify"
                    elif 'verify' in calAction:
                        calAction = None
                else:
                    if User_interface.instance == "testcenter":  # Cal Failed so pass back fails for DB logging
                        dut.close_module()
                        dut.dut.closeConnection()
                        if resultsPath is not None:
                            with open(resultsPath, 'w') as json_file:
                                json.dump(listOfFailures, json_file)
                        return listOfFailures
                    else:
                        printText(
                            "Not continuing with next stage as failed test points found in current stage.")  # Cal Failed so
                        calAction = None
            elif (calAction == None):
                if User_interface.instance is None and User_interface.instance.selectedInterface == "testcenter":
                    dut.close_module()
                    dut.dut.closeConnection()
                    if resultsPath is not None:
                        with open(resultsPath, 'w') as json_file:
                            json.dump(listOfFailures, json_file)
                    return listOfFailures
                # otherwise go back to menu
                else:
                    calAction = None
            elif 'select' in calAction:
                calAction = None
                myPpmDevice.closeConnection()
                myPpmDevice = None
                calibrationResources["moduleString"] = None
            else:
                raise Exception("calAction \"" + str(calAction) + "\" not recognised")
    except Exception as thisException:
        printText("Unexpected Exception! Aborting tests and closing all device connections. " + str(thisException))
        quarchpy.user_interface.logWarning(
            "Unexpected Exception! Aborting tests and closing all device connections. " + str(thisException))
        logging.error("Unexpected Exception! Aborting tests and closing all device connections. " + str(thisException),
                      exc_info=True)
        try:
            dut.close_all()
            myPpmDevice.closeConnection()
        # Handle case where exception may have been thrown before instrument was set up
        except Exception as e:
            logging.error("DUT connection not closed. Exception may have been thrown before instrument was set up." + str(e))
            pass


def create_dut_object():
    # Connect to the module
    while True:
        # If no address specified, the user must select the module to calibrate
        if (calibrationResources["moduleString"] == None):
            deviceString = userSelectDevice(scanFilterStr=scanFilterStr, nice=True, message="Select device for calibration")
            # quit if necessary
            if deviceString == 'quit':
                printText("no module selected, exiting...")
                sys.exit(0)
            else:
                calibrationResources["moduleString"] = deviceString

        try:
            printText("Selected Module: " + calibrationResources["moduleString"])
            myPpmDevice = quarchDevice(calibrationResources["moduleString"])
            myPpmDevice.resetDevice()  # Attempt to reset the device before using it.
            break
        except:
            printText("Failed to connect to " + str(calibrationResources["moduleString"]))
            calibrationResources["moduleString"] = None
    serialNumber = myPpmDevice.sendCommand("*SERIAL?")
    success = False
    fixtureId = None
    # Identify and create a power module object
    # If this is an HD PPM
    if ('1944' in serialNumber):
        # is this ppm original or plus version
        # get the FPGA
        FPGAPart = myPpmDevice.sendCommand("read 0xfffe")
        if ('2899' in FPGAPart):
            # create HD Plus Power Module Object
            dut = QTL1944_06(myPpmDevice)
            success = True
        else:
            # create HD Power Module Object
            dut = QTL1944(myPpmDevice)
            success = True
    # Else if this is a Power Analysis Module
    elif ('2098' in serialNumber):
        # this is a Power Analysis Module, we need to detect the fixture
        fixtureId = myPpmDevice.sendCommand("read 0xA102")
        # PCIe x16 AIC Fixture
        if ('2347' in fixtureId or '2910' in fixtureId):
            dut = QTL2347(myPpmDevice)
            success = True
        ## PCIE Gen 4 SFF Fixture
        elif ('2525' in fixtureId):
            dut = QTL2525(myPpmDevice)
            success = True
        ## PCIE Gen 5 SFF Fixture - same calibration as QTL2525
        elif ('2788' in fixtureId):
            dut = QTL2525(myPpmDevice)
            success = True
        ## Gen4 E1 EDSFF Fixture
        elif ('2673' in fixtureId):
            dut = QTL2673(myPpmDevice)
            success = True
        ## Gen4 E3 EDSFF Fixture - shares a PCBA with QTL2673
        elif ('2674' in fixtureId):
            dut = QTL2673(myPpmDevice)
            success = True
        ## Gen5 E1 EDSFF Fixture - shares a PCBA with QTL2673
        elif ('2887' in fixtureId):
            dut = QTL2673(myPpmDevice)
            success = True
        ## Gen5 E3 EDSFF Fixture - shares a PCBA with QTL2673
        elif ('2888' in fixtureId):
            dut = QTL2673(myPpmDevice)
            success = True
        ## Gen6 EDSFF x8 PAM Fixture
        elif ('3069' in fixtureId):
            dut = QTL2673(myPpmDevice)
            success = True
        # 2-Channel PAM Mezzanine
        elif ('2621' in fixtureId):
            dut = QTL2621(myPpmDevice)
            success = True
        # 4-Channel PAM Mezzanine
        elif ('2626' in fixtureId):
            dut = QTL2626(myPpmDevice)
            success = True
        # External Shunt PAM Mezzanine
        elif ('2631' in fixtureId):
            # We need to read the carrier serial number
            carrier = myPpmDevice.sendCommand("read 0xA401")
            # If this is a PCIe with AUX (GPU) fixture it has a special calibration
            if '2983' in carrier:
                dut = QTL2631_pcie(myPpmDevice)
                success = True
            # Else we should calibrate in an external shunt calibration fixture (which is different to an external shunt fixture)
            elif '2997' in carrier or '2998' in carrier or '2630' in carrier:
                dut = QTL2631(myPpmDevice)
                success = True
            # Commenting this out because dimm fixture is still in developnment and it may cause confusion in production
            # # Else this is an actual external shunt fixture (without shunt resistors), we use this to calibrate the DIMM fixture
            #elif '2628' in carrier:
            #dut = QTL2628(myPpmDevice)
            #success = True
            else:
                # Error message here!
                raise ValueError(
                    "ERROR - For external shunt we need to read the carrier part number, '" + carrier + "' was not recognised")

                # Else if this is a 3 phase AC PAM
    elif ('2582' in serialNumber) or ('2751' in serialNumber) or ('2789' in serialNumber):
        dut = QTL2582(myPpmDevice)
        success = True
    # Else if this is an IEC PAM
    elif ('2843' in serialNumber):
        dut = QTL2843(myPpmDevice)
        success = True

    if (success == False):
        if fixtureId:
            raise ValueError("ERROR - Serial number '" + fixtureId + "' not recogised as a valid power module")
        else:
            raise ValueError("ERROR - Serial number '" + serialNumber + "' not recogised as a valid power module")
    # If we're in testcenter setup the test
    if User_interface.instance != None and User_interface.instance.selectedInterface == "testcenter":
        # Store the serial number from the DUT scan for logging and verification
        TestCenter.testPoint("Quarch_Internal.StoreSerial", "Serial=" + dut.calObjectSerial)
        idnStr = str(dut.idnStr).replace("\r\n", "|")
        TestCenter.testPoint("Quarch_Internal.StoreDutActualIdn", "Idn=" + idnStr)
    return dut, myPpmDevice


def calculateTestPass(list):
    '''Simple fuction uses to determine if the overall test has passed by looking at the list of test failures '''
    if len(list) == 0:
        return True
    else:
        return False


def setup_logging(logLevel):
    # check log file is present or writeable
    numeric_level = getattr(logging, logLevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % logLevel)
    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s',datefmt='%Y-%m-%d,%H:%M:%S', level=numeric_level)


def show_action_menu(calAction):
    actionList = []
    actionList.append(["Calibrate", "Calibrate the power module"])
    actionList.append(["Verify", "Verify existing calibration on the power module"])
    actionList.append(["Select", "Select a different power module"])
    actionList.append(["Quit", "Quit"])
    calAction = listSelection("Select an action", "Please select an action to perform", actionList, nice=True,
                              tableHeaders=["Option", "Description"], indexReq=True)

    return calAction[1].lower()


# Returns a resource from the previous calibration. This is the mechanism for getting results and similar back to
# a higher level automated script.
def getCalibrationResource(resourceName):
    try:
        return calibrationResources[resourceName]
    except Exception as e:
        printText("Failed to get calibration resource : " + str(resourceName))
        printText("Exception : " + str(e))
        return None


def addOverviewSectionToReportFile(reportFile, listOfTestResults, calAction, result):
    overViewList = []
    if calAction == "calibrate":
        if result:
            stamp = "CALIBRATION PASSED"
        else:
            stamp = "CALIBRATION FAILED"
    else:
        if result:
            stamp = "VERIFICATION PASSED"
        else:
            stamp = "VERIFICATION FAILED"

    for testResults in listOfTestResults:
        overViewList.append([testResults["title"], testResults["result"], testResults["worst case"]])
    reportFile.write(
        "\n\n" + displayTable(overViewList, tableHeaders=["Title", "Passed", "Worst Case"], printToConsole=False,
                              align="r") + "\n\n" + displayTable(stamp, printToConsole=True))


def get_path_from_module_address(deviceString):
    """
    Retrieves the appropriate serial number of the module under test.
    :param deviceString: Serial number of the device
    :type deviceString: string

    :return: Returns the extracted part number of the device
    :rType: string
    """
    first_dash_index = deviceString.find("-")

    if first_dash_index != -1:
        second_dash_index = deviceString.find("-", first_dash_index + 1)

        if second_dash_index != -1:
            first_part = deviceString[:first_dash_index]
            second_part = deviceString[first_dash_index + 1:second_dash_index]
            return first_part

    return None


def check_python_version():
    # Get the current Python version tuple (major, minor, micro)
    current_version_tuple = sys.version_info[:3]  # Slice to get only major, minor, micro
    if supported_python_version != current_version_tuple:
        major, minor, micro = current_version_tuple
        supported_major, supported_minor, supported_micro = supported_python_version
        response = showYesNoDialog(
            "Python Version",
            f"You are running an unsupported version of Python ({major}.{minor}.{micro}) for the quarchCalibration module. " +
            f"The currently supported version of Python is {supported_major}.{supported_minor}.{supported_micro} " +
            f"Would you like to continue?"
        )
        if "no" in response.lower():
            return False
        return True
    return True


def get_scan_filter_str():
    return scanFilterStr


def main(argstring):
    import argparse
    # Handle expected command line arguments here using a flexible parsing system
    parser = argparse.ArgumentParser(description='Calibration utility parameters')
    parser.add_argument('-a', '--action', help='Calibration action to perform', choices=['calibrate', 'verify'],
                        type=str.lower)
    parser.add_argument('-m', '--module', help='IP Address or netBIOS name of power module to calibrate',
                        type=str.lower)
    parser.add_argument('-i', '--instr', help='IP Address or netBIOS name of calibration instrument', type=str.lower)
    parser.add_argument('-s', '--switchbox', help='IP Address or netBIOS name of switchbox instrument', type=str.lower)
    parser.add_argument('-p', '--path', help='Path to store calibration logs', type=str.lower)
    parser.add_argument('-r', '--results', help='Path to store calibration results', type=str.lower)
    parser.add_argument('-l', '--logging', help='Level of logging to report', choices=['warning', 'error', 'debug'],
                        type=str.lower, default='warning')
    parser.add_argument('-u', '--userMode', help=argparse.SUPPRESS, choices=['console', 'testcenter'], type=str.lower,
                        default='console')  # Passes the output to testcenter instead of the console Internal Use

    args, extra_args = parser.parse_known_args(argstring)
    # Create a user interface object
    thisInterface = User_interface(args.userMode)
    if extra_args != []:
        printText("failed to Parse the following ARG/s: " + str(extra_args))

    # Call the main calibration function, passing the provided arguments
    return runCalibration(loadAddress=args.instr, calPath=args.path, moduleAddress=args.module,
                          logLevel=args.logging, calAction=args.action, switchboxAddress=args.switchbox,
                          resultsPath=args.results)


# Command to run from terminal.
# python -m quarchCalibration -mUSB:QTL1999-01-002 -acalibrate -i192.168.1.210 -pC:\\Users\\sboon\\Desktop\\CalTesting
if __name__ == "__main__":
    main(sys.argv[1:])
    # main(["-anoise_test", "-mUSB:QTL2312-01-035",  "-pC:\\Users\\Public\\Documents\\calibrationReports", "-sQ:\\Production\\Calibration\\NoiseTestStreams"])
    # Example or args parsing
    # The argument do the following, set the action to calibrate, define the IP address of the module, defignt he IP saddress of the calibration instument, set the save location of the calibration report file, and set the logging level to warning.
    # main (["-acalibrate", "-mTCP:192.168.1.170", "--instrREST:192.168.1.205",  "-pC:\\Users\\Public\\Document\\QuarchPythonCalibration", "-lwarning"])
