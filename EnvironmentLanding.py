from packageReceiver import PackageReceiver
from packageReceiver import DataRefs
from packageSender import PackageSender
import math
import numpy as np
import time

class EnvironmentLanding:
    def __init__(self, ip, recv_port, send_port):
        print "Initizalized PackageSender"
        self.packageSender = PackageSender(ip, send_port)
        print "Initialized PackagReceiver"
        self.packageReceiver = PackageReceiver(ip, recv_port) 
        print "Init successful"
        
        self.reward = 0
        self.done = 0
        
        self.refHeading = 230.0 / 359.0
        self.refRoll = self.packageReceiver.getValue(DataRefs.HEADING)[1][0] / 180.0
        
        self.timeElapsed = 0
        self.timeElapsed2 = 0
        self.timeGrabbed = False
        self.timeGrabbed2 = False
        self.timeGrabbed3 = False
        
    def sampleObservation(self):
        timeLimit = self.packageReceiver.getValue(DataRefs.TIMES)[2][0]
        rpm = self.packageReceiver.getValue(DataRefs.RPM)[0][0]
        heading = self.packageReceiver.getValue(DataRefs.HEADING)[2][0] / 359.0
        roll = self.packageReceiver.getValue(DataRefs.HEADING)[1][0] / 180.0
        pitch = self.packageReceiver.getValue(DataRefs.HEADING)[0][0] / 90.0
        onRunway = self.packageReceiver.getValue(DataRefs.POSITION)[4][0]
        speed = self.packageReceiver.getValue(DataRefs.SPEED)[0][0] / 80.0
        throttle = self.packageReceiver.getValue(DataRefs.THROTTLE)[0][0]
        height = self.packageReceiver.getValue(DataRefs.POSITION)[2][0]
        normedHeight = height / 600
        distance = self.packageReceiver.getValue(DataRefs.GPS)[2][0] / 1.15
        centerDrift = self.getHeadingObservation(heading)
        rollDrift = self.getRollObservation(roll)
        angularQ = self.packageReceiver.getValue(DataRefs.ANGULAR)[0][0]
        angularP = self.packageReceiver.getValue(DataRefs.ANGULAR)[1][0]
        angularR = self.packageReceiver.getValue(DataRefs.ANGULAR)[2][0]
        hDef = self.packageReceiver.getValue(DataRefs.ILS)[5][0] / 2.5
        vDef = self.packageReceiver.getValue(DataRefs.ILS)[6][0] / 2.5

        return (timeLimit, heading, pitch, onRunway, speed, height, normedHeight, centerDrift, rollDrift, angularQ, angularQ, angularR, hDef, vDef, throttle, distance, rpm)
    
    def reset(self):
        self.done = 0
        self.reward = 0
        
        #Reset Location to airport
        self.packageSender.sendAirportReset()
        time.sleep(0.5)
        self.packageSender.sendAirportPlacementValues([0,0,0])
        
        #Sample observation twice to dismiss delayed packets
        #for i in range(0, 5):
        #    self.sampleObservation()
            
        observation = self.sampleObservation()   
        
        return (observation[2], 1, observation[3], observation[4], observation[6], observation[7], observation[8], observation[9], observation[10], observation[11],  observation[14], observation[15])
            
    def step(self, actionValues, iteration, save=True):
        #Execute action predicted from actor on aircraft
        self.packageSender.sendControlAndThrottleValues(actionValues)
        #Reset reward
        self.reward = 0
        
        timeLimit = 0
        
        #Get observation
        observation = self.sampleObservation()
        
        timeLimit = observation[0]
        heading = observation[1] * 359.0
        rpm = observation[16]
        hDef = abs(observation[12])
        vDef = abs(observation[13])
        normedHeight = observation[6]
        centerDrift = observation[7]
        onRunway = observation[3]
        rollDrift = observation[8]
        pitch = observation[2]
        speed = observation[4]
        distance = observation[15]
        
        if timeLimit > 90:
            self.done = 1

        ILSThresoldReward = 0
        pitchReward = 0
        damageReward = 0
        
        if save:
            if pitch > 20.0 / 90.0:
                print "Pitch Adjusted"
                if not self.timeGrabbed2:
                        print "Not Grabbed 2"
                        self.timeElapsed2 = timeLimit
                        self.timeGrabbed2 = True
                else:
                    pitchReward += 1
                    print "Time2: ", timeLimit - self.timeElapsed2
                    print "TimeLImit2 : ", timeLimit
                    print "TimeElapse2 : ", self.timeElapsed2
                    if timeLimit - self.timeElapsed2 > 2:
                        self.done = 1
            
            if iteration < 1000:
                if abs(heading - 230) > 30:
                    if not self.timeGrabbed2:
                        print "Not Grabbed 2"
                        self.timeElapsed2 = timeLimit
                        self.timeGrabbed2 = True
                        
                    else:
                        ILSThresoldReward += 1
                        print "Time2: ", timeLimit - self.timeElapsed2
                        print "TimeLImit2 : ", timeLimit
                        print "TimeElapse2 : ", self.timeElapsed2
                        if timeLimit - self.timeElapsed2 > 2:
                            self.done = 1
                elif hDef < 0.000001 or rpm < 200:
                    if not self.timeGrabbed2:
                        print "Not Grabbed 2"
                        self.timeElapsed2 = timeLimit
                        self.timeGrabbed2 = True
                        
                    else:
                        damageReward += 1
                        print "Time2: ", timeLimit - self.timeElapsed2
                        print "TimeLImit2 : ", timeLimit
                        print "TimeElapse2 : ", self.timeElapsed2
                        if timeLimit - self.timeElapsed2 > 2:
                            self.done = 1
            elif iteration < 2000:
                if abs(heading - 230) > 20:
                    if not self.timeGrabbed2:
                        print "Not Grabbed 2"
                        self.timeElapsed2 = timeLimit
                        self.timeGrabbed2 = True
                        
                    else:
                        ILSThresoldReward += 1
                        print "Time2: ", timeLimit - self.timeElapsed2
                        print "TimeLImit2 : ", timeLimit
                        print "TimeElapse2 : ", self.timeElapsed2
                        if timeLimit - self.timeElapsed2 > 2:
                            self.done = 1
                elif hDef < 0.000001 or rpm < 200:
                    if not self.timeGrabbed2:
                        print "Not Grabbed 2"
                        self.timeElapsed2 = timeLimit
                        self.timeGrabbed2 = True
                        
                    else:
                        damageReward += 1
                        print "Time2: ", timeLimit - self.timeElapsed2
                        print "TimeLImit2 : ", timeLimit
                        print "TimeElapse2 : ", self.timeElapsed2
                        if timeLimit - self.timeElapsed2 > 2:
                            self.done = 1
            else:
                if abs(heading - 230) > 20:
                    if not self.timeGrabbed2:
                        print "Not Grabbed 2"
                        self.timeElapsed2 = timeLimit
                        self.timeGrabbed2 = True
                        
                    else:
                        ILSThresoldReward += 1
                        print "Time2: ", timeLimit - self.timeElapsed2
                        print "TimeLImit2 : ", timeLimit
                        print "TimeElapse2 : ", self.timeElapsed2
                        if timeLimit - self.timeElapsed2 > 2:
                            self.done = 1
                elif hDef < 0.000001 or rpm < 200:
                    if not self.timeGrabbed2:
                        print "Not Grabbed 2"
                        self.timeElapsed2 = timeLimit
                        self.timeGrabbed2 = True
                        
                    else:
                        damageReward += 1
                        print "Time2: ", timeLimit - self.timeElapsed2
                        print "TimeLImit2 : ", timeLimit
                        print "TimeElapse2 : ", self.timeElapsed2
                        if timeLimit - self.timeElapsed2 > 2:
                            self.done = 1
                
                
        if abs(heading - 230) > 10:
            onTrack = 0
        else:
            onTrack = 1
            
        if self.done == 1:
            self.timeGrabbed = False
            self.timeGrabbed2 = False
            self.timeGrabbed3 = False
            
            
        #maximize = onRunway
        #minimize = hDef + vDef + centerDrift + ILSThresoldReward + rollDrift + speed + normedHeight + pitch + 5*distance
        
        maximize = onTrack + onRunway + 2*(1 - distance) + ((1 - distance) * (1 - normedHeight))
        minimize = centerDrift + ILSThresoldReward + rollDrift + pitchReward + damageReward
        
        self.reward += maximize - minimize
        
        observationFinal = (pitch, onTrack, onRunway, speed, normedHeight, centerDrift, rollDrift, observation[9], observation[10], observation[11], observation[14], observation[15])
        #Debug information
        print "Height Observation: ", ((1 - distance) * (1 - normedHeight))
        print "Heading Observation: ", centerDrift
        print "Heading Observation: ", abs(heading - 230)
        print "Pitch", pitch
        print "Roll: ", rollDrift
        #print "Speed: ", speed
        print "Runway: ", onRunway
        print "OnTrack", onTrack
        #print "hDef: ", hDef
        #print "vDef: ", vDef
        #print "distance:", distance
        print "Maximize: ", maximize
        print "Minimize: ", minimize
        
        return observationFinal, self.reward, self.done
        
    def getHeight(self):
        return self.packageReceiver.getValue(DataRefs.POSITION)[2][0] / 600
    
    def airportReset(self):
        self.packageSender.sendAirportReset()
        time.sleep(0.5)
        self.packageSender.sendAirportPlacementValues([0,0,0])
        
    def getHeadingObservation(self, heading):
        if heading > self.refHeading:
            headingObservation = heading - self.refHeading
        else:
            headingObservation = self.refHeading - heading

        return headingObservation
        
    def getRollObservation(self, roll):
        if roll > self.refRoll:
            rollObservation = roll - self.refRoll
        else:
            rollObservation = self.refRoll - roll

        return rollObservation
