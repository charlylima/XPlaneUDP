XPlane UDP Examples in Python
===============================
Examples how get data from X-Plane Flight Simulator via Network Interface in Python3.

Tested with X-Plane version 10.45 on Debian Linux version 8 "jessie".

XPlane10UdpDataOutputReceiver.py
--------------------------------
Receive data that is sent by X-Plane after configuring it in the Settings Menu of X-Plane.
You need to enter the IP of the python skript machine into X-Plane settings.
You need select the data to send in the X-Plane GUI (configuration by user is needed).

XPlane10UdpRequestDataRefs.py
------------------------------
Request data from X-Plane without configuring it in X-Plane.
You need to enter the IP of the X-Plane Machine into the Python script.
You select the data to send in the python script as dataref strings like "sim/flightmodel/position/indicated_airspeed".

XPlane10MulticastBeacon.py
---------------------
Automatically find the IP of the X-Plane machine using X-Plane's multicast announcements.

License: 
--------
* 1) GPLv3
* 2) Consider it as programmer documentation, so you are free to copy some lines ignoring the License. 

Documentation:
--------------
* @see "X-Plane 10/Resources/plugins/DataRefs.txt"
* @see "X-Plane 10/Instructions/Sending Data to X-Plane.html"
* @see "X-Plane 10/Instructions/Sending Data to X-Plane.rtfd/TXT.rtf"

Links: 
------
* http://www.x-plane.com
* http://developer.x-plane.com
