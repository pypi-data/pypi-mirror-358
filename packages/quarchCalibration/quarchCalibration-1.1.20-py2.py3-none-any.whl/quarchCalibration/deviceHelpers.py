import time
import socket
import logging

'''
Sends a measurement command to the device and decodes the response into a float and unit
component for return
'''
def returnMeasurement (myDevice, commandString):
    valueStr = None
    unitStr = None

    # Send the command
    responseStr = myDevice.sendCommand (commandString)
    # If a space is found, suggests xxx uu format
    pos = responseStr.find(" ")
    if (pos != -1):
        valStr = responseStr[:pos].strip()
        unitStr = responseStr[pos:].strip()
        try:
            floatVal = float(valStr)
        except:
            raise ValueError ("Response does not parse to a measurement value: " + responseStr)
    # If '0x' is found, looks like a register read value
    elif (responseStr.find("0x") != -1):
        unitStr = 'hex'
        try:
            unitVal = int(responseStr[2:].strip(),16)
        except:
            raise ValueError ("Response does not parse to a register measurement value: " + responseStr)
    # Otherwise may be a simple value (xxx format)       
    else:
        # Try to parse direct to float
        try:
            floatVal = float(responseStr)
        # If that failes, assumed to be xxxuu format
        except:
            for i, c in enumerate(responseStr):
                if c.isalpha():
                    pos = i
                    break
            if (i < len(responseStr)):
                valStr = responseStr[:pos].strip()
                unitStr = responseStr[pos:].strip()
                try:
                    floatVal = float(valStr)
                except:
                    raise ValueError ("Response does not parse to a measurement value: " + responseStr)
            else:
                raise ValueError ("Response does not parse to a measurement value: " + responseStr)
    
    # Return parsed values
    return valStr, unitStr
        
'''
Class to gather data from mDNS search system
'''
class MdnsListener:
    # Import zero conf only if available
    try:
        import zeroconf
        from zeroconf import ServiceInfo, Zeroconf
    except:
        logging.debug("Please install zeroconf using 'pip install zeroconf' ")
        zeroConfAvail = False

    def __init__(self):
        self.deviceList = {}

    def remove_service(self, zeroconf, type, name):
        pass

    '''
    Add all located devices to the dictionary (IP:Name)
    '''
    def add_service(self, zeroconf, type, name):
        try:
            info = zeroconf.get_service_info(type, name)
            if info:
                for address in info.addresses:
                    addr = socket.inet_ntoa(address)
                    self.deviceList[addr] = info.name
                    pass
        except Exception as e:
            logging.error("zeroconf threw an exception when attempting to add service " + name + " : " + str(e))


    def update_service(self, zeroconf, type, name):
        pass
            

'''
Function to locate a list of instruments matching the given name
'''
def locateMdnsInstr (instrName, serviceType="_http._tcp.local.", scanTime=2):
    # Import zero conf only if available
    try:
        import zeroconf
        from zeroconf import ServiceInfo, Zeroconf
    except:
        logging.error("Please install zeroconf using 'pip install zeroconf' ")
        zeroConfAvail = False

    from zeroconf import ServiceBrowser, Zeroconf
    foundDevices = {}

    # Run the scan process
    zeroconf = Zeroconf()
    listener = MdnsListener()
    browser = ServiceBrowser(zeroconf, serviceType, listener)
    time.sleep(scanTime)
    zeroconf.close()

    # Filter through the devices, looking for matching ones
    for k, v in listener.deviceList.items():
        if (instrName.upper() in v.upper()):
            foundDevices[k] = v

    # Sort the list by value to order the same way each time
    sortedFoundDevices = {}
    # get a sorted list of values
    for k in sorted(foundDevices.keys(),key=lambda x:x.lower()):
        sortedFoundDevices[k] = foundDevices[k]

    return sortedFoundDevices
