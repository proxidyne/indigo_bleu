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
		self.lastasset=""
		self.missing_assets = []
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
							id = obj.get("id","0")
							seq = int(obj.get("seq","00"),16)
							state = int(obj.get("state","00"),16)
							deviceClass=int(obj.get("class",""),16)
							asset=obj.get("assetfield","")
							group=int(obj.get("grpnum","FF"), 16)
							self.last = sequences.get(id,0)
						except KeyError as e:
							self.debugLog('Error retrieving info from JSON object'+ e.errno)
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
									nodeID=y.pluginProps["NodeID"]
									if nodeID.lower()==id.lower():
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
											if group == 0x00:
												asset_int = int(asset, 16)
												for beacon_number in range(0,11):
													bitmask = 2 ** beacon_number
													if (asset_int & bitmask == bitmask):
														if y.states.get("beaconNumber{}".format(beacon_number)) != True:
															indigo.server.log("found beacon {}".format(beacon_number))
															self.missing_assets.remove(beacon_number)
															y.updateStateOnServer("beaconNumber{}".format(beacon_number), value=True)
														else:
															self.debugLog("beacon {} detected".format(beacon_number))
													else:
														self.debugLog("beacon {} not detected".format(beacon_number))
														if beacon_number in self.missing_assets:
															if y.states.get("beaconNumber{}".format(beacon_number)) != False:
																indigo.server.log("lost beacon {}".format(beacon_number))
																y.updateStateOnServer("beaconNumber{}".format(beacon_number), value=False)
														else:
															self.missing_assets.append(beacon_number)
 				self.sleep(.25) # in seconds
		except self.StopThread:
			# do any cleanup here
			pass
