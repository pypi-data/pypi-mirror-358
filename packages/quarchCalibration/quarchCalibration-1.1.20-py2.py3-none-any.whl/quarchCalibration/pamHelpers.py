
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


def bcdString(bcd,padding):
    # strip off "0x" if present
    if bcd[:2] == "0x":
        bcd = bcd [2:]
    # strip off leading 0's
    # loop while we have more the required minimum number of characters left
    while(len(bcd)>padding):
        # if the leading character is 0, remove it
        if bcd[0] == '0':
            bcd = bcd[1:]
        # else exit loop
        else:
            break
    return bcd
