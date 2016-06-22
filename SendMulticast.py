# Example: Send something to multicast group. 

# License: 
# 1) GPLv3
# 2) Consider it as programmer documentation, so you are free to copy some lines ignoring the License. 

MCAST_GRP = "239.255.1.1"
MCAST_PORT = 49000

import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
sock.sendto(b"test", (MCAST_GRP, MCAST_PORT))

