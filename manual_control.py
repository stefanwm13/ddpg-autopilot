from packageReceiver import PackageReceiver
from packageReceiver import DataRefs
import numpy as np

GAMMA = 0.99

def main():
     packageReceiver = PackageReceiver("127.0.0.1", 50001)
     refHeading = packageReceiver.getValue(DataRefs.HEADING)[2][0] / 359.0
     refPitch = packageReceiver.getValue(DataRefs.HEADING)[0][0] / 90.0
     featureExpectations = np.zeros(3)
     i = 0
     
     while True:
         i += 1

         heading = packageReceiver.getValue(DataRefs.HEADING)[2][0] / 359.0
         pitch = packageReceiver.getValue(DataRefs.HEADING)[0][0] / 90.0
         onRunway = packageReceiver.getValue(DataRefs.POSITION)[4][0]

         headingObservation = getHeadingObservation(heading, refHeading)
         pitchObservation = getPitchObservation(pitch, refPitch)
         
         readings = [headingObservation, pitchObservation, onRunway]
         
         print readings
         featureExpectations += (GAMMA**(i))*np.array(readings)
         print featureExpectations
        
         if i > 2000:
            break


     print featureExpectations
         

         
def getHeadingObservation(heading, refHeading):
    if heading > refHeading:
        headingObservation = (heading) - (refHeading)
    else:
        headingObservation = (refHeading) - (heading)

    return headingObservation


def getPitchObservation(pitch, refPitch):
    if pitch > refPitch:
        pitchObservation = pitch
    else:
        pitchObservation = 0

    return pitchObservation
   

main()
