# Class to get dataref values from XPlane Flight Simulator via network. 
# License: GPLv3

import socket
import struct
import binascii
from time import sleep

class XPlaneIpNotFound(Exception):
  args="Could not find any running XPlane instance in network."

class XPlaneTimeout(Exception):
  args="XPlane timeout."

class XPlaneUdp:

  '''
  Get data from XPlane via network.
  Use a class to implement RAI Pattern for the UDP socket. 
  '''
  
  #constants
  MCAST_GRP = "239.255.1.1"
  MCAST_PORT = 49707 # (MCAST_PORT was 49000 for XPlane10)
  
  def __init__(self):
    # Open a UDP Socket to receive on Port 49000
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.socket.settimeout(3.0)
    # list of requested datarefs with index number
    self.datarefidx = 0
    self.datarefs = {} # key = idx, value = dataref
    # values from xplane
    self.BeaconData = {}
    self.xplaneValues = {}
    self.defaultFreq = 1

  def __del__(self):
    for i in range(len(self.datarefs)):
      self.AddDataRef(next(iter(self.datarefs.values())), freq=0)
    self.socket.close()

  def AddDataRef(self, dataref, freq = None):

    '''
    Configure XPlane to send the dataref with a certain frequency.
    You can disable a dataref by setting freq to 0. 
    '''

    idx = -9999

    if freq == None:
      freq = self.defaultFreq

    if dataref in self.datarefs.values():
      idx = list(self.datarefs.keys())[list(self.datarefs.values()).index(dataref)]
      if freq == 0:
        if dataref in self.xplaneValues.keys():
          del self.xplaneValues[dataref]
        del self.datarefs[idx]
    else:
      idx = self.datarefidx
      self.datarefs[self.datarefidx] = dataref
      self.datarefidx += 1
    
    cmd = b"RREF\x00"
    string = dataref.encode()
    message = struct.pack("<5sii400s", cmd, freq, idx, string)
    assert(len(message)==413)
    self.socket.sendto(message, (self.BeaconData["IP"], self.BeaconData["Port"]))
    if (self.datarefidx%100 == 0):
      sleep(0.2)

  def GetValues(self):
    try:
      # Receive packet
      data, addr = self.socket.recvfrom(1472) # maximum bytes of an RREF answer X-Plane will send (Ethernet MTU - IP hdr - UDP hdr)
      # Decode Packet
      retvalues = {}
      # * Read the Header "RREFO".
      header=data[0:5]
      if(header!=b"RREF,"): # (was b"RREFO" for XPlane10)
        print("Unknown packet: ", binascii.hexlify(data))
      else:
        # * We get 8 bytes for every dataref sent:
        #   An integer for idx and the float value. 
        values =data[5:]
        lenvalue = 8
        numvalues = int(len(values)/lenvalue)
        for i in range(0,numvalues):
          singledata = data[(5+lenvalue*i):(5+lenvalue*(i+1))]
          (idx,value) = struct.unpack("<if", singledata)
          if idx in self.datarefs.keys():
            # convert -0.0 values to positive 0.0 
            if value < 0.0 and value > -0.001 :
              value = 0.0
            retvalues[self.datarefs[idx]] = value
      self.xplaneValues.update(retvalues)
    except:
      raise XPlaneTimeout
    return self.xplaneValues

  def FindIp(self):

      '''
      Find the IP of XPlane Host in Network.
      It takes the first one it can find. 
      '''
    
      self.BeaconData = {}
      
      # open socket for multicast group. 
      sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
      sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      sock.bind((self.MCAST_GRP, self.MCAST_PORT))
      mreq = struct.pack("=4sl", socket.inet_aton(self.MCAST_GRP), socket.INADDR_ANY)
      sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
      sock.settimeout(3.0)
      
      while not self.BeaconData:
        
        # receive data
        try: 
          packet, sender = sock.recvfrom(1472)

          # decode data
          # * Header
          header = packet[0:5]
          if header != b"BECN\x00":
            print("Unknown packet from "+sender[0])
            print(str(len(packet)) + " bytes")
            print(packet)
            print(binascii.hexlify(packet))
            
          else:
            # * Data
            data = packet[5:21]
            # struct becn_struct
            # {
            # 	uchar beacon_major_version;		// 1 at the time of X-Plane 10.40
            # 	uchar beacon_minor_version;		// 1 at the time of X-Plane 10.40
            # 	xint application_host_id;			// 1 for X-Plane, 2 for PlaneMaker
            # 	xint version_number;			// 104014 for X-Plane 10.40b14
            # 	uint role;						// 1 for master, 2 for extern visual, 3 for IOS
            # 	ushort port;					// port number X-Plane is listening on
            # 	xchr	computer_name[strDIM];		// the hostname of the computer 
            # };
            beacon_major_version = 0
            beacon_minor_version = 0
            application_host_id = 0
            xplane_version_number = 0
            role = 0
            port = 0
            (
              beacon_major_version,  # 1 at the time of X-Plane 10.40
              beacon_minor_version,  # 1 at the time of X-Plane 10.40
              application_host_id,   # 1 for X-Plane, 2 for PlaneMaker
              xplane_version_number, # 104014 for X-Plane 10.40b14
              role,                  # 1 for master, 2 for extern visual, 3 for IOS
              port,                  # port number X-Plane is listening on
              ) = struct.unpack("<BBiiIH", data)
            computer_name = packet[21:-1]
            if beacon_major_version == 1 \
               and beacon_minor_version == 1 \
               and application_host_id == 1:
                self.BeaconData["IP"] = sender[0]
                self.BeaconData["Port"] = port
                self.BeaconData["hostname"] = computer_name.decode()
                self.BeaconData["XPlaneVersion"] = xplane_version_number
                self.BeaconData["role"] = role

        except socket.timeout:
          raise XPlaneIpNotFound()

      sock.close()
      return self.BeaconData

# Example how to use:
# You need a running xplane in your network. 
if __name__ == '__main__':

  xp = XPlaneUdp()

  try:
    beacon = xp.FindIp()
    print(beacon)
    print()
    
    xp.AddDataRef("sim/flightmodel/position/indicated_airspeed", freq=1)
    xp.AddDataRef("sim/flightmodel/position/latitude")
    
    while True:
      try:
        values = xp.GetValues()
        print(values)
      except XPlaneTimeout:
        print("XPlane Timeout")
        exit(0)

  except XPlaneIpNotFound:
    print("XPlane IP not found. Probably there is no XPlane running in your local network.")
    exit(0)
