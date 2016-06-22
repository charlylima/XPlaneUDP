# Example how to request UDP data from X-Plane 10 in Python3. 

# License: 
# 1) GPLv3
# 2) Consider it as programmer documentation, so you are free to copy some lines ignoring the License. 

# Send the RREF command to X-Plane to request regularly sent datarefs. 
# X-Plane should send the messages right back to the IP address and port number
# you sent the RREF command from.
#
# Send this data structure to X-Plane,
#   dref_freq is times per second you get the data, 
#   dref_en is an integer index to request multiple datarefs,
#   dref_string is a null terminated string like “sim/flightmodel/engine/POINT_thrust[0]“. 
# Set dref_freq to 0 to stop sending. 
# "RREF\x00"
# struct dref_struct_in
# {
# 	xint dref_freq		;
# 	xint dref_en		;
# 	xchr dref_string[400]	;
# };
#
# You will get an array of this data structure back:
# "RREFO"
# struct dref_struct_out
# {
# 	xint dref_en	;
# 	xflt dref_flt	;
# };

# IP Address of machine running X-Plane. 
UDP_IP = "10.10.0.160"
UDP_PORT = 49000

import socket
import struct 

# List of datarefs to request. 
datarefs = [
    # ( dataref, unit, description, num decimals to display in formatted output )
    ("sim/flightmodel/position/latitude","°N","The latitude of the aircraft",6),
    ("sim/flightmodel/position/longitude","°E","The longitude of the aircraft",6),
    ("sim/flightmodel/misc/h_ind", "ft", "",0),
    ("sim/flightmodel/position/y_agl","m", "AGL", 0), 
    ("sim/flightmodel/position/mag_psi", "°", "The real magnetic heading of the aircraft",0),
    ("sim/flightmodel/position/indicated_airspeed", "kt", "Air speed indicated - this takes into account air density and wind direction",0), 
    ("sim/flightmodel/position/groundspeed","m/s", "The ground speed of the aircraft",0),
    ("sim/flightmodel/position/vh_ind", "m/s", "vertical velocity",1)
  ]

def DecodePacket(data):
  retvalues = {}
  # Read the Header "RREFO".
  header=data[0:5]
  if(header!=b"RREFO"):
    print("Unknown packet: ", binascii.hexlify(data))
  else:
    # We get 8 bytes for every dataref sent:
    #    An integer for idx and the float value. 
    values =data[5:]
    lenvalue = 8
    numvalues = int(len(values)/lenvalue)
    idx=0
    value=0
    for i in range(0,numvalues):
      singledata = data[(5+lenvalue*i):(5+lenvalue*(i+1))]
      (idx,value) = struct.unpack("<if", singledata)
      retvalues[idx] = (value, datarefs[idx][1], datarefs[idx][0])
  return retvalues

def main():
  # Open a Socket on UDP Port 49000
  sock = socket.socket(socket.AF_INET, # Internet
                       socket.SOCK_DGRAM) # UDP

  for idx,dataref in enumerate(datarefs):
    # Send one RREF Command for every dataref in the list.
    # Give them an index number and a frequency in Hz.
    # To disable sending you send frequency 0. 
    cmd = b"RREF\x00"
    freq=1
    string = datarefs[idx][0].encode()
    message = struct.pack("<5sii400s", cmd, freq, idx, string)
    assert(len(message)==413)
    sock.sendto(message, (UDP_IP, UDP_PORT))

  while True:
    # Receive packet
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    # Decode Packet
    values = DecodePacket(data)
    # Example values:
    # {
    #   0: (  47.85240554 , '°N'  , 'sim/flightmodel/position/latitude'           ),
    #   1: (  12.54742622 , '°E'  , 'sim/flightmodel/position/longitude'          ),
    #   2: (  1502.2      , 'ft'  , 'sim/flightmodel/misc/h_ind'                  ),
    #   3: (  0.01        , 'm'   , 'sim/flightmodel/position/y_agl'              ),
    #   4: (  76.41       , '°'   , 'sim/flightmodel/position/mag_psi'            ),
    #   5: ( -9.76e-05    , 'kt'  , 'sim/flightmodel/position/indicated_airspeed' ),
    #   6: (  1.39e-05    , 'm/s' , 'sim/flightmodel/position/groundspeed'        ),
    #   7: ( -1.37e-06    , 'm/s' , 'sim/flightmodel/position/vh_ind'             )
    # }

    # Print Values:
    for key,val in values.items():
      print(("{0:10."+str(datarefs[key][3])+"f} {1:<5} {2}").format(val[0],val[1],val[2]))
    print()
    # Example:
    # 47.852406 °N    sim/flightmodel/position/latitude
    # 12.547426 °E    sim/flightmodel/position/longitude
    #      1502 ft    sim/flightmodel/misc/h_ind
    #         0 m     sim/flightmodel/position/y_agl
    #        76 °     sim/flightmodel/position/mag_psi
    #        -0 kt    sim/flightmodel/position/indicated_airspeed
    #         0 m/s   sim/flightmodel/position/groundspeed
    #      -0.0 m/s   sim/flightmodel/position/vh_ind

if __name__ == '__main__':
  main()
