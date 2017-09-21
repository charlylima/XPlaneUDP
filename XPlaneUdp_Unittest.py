import unittest
import XPlaneUdp as xplib

class TestXplaneUdp(unittest.TestCase):

  """ Unittest for XPlaneUDP.py """
  """ To run the test you need a running xplane in your network. """
  
  def test1(self):
    
    xp = xplib.XPlaneUdp()
    xp.defaultFreq = 100

    beacon = xp.FindIp()
    print(beacon)
    print()
    self.assertTrue( beacon )
    
    xp.AddDataRef("sim/flightmodel/position/indicated_airspeed", freq=100)
    xp.AddDataRef("sim/flightmodel/position/latitude")
        
    values = xp.GetValues()
    print(values)
    self.assertEqual( values.keys() , {"sim/flightmodel/position/indicated_airspeed", "sim/flightmodel/position/latitude"} )
    values = xp.GetValues()
    print(values)
    self.assertEqual( values.keys() , {"sim/flightmodel/position/latitude", "sim/flightmodel/position/indicated_airspeed"} )

    xp.AddDataRef("sim/flightmodel/position/latitude",0)
    values = xp.GetValues()
    print(values)
    self.assertEqual( values.keys() , {"sim/flightmodel/position/indicated_airspeed"} )
    values = xp.GetValues()
    print(values)
    self.assertEqual( values.keys() , {"sim/flightmodel/position/indicated_airspeed"} )

    xp.AddDataRef("sim/flightmodel/position/indicated_airspeed", freq=200)
    xp.AddDataRef("sim/flightmodel/position/longitude")
    values = xp.GetValues()
    print(values)
    self.assertEqual( values.keys() , {"sim/flightmodel/position/indicated_airspeed", "sim/flightmodel/position/longitude"} )
    values = xp.GetValues()
    print(values)
    self.assertEqual( values.keys() , {"sim/flightmodel/position/indicated_airspeed", "sim/flightmodel/position/longitude"} )
    values = xp.GetValues()
    print(values)
    self.assertEqual( values.keys() , {"sim/flightmodel/position/indicated_airspeed", "sim/flightmodel/position/longitude"} )
    values = xp.GetValues()
    print(values)
    self.assertEqual( values.keys() , {"sim/flightmodel/position/indicated_airspeed", "sim/flightmodel/position/longitude"} )

    xp.AddDataRef("sim/flightmodel/position/latitude",0)
    values = xp.GetValues()
    print(values)
    self.assertEqual( values.keys() , {"sim/flightmodel/position/indicated_airspeed", "sim/flightmodel/position/longitude"} )
    values = xp.GetValues()
    print(values)
    self.assertEqual( values.keys() , {"sim/flightmodel/position/indicated_airspeed", "sim/flightmodel/position/longitude"} )

    xp.AddDataRef("sim/flightmodel/position/latitude",100)
    values = xp.GetValues()
    print(values)
    self.assertEqual( values.keys() , {"sim/flightmodel/position/indicated_airspeed", "sim/flightmodel/position/longitude", "sim/flightmodel/position/latitude"} )
    values = xp.GetValues()
    print(values)
    self.assertEqual( values.keys() , {"sim/flightmodel/position/indicated_airspeed", "sim/flightmodel/position/longitude", "sim/flightmodel/position/latitude"} )
    values = xp.GetValues()
    print(values)
    self.assertEqual( values.keys() , {"sim/flightmodel/position/indicated_airspeed", "sim/flightmodel/position/longitude", "sim/flightmodel/position/latitude"} )
    values = xp.GetValues()
    print(values)
    self.assertEqual( values.keys() , {"sim/flightmodel/position/indicated_airspeed", "sim/flightmodel/position/longitude", "sim/flightmodel/position/latitude"} )

    xp = None

    # Check that XPlane does no longer send datarefs:
    xp = xplib.XPlaneUdp()
    xp.FindIp()
    with self.assertRaises(xplib.XPlaneTimeout):
      xp.GetValues()
    xp = None

    
if __name__ == '__main__':
  unittest.main()
