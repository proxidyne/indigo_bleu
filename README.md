# Indigo Bleu: Indigo home automation software plugin to use Bleunet bluetooth devices.

* ## Supported Devices: 
* [Proxidyne 4 Up Button](https://store.proxidyne.com/collections/bleunet-sensors-for-home-automation/products/survey-button?variant=35408516234)
* [Proxidyne 1 Up Button](https://store.proxidyne.com/collections/bleunet-sensors-for-home-automation/products/single-button-sensor?variant=35411831498)
* [Proxidyne Compact Four-Button Button with Mounting Bracket](https://store.proxidyne.com/collections/bleunet-sensors-for-home-automation/products/proxidyne-compact-four-button-button-with-mounting-bracket?variant=35404503626)
* [Proxidyne Motion Sensor with Mounting Bracket](https://store.proxidyne.com/collections/bleunet-sensors-for-home-automation/products/motion-sensor?variant=35373531914)
* [Proxidyne Bleunet Receiver](https://store.proxidyne.com/collections/bleunet-sensors-for-home-automation/products/bluetooth-receiver?variant=35364208138)

<img src="https://i0.wp.com/s3.amazonaws.com/proxidyne-static/2016/05/16151101/graphic-beacon_LEFT-greenLED_FINALcutout.jpeg"  width="256" align="left">
<img src="https://i0.wp.com/s3.amazonaws.com/proxidyne-static/2016/12/29095222/single-button-sensor320X240.png"  width="256" align="left">
<img src="https://i0.wp.com/s3.amazonaws.com/proxidyne-static/2016/05/16151101/graphic-beacon_LEFT-greenLED_FINALcutout.jpeg"  width="256" align="left">
<img src="https://s3.amazonaws.com/proxidyne-static/2016/08/17092341/survey_button_no_background.jpg"  width="256" align="left">
<img src="https://i0.wp.com/s3.amazonaws.com/proxidyne-static/2016/12/28204603/motion-sensor320X240.png"  width="256" align="left">
<img src="https://i1.wp.com/s3.amazonaws.com/proxidyne-static/2017/03/11133303/series100.png"  width="256" >


## Instructions
* Download and install our Indigo plugin from github.  The plugin needs to be installed in the /Library/Application Support/Perceptive Automation/Indigo 7/Plugins folder:
![image](https://i0.wp.com/s3.amazonaws.com/proxidyne-static/2017/03/23212621/pathtoplugin.png)
* Indigo now shows the Bleunet plugin as an available plug-in in Indigo:
![image](https://i1.wp.com/s3.amazonaws.com/proxidyne-static/2017/03/23212722/plugin.png)
* Plug in the Proxidyne Receiver, click Configure to select the serial port.  It shows up as a usbmodemXXXX:
![image](https://i1.wp.com/s3.amazonaws.com/proxidyne-static/2017/03/23212843/serial.png)
* Now the plugin is talking to the receiver.  To receive iBeacon packets, I set up a device by selecting Devices in the main window and clicking New.  Create New Device appears and select Type and Model:
![image](https://i2.wp.com/s3.amazonaws.com/proxidyne-static/2017/03/23213033/newdevice.png)
* When prompted for the Node ID, I entered in the number on the side of the iBeacon Detector:
![image](https://i2.wp.com/s3.amazonaws.com/proxidyne-static/2017/03/23213219/nodeid1.png)
* The device now shows up in Devices in Indigo.

## Buttons and Motion Sensors
• Once the device is set up, you can set up triggers when a button is pressed or motion is detected:
![image](https://i0.wp.com/s3.amazonaws.com/proxidyne-static/2017/03/23163307/buttonpresstrigger.png)
![image](https://i2.wp.com/s3.amazonaws.com/proxidyne-static/2017/03/23163255/trigger2.png)

## iBeacon Detector

The system looks like this:
![image](https://i1.wp.com/s3.amazonaws.com/proxidyne-static/2017/03/23163324/beacon-detector2.png)

When someone with a wearable walks into a room with an iBeacon Detector, the iBeacon detector senses it and compares the identifiers being broadcast by the iBeacon to the identifiers the iBeacon detector is listening for.  Specifically, if the UUID and major number of the iBeacon transmission from the wearable match the configured UUID and major number of the iBeacon Detector, a trigger is sent from the iBeacon Detector to the USB Receiver plugged into the Indigo Server.  The Indigo server has our plugin installed, and recognizes this transmission, and triggers an action based on the person entering or existing the proximity to the iBeacon Detector.  The iBeacon Detector has the ability to filter out based on signal strength as well, so only iBeacons that are within a specified distance  will trigger actions.  You have much more granular control for triggering on distance than with an app and an iBeacon.

* Plug in the Beacon Detector to start detecting iBeacons.
* Configure a wearable iBeacon to the correct UUID and major number of the iBeacon Detector:
![image](https://s3.amazonaws.com/proxidyne-static/2017/03/23220755/IMG_1413.png)
* The iBeacon now shows up under Custom States in the Beacon Detector device:
![image](https://i2.wp.com/s3.amazonaws.com/proxidyne-static/2017/03/23220954/devices1.png?resize=754%2C724&ssl=1)


