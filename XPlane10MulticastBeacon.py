# Example how to find out X-Plane host's IP-Address using X-Planes multicast beacons. 

# License: 
# 1) GPLv3
# 2) Consider it as programmer documentation, so you are free to copy some lines ignoring the License. 

import socket
import struct
import binascii

# In order to subscribe to X-Plane's BEACON, you must join the
# multicast group 239.255.1.1 and listen on port 49000.
MCAST_GRP = "239.255.1.1"
MCAST_PORT = 49000

def DecodeBeacon(packet, sender):
  BeaconData = {}

  # Header
  header = packet[0:5]
  if header != b"BECN\x00":
    print("Unknown packet from "+sender[0])
    print(str(len(packet)) + " bytes")
    print(packet)
    print(binascii.hexlify(packet))
    
  else:
    # Decode Data
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
        BeaconData["IP"] = sender[0]
        BeaconData["Port"] = port
        BeaconData["hostname"] = computer_name.decode()
        BeaconData["XPlaneVersion"] = xplane_version_number
        BeaconData["role"] = role
  return BeaconData

def main():
  # open socket for multicast group. 
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind((MCAST_GRP, MCAST_PORT))
  mreq = struct.pack("=4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
  sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

  while True:
    # receive data
    data, sender = sock.recvfrom(15000)
    # decode data
    beacon = DecodeBeacon(data, sender)
    print(beacon)
    # Example:
    # {
    #  'IP': '10.10.0.160',
    #  'Port': 49000,
    #  'XPlaneVersion': 104503,
    #  'hostname': 'flusi',
    #  'role': 1
    # }
    print()

if __name__ == '__main__':
  main()

