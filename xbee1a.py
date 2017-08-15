#!/usr/bin/python

import serial
import time
from collections import deque
import json
class XB():
	RxBuff=bytearray()
	RxMessages = deque()
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


	def send (self, msg, addr=0xFFFF, options=0x00, frameid=0x00):
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
	def Receive(self):
#		print "Receiving"
		remaining = self.serial.inWaiting()
		while remaining:
			chunk = self.serial.read(remaining)
			remaining -= len(chunk)
			self.RxBuff.extend(chunk)
		msgs = self.RxBuff.split(bytes(b'\x7E'))
		for msg in msgs[:-1]:
#			print msg
			self.Validate(msg)
		self.RxBuff = (bytearray() if self.Validate(msgs[-1]) else msgs[-1])
		if self.RxMessages:
			return self.RxMessages.popleft()
		else:
			return None
	def Validate(self, msg):
#		print "Validation size :", len(msg)
		if (len(msg) - msg.count(bytes(b'0x7D'))) < 6:
#			print "Validation Failure size"
			return False
		frame = self.Unescape(msg)
		
		LSB = frame[1]
		if LSB > (len(frame[2:])-1):
#			print "Validation Failure(length)"
			return False
		if (sum(frame[2:3+LSB]) & 0xFF) != 0xFF:
#			print "Validation Failure(checksum)"
			return False
#		print ("Rx: " + self.format(bytearray(b'\x7E') +msg))
		self.RxMessages.append(frame)
#		print "Validation Success"
		return True

	def Unescape(self, msg):
		if msg[-1] == 0x7D:
			return None
		out = bytearray()
		skip = False
		for i in range(len(msg)):
			if skip:
				skip=False
				continue
			if msg[i] == 0x7D:
				out.append(msg[i+1] ^ 0x20)
				skip = True
			else:
				out.append(msg[i])
		return out

def decode(msg):
	print int(msg[1])
	if msg[2]==0x81:
		print "Start Found of Received Message"
		print "From " + hex(msg[4]) + " RSSI=" + hex(msg[5]) + " Options " + hex(msg[6])
		data = msg[7:-1]
		print str(data)
		fz = json.loads(str(data))
		print "Test" + fz
	return		

xbee = XB("/dev/ttyUSB0", 57600)


for i in range(1,10):
#	xbee.send(msg, 0x13, 0x00, i)
#	print xbee.checkSerial()
	incoming = xbee.Receive()
	if incoming:
		print "Decoding"
		decode(incoming)
	else:
		time.sleep(.65)



