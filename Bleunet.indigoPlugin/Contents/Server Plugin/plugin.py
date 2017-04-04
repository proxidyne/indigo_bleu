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
		self.beacon_range = range(0,11)
		self.beacon_last_seen = {}
		self.beacon_absence_filter = 40 # seconds
	def __del__(self):
		indigo.PluginBase.__del__(self)
	######################
	def startup(self):
		self.loadPluginPrefs()
		self.debugLog(u"startup called")
	def shutdown(self):
		self.debugLog(u"shutdown called")

	######################


	def triggerStartProcessing(self, trigger):
		self.debugLog("Start processing trigger " + str(trigger.id))
		self.triggers.append(trigger)

	########################################
	def triggerStopProcessing(self, trigger):
		self.debugLog("Stop processing trigger " + str(trigger.id))
		for x in self.triggers:
			if trigger.id == x.id:
				self.triggers.remove(x)

	def loadPluginPrefs(self):
		self.debugLog(u"loadpluginPrefs called")	
		self.debug = self.pluginPrefs.get('debugEnabled',False)
		self.beacon_absence_filter = format_beacon_absence_filter(self.pluginPrefs.get('beaconAbsenceFilter', '0'))
		self.debugLog("Beacon absence filter: {} seconds".format(self.beacon_absence_filter))

	def closedPrefsConfigUi ( self, valuesDict, UserCancelled):
		if UserCancelled is False:
			indigo.server.log ("Preferences were updated.")
			self.loadPluginPrefs()

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
						except ValueError:
							self.debugLog('Error decoding JSON object')
							obj = {}
						device_id = obj.get("id","0")
						seq = int(obj.get("seq","00"),16)
						state = int(obj.get("state","00"),16)
						deviceClass=int(obj.get("class","00"),16)
						asset=int(obj.get("assetfield","00"), 16)
						offset=int(obj.get("offset","FF"), 16)
						asset = asset + offset
						self.last = sequences.get(device_id,0)
						if seq > self.last:
							sequences[device_id] = seq
							for y in indigo.devices.iter("self"):
								if "NodeID" in y.pluginProps:
									nodeID=y.pluginProps["NodeID"]
									if nodeID.lower() == device_id.lower():
										if (deviceClass == 0x8):  #button
											state_options = {'Pressed': {'One': 0x01, 'Two': 0x11, 'Three': 0x21, 'Four': 0x31}, 
												'LongPress': {'One': 0x02, 'Two': 0x12, 'Three': 0x22, 'Four': 0x32}}
											for push_type in state_options.keys():
												for button_number in state_options[push_type].keys():
													if (state == state_options[push_type][button_number]):
														state_name = "button{}{}".format(button_number, push_type)
														y.updateStateOnServer(state_name, value=True)
														y.updateStateOnServer(state_name, value=False)
										if (deviceClass == 0x9):  #motion sensor
											if (state == 0x00):
												y.updateStateOnServer('motionDetected', value=False)
											elif (state == 0x01):
												y.updateStateOnServer('motionDetected', value=True)
										if (deviceClass == 0x0a):  #beacon detector
											for beacon_number in self.beacon_range:
												beacon_previous_state = y.states.get("beaconNumber{}".format(beacon_number))
												if bit_present(asset, beacon_number):
													self.debugLog("beacon {} detected".format(beacon_number))
													self.beacon_last_seen[beacon_number] = time.time()
													if beacon_previous_state != True:
														indigo.server.log("found beacon {}".format(beacon_number))
														y.updateStateOnServer("beaconNumber{}".format(beacon_number), value=True)
												else:
													seconds_since_seen = time.time() - self.beacon_last_seen.get(beacon_number, 0)
													if (seconds_since_seen > self.beacon_absence_filter) and (beacon_previous_state != False):
														indigo.server.log("lost beacon {}".format(beacon_number))
														y.updateStateOnServer("beaconNumber{}".format(beacon_number), value=False)
 				self.sleep(.25) # in seconds
		except self.StopThread:
			# do any cleanup here
			pass

def bit_present(number, bit_position):
	bitmask = 2 ** bit_position
	return number & bitmask == bitmask

def format_beacon_absence_filter(value):
	if (not value.isdigit()) or (int(value) < 0):
		value = 0
	return int(value)
