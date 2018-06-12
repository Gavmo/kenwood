import serial
import binascii
import time

class datapacket:
    def __init__(self):
        self.size = None
        self.ident = None
        self.subident = None
        self.data = list()
        self.checksum = None
        self.chksumindata = True

    def calcChecksum(self):
        datasum = 0
        if self.checksum:
            self.checksum = self.data.pop(-1)
            self.chksumindata = False
        for byte in self.data:
            datasum += int(byte, 16)
        checksum = hex(256 - datasum)
        self.checksum = checksum[checksum.find('x')+1:].zfill(2)
        return self.checksum

    def buildpacket(self, ident, data, subident=None):
        self.ident = ident
        self.data = data
##        print "ff {}".format(data)
        if subident:
            self.subident = subident
            self.size = hex(len(data)+1)[2:].zfill(2)
            self.data = [ident, self.size, subident]
            self.data.append(data[0].zfill(2))
        else:
            self.size = hex(len(data))
            self.data = [ident]
        cc = self.calcChecksum()
        self.data.append(cc)
        packet = ['10']
        packet.extend(self.data)
        packet.append('10')
        packet.append('03')
        return packet


def getpacket(serport):
    startarm = False
    endarm = False
    while not startarm:
        byte = binascii.hexlify(serport.read())
        if byte == '10':
            byte2 = binascii.hexlify(serport.read())
            if byte2 != '03':
                startarm = True
                packet = datapacket()
                packet.ident = byte2
                packet.data.append(byte2)
                break
##    packet = datapacket()
##    packet.ident = binascii.hexlify(serport.read())
    packet.size = binascii.hexlify(serport.read())
    packet.data.append(packet.size)
    if packet.ident == '8d':
        byte = binascii.hexlify(serport.read())
        packet.data.append(byte)
        packet.subident = byte
    while not endarm:
        byte = binascii.hexlify(serport.read())
##        print byte
        if byte == '10':
            byte2 = binascii.hexlify(serport.read())
            if byte2 == '03':
                endarm = True
                break
        packet.data.append(byte)
    return packet


def main():
    print "Opening port"
    ser = serial.Serial('/dev/ttyAMA0', 38400)
    print "Flushing"
    ser.flush()
    print "reading"
    data = ser.read(10)
    print type(data)
    print len(data)
    print repr(data)
    print binascii.hexlify(data)
    pod = getpacket(ser)
    print "---"
    print pod.ident
    print pod.data
    print pod.calcChecksum()
    for blah in testiterable():
        print 'Send data: {}'.format(blah)
        time.sleep(0.5)
        ser.write(blah)
        response = getpacket(ser)
        print 'response: {}'.format(response.data)
    ser.close()

def testiterable():
    for value in range(256):
        packet = datapacket()
        packetstring =  r'\x' + r'\x'.join(packet.buildpacket('8d', [hex(value)[2:]], subident='08'))
##        print packetstring
        yield packetstring

if __name__ == '__main__':
    main()
##    testiterable()
