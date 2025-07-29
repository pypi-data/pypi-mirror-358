# acHelpers.py
# a home for methods common to the AC PAM Calibration Scripts
# I think there is a better home and format for these

from quarchpy.connection_specific.connection_QIS import QisInterface as qisInterface
from quarchpy.qis import isQisRunning, startLocalQis
import re

# import matplotlib to show graphs for debug, later decision on whether and how to include this
import matplotlib
from matplotlib import pyplot as plt

#todo: MIKE - terrible name and strange location
def get_QIS_version():
	#TODO option var "close_qis_afer_check" to determine if qis is left open or not.
    global my_close_qis
    """
    Returns the version of QIS.  This is the version of QIS currenty running on the local system if one exists.
    Otherwise the local version within quarchpy will be exectued and its version returned.

    Returns
    -------
    version: str
        String representation of the QIS version number

    """

    qis_version = ""
    if isQisRunning() == False:
        my_close_qis = True
        startLocalQis(headless=True)

    myQis = qisInterface()
    qis_version = myQis.sendAndReceiveCmd(cmd="$version")
    if "No Target Device Specified" in qis_version:
        qis_version = myQis.sendAndReceiveCmd(cmd="$help").split("\r\n")[0]
    vmatch = re.search("v([0-9]).([0-9]+)", qis_version)
    if vmatch:
        return [int(x) for x in vmatch.groups()]

def startStream(device,streamFilename,streamDuration):

    # Sets for a manual record trigger, so we can start the stream from the script
    device.sendCommand("record:trigger:mode manual")
    device.sendCommand("record:averaging 0")
    device.startStream(streamFilename, 2000, 'Example stream to file', streamDuration)

def readRawValues(self):
            
    # Wait for stream to complete
    while ("Running" in device.streamRunningStatus()):
        time.sleep(0.1)
            
    rawValues = {}
    with open(self.streamFilename, 'r') as fh:
        csvfile = csv.reader(fh)
        titles = None
        for row in csvfile:
            if not titles:
                titles = row
                for i in range(len(row)):
                    rawValues[titles[i]] = []
            else:
                for i in range(len(row)):
                    try:
                        rawValues[titles[i]].append(int(row[i]))
                    except ValueError:
                        rawValues[titles[i]].append(0)
    return rawValues

'''
movingAverage(self,values,average)

values = a dictionary of channels each containing a list of samples
average = the number of samples to average with a moving window
returns a dictionary of channels each containing a list of samples
'''
def movingAverage(self,values,average):
    filteredValues = {}
    for channel in values.keys():
        filteredValues[channel] = []
        for x in range(0,len(values[channel])-(average-1)):
            filteredValues[channel].append(sum(values[channel][x:x+average])/average)
    return filteredValues

# we calculate rms on every measurement here then return the lot
# in calibration we only tend to care about one measurement and should probably replace this with something more specific

def calcRmsValues(self,average=1):
    rawValues = self.readRawValues()
    filteredValues = self.movingAverage(rawValues,average)
    rmsValues = {}
    for k in filteredValues.keys():
            items = [float(x**2) for x in rawValues[k]]
            if len(items) > 0:
                meanSquares = sum(items) / float(len(items))
            else:
                meanSquares = 0
            rmsValues[k] = meanSquares**0.5
    self.lastMeasurement = rmsValues
    return rmsValues

def findPeakValues(self):
    maxvalues = []
    prevValues = []
    peakList = []
    rising = []
    with open(self.streamFilename, 'r') as fh:
        csvfile = csv.reader(fh)
        titles = None
        for row in csvfile:
            if not titles:
                titles = row
                for i in range(len(row)):
                    maxvalues.append(0)
                    prevValues.append(0)
                    peakList.append([])
                    rising.append(False)
            else:
                for i in range(len(row)):
                    value = int(row[i])
                    if value >= maxvalues[i]:
                        maxvalues[i] = value

                    # If we are in the positive have of the wave, look for the point just when values begin to fall
                    if value > 0:
                        if value > prevValues[i]:
                            rising[i] = True
                            prevValues[i] = value
                        else:
                            if rising[i]:
                                peakList[i].append(prevValues[i])
                                rising[i] = False
                    else:
                        # On the negative half of the wave, reset the values for the next pass
                        rising[i] = False
                        prevValues[i] = 0

    mvdict = {}
    avgPeak = {}
    for i in range(len(titles)):
        mvdict[titles[i]] = maxvalues[i]

        # Throw away first and last samples, as they may have been clipped
        peakVector = np.array(peakList[i][1:-1])
        avgPeak[titles[i]] = peakVector.mean()

    return avgPeak

def getMeasurement(self, phase, parm, typ='PEAK', average=1):
    #self.streamData()
    if typ == 'PEAK':
        vals = self.findPeakValues()
    else:
        vals = self.calcRmsValues(average=average)

    if parm == 'V':
        key = "{0:s} mV".format(phase)
    else:
        key = "{0:s} mA".format(phase)

    if key in vals:
                
        #TODO: Mike Debug but might be useful if we want to add another package
        #plot value in question
        data = self.readRawValues()[key]
        x = range(0,len(data),1)
        y = self.readRawValues()[key]

        plt.clf()           # clear figure
        plt.title(key)      # set title
        plt.ion()           #interactive on, so it doesnt block
        plt.plot(x, y)      # add the data
        plt.draw()          # draw the data
        plt.pause(0.001)    # allow the GUI to update
        plt.show()          # show the window

        return vals[key]

    else:
        raise ValueError("requested measurement not found in data")