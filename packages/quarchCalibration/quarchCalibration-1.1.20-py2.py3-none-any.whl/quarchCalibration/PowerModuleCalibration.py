'''
Quarch Power Module Calibration Functions
Written for Python 3.6 64 bit

M Dearman April 2019
'''
from quarchCalibration import calibrationResources

'''
Calibration Flow
    Connect to PPM
    Connect to Keithley
    step through a set of values and get ADC vs Reference Value
    evaluate results vs defined limits
'''

#Imports QuarchPy library, providing the functions needed to use Quarch modules
#from quarchpy import quarchDevice #, scanDevices

# Import other libraries used in the examples
from functools import reduce
from quarchpy.device.device import *
from time import sleep,time
from math import ceil
from quarchpy.user_interface import *

'''
Coefficient Class

This class holds a floating point value, and the precision at which it will be stored (in the FPGA)

    The constructor will throw an OverFlowError if the integer value overflows the specified integer width

    Value() returns the original value

    storedValue() returns the reduced precision value as would be stored in the FPGA

    hexString() returns an appropriate length hex string of the stored Value

'''

class Coefficient:
    def __init__(self, value, signed, int_width, frac_width):
        # set overflow flag if the value can't fit in the assigned integer range
        if (signed == True and abs(value) >= (2**(int_width-1))) or (signed == False and abs(value) >= (2**(int_width))):
            self.overflow = True
        else:
            self.overflow = False

        self.value = value
        self.signed = signed
        self.int_width = int_width
        self.frac_width = frac_width

    def originalValue(self):
        return self.value

    # This function returns the value at the precision it would be stored in the FPGA flash
    def storedValue(self):
        # if number has overflowed, don't return a value
        if self.overflow == True:
            return 0
        # else reduce the value to the precision we can store
        else:
            #shift whole value left, then round to remove additional trailing bits and shift back to original position
            return float( round( self.value * (2**self.frac_width) ) ) / (2**self.frac_width)

    '''
    hexString(hex_chars)

    returns a hex string begining 0x with the number of hex characters specified
    '''
    #def hexString(self,hex_chars):
    #    #shift left by required number of fractional bits, round it (to nearest integer), then and with 1's to truncate it to required length
    #    return "{:#0{hex_chars}x}".format(round(self.value*(2**self.frac_width)) & (2**(hex_chars*4)-1),hex_chars=(hex_chars+2))

    def hexString(self,hex_chars):
        # if number has overflowed, don't return a value
        if self.overflow == True:
            return "Overflow Error"
        else:
            #shift left by required number of fractional bits, then AND with required number of characters to truncate as necessary
            return "{:#0{hex_chars}x}".format(int(self.storedValue()*(2**self.frac_width)) & (2 ** (self.int_width + self.frac_width) - 1) & ((2**(hex_chars*4))-1),hex_chars=(hex_chars+2))

'''
Calibration Class

This class holds a multiplier and offset coefficient as instances of the Coefficient class

    The constructor will generate multiplier and offset from a set of points in the form of a list of coordinates, using the x axis for ADC value and the y axis for reference value
    shift is an integer providing the size of the shift left that is applied to the result after multiplication and offset are applied

    Calibration(points,shift,abs_error,rel_error)

        shift is the binary left shift that takes place inside the FPGA


                LOW_12V = Calibration("uA",init_cmd,read_cmd,multiplier_cmd,offset_cmd,
                              MULTIPLIER = Coefficient(multiplier_int_width,multiplier_frac_width,multiplier_shift)
                              OFFSET = Coefficient(offset_int_width,offset_frac_width,offset_shift)

'''
class Calibration:

    powerModule = None
    absErrorLimit = None
    relErrorLimit = None
    test_min = None
    test_max = None
    test_steps = None
    units = None
    scaling = None
    multiplier_signed = None
    multiplier_int_width = None
    multiplier_frac_width  = None
    offset_signed = None
    offset_int_width  = None
    offset_frac_width  = None

    '''
    generate(points)

        generates a multiplier and offset from a set of coordinates

        points  -   a list of x and y values in form [(x0,y0),(x1,y1),(x2,y2)]

    '''        
    def generate(self,points):
        (thisMultiplier,thisOffset) = bestFit(points)
        # divide the offset by the hardware shift
        thisOffset /= self.scaling
        self.multiplier = Coefficient(thisMultiplier,self.multiplier_signed,self.multiplier_int_width,self.multiplier_frac_width)
        self.offset = Coefficient(-thisOffset,self.offset_signed,self.offset_int_width,self.offset_frac_width)            # offsets are subtracted in the hw, so we flip the sign of the offset
        if self.multiplier.overflow == True or self.offset.overflow == True:
            return False
        else:
            return True

    '''
    getResult(adc_value)

        takes in a value and applies the current calibration to it    

    '''
    def getResult(self,value):
        return round( ( (float(value)/self.scaling ) * self.multiplier.storedValue() - self.offset.storedValue() ) * self.scaling )

    '''
    getStepMultiplier()

        works out the multiplier to apply on each step to get exponentially from test_min to test_max in test_steps

    '''
    def getStepMultiplier(self):
        try:
            multiplier = (self.test_max/self.test_min)**(1/(self.test_steps-1))
            return multiplier
        except:
            raise ValueError("invalid step multiplier requested")

'''
AC PAM Coefficient Class

This class holds a floating point value, and the precision at which it will be stored (in the FPGA)

    The constructor will throw an OverFlowError if the integer value overflows the specified integer width

    Value() returns the original value

    storedValue() returns the reduced precision value as would be stored in the FPGA

    hexString() returns an appropriate length hex string of the stored Value

'''

class AcPamCoefficient:
    def __init__(self, value):
        # set overflow flag if the value is out of the supported range
        if value < 0.5 or value > 1.5:
            self.overflow = True
        else:
            self.overflow = False

        self.value = value

    def originalValue(self):
        return self.value

    # This function returns the value at the precision it would be stored in the FPGA flash
    def storedValue(self):
        # if number has overflowed, don't return a value
        if self.overflow == True:
            return 1
        # else reduce the value to the precision we can store
        else:
            # positive reg value
            if (self.value-1) >= 0:
                return 1 + (round(abs(self.value-1) * 2**23) / 2**23)
            # negative reg value
            else:
                return 1 - (round(abs(self.value-1) * 2**23) / 2**23)

    '''
    hexString(hex_chars)

    returns a hex string beginning 0x with the number of hex characters specified
    '''
    #def hexString(self,hex_chars):
    #    #shift left by required number of fractional bits, round it (to nearest integer), then and with 1's to truncate it to required length
    #    return "{:#0{hex_chars}x}".format(round(self.value*(2**self.frac_width)) & (2**(hex_chars*4)-1),hex_chars=(hex_chars+2))

    def hexString(self,hex_chars):
        # if number has overflowed, don't return a value
        if self.overflow == True:
            return "Overflow Error"
        # if the number will be positive
        if self.storedValue() >= 1:
            return "{:#0{hex_chars}x}".format(round((self.storedValue() - 1) * (2 ** 23)), hex_chars=(hex_chars + 2))
        # else result is negative
        else:
            return "{:#0{hex_chars}x}".format((2**(hex_chars*4)) - (round(abs(self.storedValue() - 1) * (2 ** 23))), hex_chars=(hex_chars + 2))

'''
AC PAM Calibration Class

This class holds a multiplier and offset coefficient as instances of the Coefficient class

    The constructor will generate multiplier and offset from a set of points in the form of a list of coordinates, using the x axis for ADC value and the y axis for reference value
    shift is an integer providing the size of the shift left that is applied to the result after multiplication and offset are applied

    Calibration(points,shift,abs_error,rel_error)

        shift is the binary left shift that takes place inside the FPGA


                LOW_12V = Calibration("uA",init_cmd,read_cmd,multiplier_cmd,offset_cmd,
                              MULTIPLIER = Coefficient(multiplier_int_width,multiplier_frac_width,multiplier_shift)
                              OFFSET = Coefficient(offset_int_width,offset_frac_width,offset_shift)

'''
class AcPamCalibration:

    powerModule = None
    absErrorLimit = None
    relErrorLimit = None
    test_min = None
    test_max = None
    test_steps = None
    units = None
    scaling = None
    multiplier_signed = None
    multiplier_int_width = None
    multiplier_frac_width  = None
    offset_signed = None
    offset_int_width  = None
    offset_frac_width  = None

    '''
    generate(points)

        generates a multiplier and offset from a set of coordinates

        points  -   a list of x and y values in form [(x0,y0),(x1,y1),(x2,y2)]

    '''        
    def generate(self,points):
        (thisMultiplier,thisOffset) = bestFit(points)
        # divide the offset by the hardware shift
        thisOffset /= self.scaling
        self.multiplier = AcPamCoefficient(thisMultiplier)
        self.offset = Coefficient(-thisOffset,self.offset_signed,self.offset_int_width,self.offset_frac_width)            # offsets are subtracted in the hw, so we flip the sign of the offset
        if self.multiplier.overflow == True or self.offset.overflow == True:
            return False
        else:
            return True

    '''
    getResult(adc_value)

        takes in a value and applies the current calibration to it    

    '''
    def getResult(self,value):
        return round( ( (float(value)/self.scaling ) * self.multiplier.storedValue() - self.offset.storedValue() ) * self.scaling )

    '''
    getStepMultiplier()

        works out the multiplier to apply on each step to get exponentially from test_min to test_max in test_steps

    '''
    def getStepMultiplier(self):
        try:
            multiplier = (self.test_max/self.test_min)**(1/(self.test_steps-1))
            return multiplier
        except:
            raise ValueError("invalid step multiplier requested")


'''
Class PowerModule

    Generic Class for a quarch module with measurement channels. The function holds a list of channels, and a channel holds a list of calibrations

'''
class PowerModule:

    name = None                # this is the name of the product that will be displayed to the user
    dut = None                 # this is a comms device for the module
    calObjectSerial = None     # This is the serial number of the device being calibrated i.e QTL1944 in PPM, the fixture serial number in PAM
    calibrations = {}          # a dictionary of calibrations supported by this module
    verifications = {}         # a dictionary of verifications supported by this module
    voltageMode = None

    def specific_requirements(self):
        # stub method to be overridden
        pass

    def wait_for_up_time(self, desired_up_time=600, command="conf:runtimes?"):

        returnText=""
        try:
            current_up_time = int(self.dut.sendCommand(command).lower().replace("s", ""))
            success = True
            wait_time = desired_up_time - current_up_time
        except:
            success = False
            current_up_time = 0
            wait_time = desired_up_time
        if current_up_time < desired_up_time:
            skip_uptime_wait = listSelection(title="Up Time", message=("Has the Module been on for more than " + str(desired_up_time) + " seconds?"),selectionList="Yes=Yes,No=No", tableHeaders=["Options"])
            if skip_uptime_wait.lower() == "no":
                printText("Waiting " + str(wait_time) + " seconds")
                startTime = time.time()
                currentTime = time.time()
                while int(currentTime - startTime) < int(wait_time):
                    sleep(1)
                    progressBar(int(currentTime - startTime), (wait_time))
                    currentTime = time.time()
                progressBar(100,100)
                printText("Wait Complete")
                returnText += "Runtime check complete - Module temperature is stable\n"
            else:
                printText("Wait for runtime to reach " + str(desired_up_time) + "s skipped")
                returnText += "Runtime check skipped - Module temperature not guaranteed to be stable.\n"
        return returnText

    def open_module(self):

        # stub method to be overridden
        pass
        
    def clear_calibration(self):
        # stub method to be overridden
        pass

    def write_calibration(self):
        # stub method to be overridden
        pass

    def close_module(self):
            
        # stub method to be overridden
        pass

    def close_all(self):

        # stub method to be overriden
        pass

    def readCalibration(self):

        calValues = {}

        for channel in self.calibrations:

            calValues[channel] = {}

            for calibration in self.calibrations[channel]:

                calValues[channel][calibration] = self.calibrations[channel][calibration].readCoefficients()


        return calValues

    def writeCalibration(self,calValues):

        self.dut.sendCommand("write 0xf000 0xaa55")
        self.dut.sendCommand("write 0xf000 0x55aa")
        
        for channel in calValues:

            for calibration in calValues[channel]:

                self.calibrations[channel][calibration].writeCoefficients(calValues[channel][calibration])

    def calibrateOrVerify(self,action,reportFile):

        listOfTestResults = []
        if action == 'calibrate':
            list = self.calibrations
        elif action == 'verify':
            list = self.verifications
        else:
            raise Exception('calibrateOrVerify() called with invalid action: ' + action)

        self.open_module()

        if action == 'calibrate':
            self.clear_calibration()

        # for each channel to be calibrated on the instrument
        for channel in list:

            # for each calibration/verification in the channel
            for calibration in list[channel]:

                thisItem = list[channel][calibration]

                # print title
                if action == 'calibrate':
                    startTestBlock("Calibrating " + channel + " " + calibration)
                else:
                    startTestBlock("Verifying " + channel + " " + calibration)

                # Initialise this calibration/verification
                thisItem.init()

                # step through values and populate table
                iteration = 1
                data = []
                steps = thisItem.test_steps
                test_value = thisItem.test_min
                abort_test = False
                while iteration <= steps:

                    # set reference value
                    thisItem.setRef(int(test_value))

                    # get calibrated result
                    reference = thisItem.readRef()

                    # get DUT result
                    value = thisItem.readVal()

                    # store the results
                    data.append([value, reference, test_value])

                    if not hasattr(thisItem, "skip_ref_check"):
                        # Check that the reference is within 10% of the set value, if not abort this calibration entirely
                        if reference >= (test_value * 1.1) or reference <= test_value * 0.9:
                            # Calculate the absolute difference
                            abs_difference = abs(reference - test_value)

                            # Divide by the test value to get the ratio
                            ratio = abs_difference / test_value

                            # Convert to percentage
                            percent_diff = ratio * 100

                            # Log a fail
                            logDebug(
                                "FAILED: Reference is not within 10% of the set value... Calibration is being aborted: "
                                "Reference Value: " + str(reference) + " Raw Set Value:" + str(test_value) + " Error: " +
                                str(percent_diff) + "%")
                            printText(
                                "FAILED: Reference is not within 10% of the set value... Calibration is being aborted: "
                                "Reference Value: " + str(reference) + " Raw Set Value:" + str(test_value) + " Error: " +
                                str(percent_diff) + "%")

                            abort_test = True

                            break

                    # print progress bar
                    progressBar(iteration,steps)
                    iteration += 1

                    # increment the test value or finish
                    test_value = test_value*thisItem.getStepMultiplier()

                # turn off the module and load
                thisItem.finish()

                if action == 'calibrate':

                    # generate coefficients
                    calibrationValid = thisItem.generate(data)

                    # if the coefficients are valid
                    if calibrationValid:
                        #set coefficients
                        thisItem.setCoefficients()
                    else:
                        printText("Error: coefficients are not valid and have not been written to the device")
                        reportFile.write("coefficients are not valid and have not been written to the device")

                report = thisItem.report(data)
                    
                reportFile.write("---------------------------------\n")
                reportFile.write(report["title"])
                reportFile.write("\n" + report["report"].replace("\r\n", "\n") + "\n")
                reportFile.flush()
                logCalibrationResult(report["title"],report)

                #Collect all results
                listOfTestResults.append(report)

                if abort_test:
                    # Append a "Fail" test point to ensure verification is skipped
                    listOfTestResults.append(
                        {"title": "Fail", "result": False, "worst case": "NONE - TEST POINT FAILED", "report": ""})
                    return listOfTestResults

        if action == 'calibrate':
            self.write_calibration()

        # reset the unit
        self.close_module()

        #return all results
        return listOfTestResults


'''
bestFit(points)

takes in a list of x and y coordinates of ADC values (x value) and reference values (y value)
and returns offset and gradient for the best fit straight line approximation of those points

'''
def bestFit(points):

    try:
        # calculate the mean value of all x coordinates
        AveX = reduce(lambda sum,point : sum+point[0],points,0)/len(points)
        # calculate the mean value of all y coordinates
        AveY = reduce(lambda sum,point : sum+point[1],points,0)/len(points)
        # calculate the sum of (x-x'mean)*(y-y'mean) for all points
        SumXY = reduce(lambda sum,point : sum + ((point[0]-AveX)*(point[1]-AveY)), points, 0)
        # calculate the sum of (x-x'mean)*(x-x'mean) for all points
        SumX2 = reduce(lambda sum,point : sum + ((point[0]-AveX)*(point[0]-AveX)), points, 0)

        if SumX2 == 0:
            Slope = AveY/AveX
            Intercept = 0.0
        else:
            Slope = SumXY/SumX2
            Intercept = AveY-(Slope*AveX)

        return Slope,Intercept

    except Exception as e:
        logging.critical(os.path.basename(__file__) + "bestFit algorithm failed to find a solution")
        return 1.0,0.0

'''
getError(reference_value,calculated_value,abs_error,rel_error)

    takes in a reference value and a calculated value
    returns a tuple with actual error (reference-calculated), absolute error, relative error and result

    abs_error is the absolute error allowance for this calibration, in the same units as the result
    rel_error is a percentage error allowance for this calibration, it is the percentage error between calibrated and reference value after the absolute error allowance is subtracted.

'''
def getError(reference_value,calculated_value,abs_error_limit,rel_error_limit):

    #the error at this point is reference value - test value
    error_value = calculated_value - reference_value

    #work out sign
    if error_value >= 0:
        error_sign = '+'
    else:
        error_sign = '-'

    #make error positive
    error_value = abs(error_value)
            
    # if error at this point is greater than absolute_error, set abs_error_val to absolute_error
    if error_value >= abs_error_limit:
        abs_error_val = abs_error_limit

        # calculate relative error after deduction of absolute error allowance, and as a percentage of the calculated value (not the reference value)
        # we return a positive percentage because the sign is always the same as abs_error_val so we display +/-(abs + pc)
        # check for divide by zero
        if calculated_value != 0:
            rel_error_val = abs(((error_value - abs_error_val) /  calculated_value) * 100)
        ## if divide by zero return 100%
        else:
            rel_error_val = 100

    # else round up to the nearest integer 
    else:
        abs_error_val = ceil(error_value)
        rel_error_val = 0

    # set pass/fail
    if abs(rel_error_val) <= rel_error_limit:
        result = True
    else:
        result = False

    #  Actual Error, Absolute Error, Relative Error, Pass/Fail
    return([error_value,error_sign,abs_error_val,rel_error_val,result])

