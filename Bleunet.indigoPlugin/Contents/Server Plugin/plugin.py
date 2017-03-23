#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright (c) 2016, Perceptive Automation, LLC. All rights reserved.
# http://www.indigodomo.com

from __future__ import with_statement

import indigo
import functools
import os
import Queue
from serial import Serial
import sys
import threading
import json
import time
import xml.etree.ElementTree as xmlTree

# Retry unavailable/broken serial connections approximately every 5 seconds:
kBadSerialRetryInterval = 5


################################################################################
class Plugin(indigo.PluginBase):
	########################################
	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		super(Plugin, self).__init__(pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
		self.debug = False
		self.triggers=[]
		self.last=0
	def __del__(self):
		indigo.PluginBase.__del__(self)
	######################
	def startup(self):
		self.debugLog(u"startup called")
	def shutdown(self):
		self.debugLog(u"shutdown called")

	######################


	def triggerStartProcessing(self, trigger):
		self.debugLog("Start processing trigger " + str(trigger.id))
		self.debugLog(trigger)
		self.triggers.append(trigger)

	########################################
	def triggerStopProcessing(self, trigger):
		self.debugLog("Stop processing trigger " + str(trigger.id))
		for x in self.triggers:
			if trigger.id == x.id:
				self.triggers.remove(x)



	def runConcurrentThread(self):
		serial = Serial(self.pluginPrefs['devicePortFieldId_serialPortLocal'], timeout=1)		
		sequences = dict()
		try:
			while True:
			# Do your stuff here
				if (serial.inWaiting()>0):
					data = serial.readline().translate(None, b'\x00')
					if data:
						self.debugLog("read data from serial: %s" % data.decode('ascii'))
						try:
							obj = json.loads(data.decode('ascii'))
							id = obj['id']
							seq = int(obj['seq'], 16)
							state = int(obj['state'])
							deviceClass=int(obj['class'])
							self.last = sequences.get(id) or 0
						except KeyError:
							self.debugLog('Error retrieving info from JSON object')
							seq = 0
						except ValueError:
							self.debugLog('Error decoding JSON object')
							obj = {}
							seq = 0
							self.last = 0
						if seq > self.last:
							sequences[id] = seq
							for y in indigo.devices.iter("self"):
								if "NodeID" in y.pluginProps:
									self.debugLog(y.pluginProps["NodeID"])
									nodeID=y.pluginProps["NodeID"]
									if nodeID.lower()==id.lower():
										if (deviceClass == 8):
											if (state == 01):
												y.updateStateOnServer('buttonOnePressed', value=True)
												y.updateStateOnServer('buttonOnePressed', value=False)
											elif (state == 11):
												y.updateStateOnServer('buttonTwoPressed', value=True)
												y.updateStateOnServer('buttonTwoPressed', value=False)
											elif (state == 21):
												y.updateStateOnServer('buttonThreePressed', value=True)
												y.updateStateOnServer('buttonThreePressed', value=False)
											elif (state == 31):
												y.updateStateOnServer('buttonFourPressed', value=True)
												y.updateStateOnServer('buttonFourPressed', value=False)
											if (state == 02):
												y.updateStateOnServer('buttonOneLongPress', value=True)
												y.updateStateOnServer('buttonOneLongPress', value=False)
											elif (state == 12):
												y.updateStateOnServer('buttonTwoLongPress', value=True)
												y.updateStateOnServer('buttonTwoLongPress', value=False)
											elif (state == 22):
												y.updateStateOnServer('buttonThreeLongPress', value=True)
												y.updateStateOnServer('buttonThreeLongPress', value=False)
											elif (state == 32):
												y.updateStateOnServer('buttonFourLongPress', value=True)
												y.updateStateOnServer('buttonFourLongPress', value=False)
										if (deviceClass == 9):  #motion sensor
											if (state == 0):
												y.updateStateOnServer('motionDetected', value=False)
											elif (state == 1):
												y.updateStateOnServer('motionDetected', value=True)

																				

						

 				self.sleep(.25) # in seconds
		except self.StopThread:
			# do any cleanup here
			pass		