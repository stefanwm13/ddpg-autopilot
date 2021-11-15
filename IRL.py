from ddpg import ActorNetwork
from ddpg import CriticNetwork
import ddpg
from EnvironmentIRL import EnvironmentIRL

import tensorflow as tf
import tflearn
import time
import numpy as np
import scipy
import subprocess
from cvxopt import matrix 
from cvxopt import solvers #convex optimization library

# Max training steps
MAX_EPISODES = 2
# Max episode length
MAX_EP_STEPS = 1000
# Base learning rate for the Actor network
ACTOR_LEARNING_RATE = 0.0001
# Base learning rate for the Critic Network
CRITIC_LEARNING_RATE = 0.001
# Discount factor
GAMMA = 0.99
# Soft target update param
TAU = 0.001


class irlAgent:
    def __init__(self, randomFE, expertFE, epsilon, num_states, num_frames, behavior):
        self.randomPolicy = randomFE
        self.expertPolicy = expertFE
        self.num_states = num_states
        self.num_frames = num_frames
        self.behavior = behavior
        self.epsilon = epsilon
        self.randomT = np.linalg.norm(np.asarray(self.expertPolicy)-np.asarray(self.randomPolicy))
        self.policiesFE = {self.randomT:self.randomPolicy} # storing the policies and their respective t values in a dictionary
        print ("Expert - Random at the Start (t) :: " , self.randomT) 
        self.currentT = self.randomT
        self.minimumT = self.randomT
	self.actor = None
	self.critic = None
	self.env = None

    def getRLAgentFE(self, W, i):
        print "Starting Training"
	cmd = "rm saved_models/*"
        x = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	print "Deleted Models"
        result = ddpg.start(W, i, True)
	print result
        return result

    def policyListUpdater(self, W, i):
        tempFE = self.getRLAgentFE(W, i)
	print "HEY"
	f = open('tempFE.txt', 'a')
	f.write(str(tempFE))
        f.write('\n')
        f.close()
        print "TEMPFE: ", tempFE
        hyperDistance = np.abs(np.dot(W, np.asarray(self.expertPolicy)-np.asarray(tempFE))) #hyperdistance = t
        self.policiesFE[hyperDistance] = tempFE

        return hyperDistance # t = (weights.tanspose)*(expert-newPolicy)

    def optimalWeightFinder(self):
       
        i = 1
        while True:
            f = open('weights.txt', 'a')
            print ("IRL I VALUE: ", i)
            W = self.optimization() # optimize to find new weights in the list of policies
            print ("weights ::", W )
            f.write(str(W))
            f.write('\n')
            print ("the distances  ::", self.policiesFE.keys())
            self.currentT = self.policyListUpdater(W, i)
            print ("Current distance (t) is:: ", self.currentT )
            f.close()
            if self.currentT <= self.epsilon: # terminate if the point reached close enough
                break
            i += 1
        
        return W

    def optimization(self): # implement the convex optimization, posed as an SVM problem
        m = len(self.expertPolicy)
        P = matrix(2.0*np.eye(m), tc='d') # min ||w||
        q = matrix(np.zeros(m), tc='d')
        policyList = [self.expertPolicy]
        h_list = [1]
        for i in self.policiesFE.keys():
            print "Solvers: ", i
            policyList.append(self.policiesFE[i])
            h_list.append(1)
        policyMat = np.matrix(policyList)
        policyMat[0] = -1*policyMat[0]
        G = matrix(policyMat, tc='d')
        h = matrix(-np.array(h_list), tc='d')
        sol = solvers.qp(P,q,G,h)
        
        weights = np.squeeze(np.asarray(sol['x']))
        norm = np.linalg.norm(weights)
        weights = weights/norm
        
        return weights # return the normalized weights

if __name__ == '__main__':
	randomPolicyFE = [1.34, 0.8239238, 80.0]
	expertPolicyFE = [0.43118406, 4.20342582, 96.30815239]

	IP = "127.0.0.1"
	RECV_PORT = 50001
	SEND_PORT = 49000

	state_dim = 3
	action_dim = 2
	action_bound = 0.65

	epsilon = 0.1
	irlearner = irlAgent(randomPolicyFE, expertPolicyFE, epsilon, 2, 0, "test")
	print (irlearner.optimalWeightFinder())
