from quarchpy.device.device import *
from quarchpy.user_interface import *
from quarchpy.device.scanDevices import userSelectDevice
class QTL2536_6_way_switchbox(quarchDevice):
    
    '''
    QTL2536_6_way_switchbox(portDict)

        portDict is a dictionary of names (keys) to ports (values) where the ports can be any or all of 'A','B','1','2','3','4','5','6'

    '''
    def __init__(self,switchboxAddress,name,portDict):
        for value in portDict.values():
            if value not in ['A','B','1','2','3','4','5','6']:
                raise
        self.name = name
        self.portDict = portDict
        self.connections = []   #A list of current connections on this switch
        try:
            self.switchbox = quarchDevice(switchboxAddress)
        except:
            raise

    # Connections are entered as a list of tuples, [(port,port),(port,port)] where port is a valid port name or 'None' to turn off the port
    # any connections not mentioned will be turned off
    def setConnections(self,connectionList,reset=False): #loadConnection,hostPowerConnection,reset=False):
    #TODO Fix for using class variable.
        if reset:
            self.connections = []

        #If changes need to be made
        if connectionList != self.connections:

            # Verify the connectionList
            for connections in connectionList:
                # Each entry should have 2 items
                if len(connections) == 2:
                    # Each item should be in the portList or None
                    for connection in connections:
                        if connection in self.portDict.keys() or connection == None:
                            pass
                        else:
                            raise Exception("invalid key found in connectionList")
                else:
                    raise Exception("each entry in connectionList should have 2 items")

            # No individual off commands so turn everything off first
            self.switchbox.sendAndVerifyCommand("connect off")

            # For each connection in the list
            for connection in connectionList:

                # If the tuple has two values, and they are both present in the port list, connect them
                if connection[0] in self.portDict.keys() and connection[1] in self.portDict.keys():
                    self.switchbox.sendAndVerifyCommand("connect " + self.portDict[connection[0]] + " " + self.portDict[connection[1]])

            self.connections = connectionList

    def checkWiring(self):
            listOfConnections = []
            listOfConnections.append("")
            listOfConnections.append(self.name)
            listOfConnections.append("======================")
            for port in self.portDict:
                listOfConnections.append("Please connect " + port + " to port " + self.portDict[port])
            showDialog(message="\r\n".join(listOfConnections))


    def disable(self):
        # Do not exit this method, until we are sure the load is disabled
        timeout_window = 10  # 10 seconds
        timeout = time.time() + timeout_window  # time = 10 seconds from now
        cmdResponse=""
        while cmdResponse.lower() != "ok":
            if time.time() > timeout:
                raise Exception("CRITICAL FAILURE : Can't disable Keithley, Please turn off manually and stop testing")
            cmdResponse = self.switchbox.sendCommand("con off")
            time.sleep(0.1)
        printText("6way switchbox disabled")


    def closeConnection(self):
        self.switchbox.closeConnection()


def get_switchbox(msg,name,portDict):
    # CheckSwitchbox
    while (True):
        switchboxAddress = userSelectDevice(scanFilterStr=["QTL2536"], message=msg, nice=True)
        if switchboxAddress == "quit":
            printText("User Quit Program")
            sys.exit(0)
        try:
            switchbox = QTL2536_6_way_switchbox(switchboxAddress,name,portDict)
            break
        except:
            printText("Unable to communicate with selected device!")
            printText("")
            switchboxAddress = None
            raise
    return switchbox