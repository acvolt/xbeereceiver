#!/usr/bin/python

import serial
class XB():
	def Escape(self, msg):
		escaped = bytearray()
		reserved = bytearray(b"\x7E\x7D\x11\x13")
		
		escaped.append(msg[0])
		for m in msg[1:]:
			if m in reserved:
				escaped.append(0x7D)
				escaped.append(m ^ 0x20)
			else:
				escaped.append(m)
		return escaped

	def format (self, msg):
		return " ".join("{:02x}".format(b) for b in msg)


	def send (self, msg, addr=0xFFFF, options=0x01, frameid=0x00):
		if not msg:
			return 0
		msg.encode('utf-8')
		hexs = '7E 00 {:02X} 01 {:02X} {:02X} {:02X} {:02X}'.format(len(msg)+5, frameid, (addr & 0xFF00)>>8, addr & 0xFF, options)

		frame = bytearray.fromhex(hexs)
		frame.extend(msg)
		frame.append(0xFF - (sum(frame[3:]) & 0xFF))
		frame=self.Escape(frame)
		print("Tx: " + self.format(frame))
		return self.serial.write(frame)
	def __init__(self, serialport="/dev/ttyUSB0", baudrate=115200):
		self.serial = serial.Serial(serialport, baudrate)


	def checkSerial(self):
		return self.serial.inWaiting()



xbee = XB()

for i in range(1,10):
	msg = "This is the message " + str(i)
	print "In the for loop"
	print msg
	xbee.send(msg, 0x13, 0x00, i)
	print xbee.checkSerial()


