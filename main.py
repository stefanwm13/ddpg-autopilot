#from packageReceiver import PackageReceiver
#from packageReceiver import DataRefs
#from packageSender import PackageSender
from Environment import EnvironmentTakeoff
import random
import time
import numpy as np

IP = '127.0.0.1'
RECV_PORT = 50001
SEND_PORT = 49000

#packageReceiver = PackageReceiver(IP, RECV_PORT)
#packageSender = PackageSender(IP, SEND_PORT)
#packageSender.sendAirportPlacementValues((-2382.1, -5.0181, -13175))
#packageSender.sendAirportReset()
env = EnvironmentTakeoff(IP, RECV_PORT, SEND_PORT)

while True:
    values = []
    s, r, d = env.step((0,))

    print "State:" ,s
    print "Reward: ", r

   # time.sleep(1)
# controls = packageReceiver.getValue(DataRefs.CONTROLS)
   # print 'Controls: ', controls

 #   position = packageReceiver.getValue(DataRefs.HEADING)
  #  print 'Position: ', position

   # throttle = packageReceiver.getValue(DataRefs.THROTTLE)
   # print 'Throttle: ', throttle
#    packageSender.sendControlAndThrottleValues(
#   (-999,
#   -999,
#   1,
#   -999,
#   -999))

#    time.sleep(1)

