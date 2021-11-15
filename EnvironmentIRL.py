from packageReceiver import PackageReceiver
from packageReceiver import DataRefs
from packageSender import PackageSender
import math
import numpy as np
import time

timeLimit = 0

class EnvironmentIRL:   
    def __init__(self, ip, recv_port, send_port, weights):
        print "Initizalized PackageSender"
        self.packageSender = PackageSender(ip, send_port)
        print "Initialized PackagReceiver"
        self.packageReceiver = PackageReceiver(ip, recv_port) 
        print "Init successful"
        
        baseLineObservation = self.sampleObservation()
        self.refHeading = baseLineObservation[0][0] / 359.0
        self.refPitch = baseLineObservation[1][0] / 90.0
        self.refRoll = self.packageReceiver.getValue(DataRefs.HEADING)[1][0] / 180.0
        self.refDistanceToDME = self.packageReceiver.getValue(DataRefs.ILS)[4][0] / 45.0
        self.EPSILON = 0.01
        self.DECISION_HEIGHT = 60

        self.reward = 0
        self.done = 0

        self.oldHeading = baseLineObservation[0][0] / 359.0
        self.oldPitch = 0

        self.W = weights
        self.timeElapsed = 0
        self.timeElapsed2 = 0
        self.timeGrabbed = False
        self.timeGrabbed2 = False
        self.timeGrabbed3 = False

        self.offsetTimeLimit = 0
        self.externalTimeLimit = 0


    #Reset environment
    def reset(self):
        self.done = 0
        self.reward = 0
        
        #Reset Location to airport
        self.packageSender.sendAirportReset()
        
        #Sampple observation twice to dismiss delayed packets
        for i in range(0, 35):
            self.sampleObservation()
        
        observation = self.sampleObservation()

        #Get all environment variables
        heading = self.refHeading
        pitch = self.refPitch
        onRunway = observation[2][0]
        speed = observation[3][0] / 115.0
        height = self.packageReceiver.getValue(DataRefs.POSITION)[2][0]
        normedHeight = height / 1000
        roll = self.packageReceiver.getValue(DataRefs.HEADING)[1][0] / 180.0
        noseWheel = self.packageReceiver.getValue(DataRefs.CONTROLS)[4][0] / 48.0
        centerDrift = self.getHeadingObservation(heading)
        rollDrift = self.getRollObservation(roll)
        distanceToDME = self.packageReceiver.getValue(DataRefs.ILS)[4][0] / 45
        angularQ = self.packageReceiver.getValue(DataRefs.ANGULAR)[0][0]
        angularP = self.packageReceiver.getValue(DataRefs.ANGULAR)[1][0]
        angularR = self.packageReceiver.getValue(DataRefs.ANGULAR)[2][0]


        return (speed, centerDrift, onRunway, noseWheel, distanceToDME, normedHeight, pitch / 90, rollDrift, angularQ, angularP, angularR)


    #Get base sample of observations in the environment
    def sampleObservation(self):
        heading = self.packageReceiver.getValue(DataRefs.HEADING)[2]
        pitch = self.packageReceiver.getValue(DataRefs.HEADING)[0]
        onRunway = self.packageReceiver.getValue(DataRefs.POSITION)[4]
        speed = self.packageReceiver.getValue(DataRefs.SPEED)[0]
        
        return (heading, pitch, onRunway, speed)

    
    #Release aircrafts brakes
    def releaseBrakes(self):
        self.packageSender.releaseBrakes()

    def airportReset(self):
        self.packageSender.sendAirportReset()
    
    def getHeight(self):
        return self.packageReceiver.getValue(DataRefs.POSITION)[2][0] / 1000

    def getSpeed(self):
	return self.packageReceiver.getValue(DataRefs.SPEED)[0][0]
    
    def getTime(self):
        return self.externalTimeLimit
    #Take a step in the environment
    def step(self, actionValues, save):
        #Execute action predicted from actor on aircraft
        self.packageSender.sendControlAndThrottleValues(actionValues)
        
        #Reset reward
        self.reward = 0
        
        timeLimit = 0

        #Get observation
        observation = self.sampleObservation()

        #Get all environment variables
        timeLimit = self.packageReceiver.getValue(DataRefs.TIMES)[2][0]
        headingThreshold = observation[0][0]
        pitch = observation[1][0] 
        onRunway = observation[2][0]
        speed = observation[3][0] / 115.0
        height = self.packageReceiver.getValue(DataRefs.POSITION)[2][0]
        stall = self.packageReceiver.getValue(DataRefs.WARNING)[6][0] * 2
        roll = self.packageReceiver.getValue(DataRefs.HEADING)[1][0] / 180.0
        noseWheel = self.packageReceiver.getValue(DataRefs.CONTROLS)[4][0] / 48.0
        normedHeight = height / 1000
        heading = headingThreshold / 359.0
        centerDrift = self.getHeadingObservation(heading)
        rollDrift = self.getRollObservation(roll)
        distanceToDME = self.packageReceiver.getValue(DataRefs.ILS)[4][0] / 45.0
        distanceToDME = self.refDistanceToDME - distanceToDME
        angularQ = self.packageReceiver.getValue(DataRefs.ANGULAR)[0][0]
        angularP = self.packageReceiver.getValue(DataRefs.ANGULAR)[1][0]
        angularR = self.packageReceiver.getValue(DataRefs.ANGULAR)[2][0]
        
        #If time limit threshod passed reset the environment
	print speed
        print time
        #if speed > 15 / 115.0 and not self.timeGrabbed3:
        #    self.offsetTimeLimit = time
        #    self.timeGrabbed3 = True
        
        #if self.timeGrabbed3:
        #    timeLimit = time - self.offsetTimeLimit
        #    self.externalTimeLimit = timeLimit
        #else:
        #    timeLimit = 0
        #    self.externalTimeLimit = 0
        
        print timeLimit
        if timeLimit > 80:
            self.timeGrabbed3 = False
            self.offsetTimeLimit = 0
            self.done = 1
                
        headingThresholdReward = 0
        if save and height < self.DECISION_HEIGHT: 
            if headingThreshold > (self.refHeading * 359.0) + 45 or headingThreshold < (self.refHeading * 359.0) - 45:
                if not self.timeGrabbed2:
                    print "Not Grabbed 2"
                    self.timeElapsed2 = timeLimit
                    self.timeGrabbed2 = True
                else:
                    headingThresholdReward += 1
                    print "Time2: ", timeLimit - self.timeElapsed2
                    print "TimeLImit2 : ", timeLimit
                    print "TimeElapse2 : ", self.timeElapsed2
                    if timeLimit - self.timeElapsed2 > 1:
                        self.done = 1
           
        if self.done == 1:
            self.timeGrabbed = False
            self.timeGrabbed2 = False
            self.timeGrabbed3 = False
                    
            
        #Get reward for leaving the runway 
        runwayReward = 0
        if save and height < self.DECISION_HEIGHT: 
            if onRunway == 0:
                if not self.timeGrabbed:
                    self.timeElapsed = timeLimit
                    self.timeGrabbed = True
                else:
                    runwayReward += 1
                    print "Time: ", timeLimit - self.timeElapsed
                    print "TimeLImit : ", timeLimit
                    print "TimeElapse : ", self.timeElapsed
                    if timeLimit - self.timeElapsed > 3:
                        self.done = 1
                
        if self.done == 1:
            self.timeGrabbed = False
            self.timeGrabbed2 = False
            self.timeGrabbed3 = False

        #maximize = (normedHeight + (0.1 * speed))
        #maximize = (normedHeight) + (pitch / 90.0)
        #minimize = (centerDrift + rollDrift + runwayReward + headingThresholdReward + stall) 
        
        maximize = distanceToDME + onRunway + normedHeight + (pitch / 90)
        minimize = centerDrift + runwayReward + headingThresholdReward + rollDrift

        #Accumulate reward
        self.reward += maximize - minimize
        
        #Update state variables
        #observationFinal = (normedHeight, speed, centerDrift, rollDrift, 
        #                    pitch / 90.0, noseWheel, distanceToDME)
       
        observationFinal = (speed, centerDrift, onRunway, noseWheel, distanceToDME, normedHeight, pitch / 90, rollDrift, angularQ, angularP, angularR)

        #Debug information
        print "Height Observation: ", normedHeight
        print "Heading Observation: ", centerDrift
        #print "Nosewheel Heading: ", noseWheel
        print "Pitch", pitch / 90.0
        print "Roll: ", rollDrift
        print "Speed: ", speed
        print "Runway: ", onRunway
        print "Stall: ", stall
        print "DME: ", distanceToDME
        print "Maximize: ", maximize
        print "Minimize: ", minimize

        return observationFinal, self.reward, self.done


    def getHeadingObservation(self, heading):
        if heading > self.refHeading:
            headingObservation = heading - self.refHeading
        else:
            headingObservation = self.refHeading - heading

        return headingObservation


    def getPitchObservation(self, pitch):
        pitchObservation = pitch

        return pitchObservation


    def getRollObservation(self, roll):
        if roll > self.refRoll:
            rollObservation = roll - self.refRoll
        else:
            rollObservation = self.refRoll - roll

        return rollObservation

    
    def getAttitudeObservation(self, pitch):
        if pitch <= 20.0:
            attitude = math.exp(-( pow(pitch - 20.0, 2) / (2 * pow(9, 2)) )) #Gaussian basis function
        elif pitch > 20.0 or pitch < -1.0:
            attitude = math.exp(-( pow(pitch - 20.0, 2) / (2 * pow(9, 2)) )) 
          
        return attitude
