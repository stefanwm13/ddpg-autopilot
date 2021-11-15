import tensorflow as tf
from ddpg import *
from EnvironmentLanding import EnvironmentLanding
import numpy as np
import gc
gc.enable()

ENV_NAME = 'InvertedPendulum-v1'
EPISODES = 100000
TEST = 10
SUMMARY_DIR = './results/landing_36'

def build_summaries():
    episode_reward = tf.Variable(0.)
    tf.summary.scalar("Reward", episode_reward)
    episode_ave_max_q = tf.Variable(0.)
    tf.summary.scalar("Qmax Value", episode_ave_max_q)
    average_height = tf.Variable(0.)
    tf.summary.scalar("Average height", average_height)
    
    summary_vars = [episode_reward, episode_ave_max_q, average_height]
    summary_ops = tf.summary.merge_all()

    return summary_ops, summary_vars


def main():
    IP = "127.0.0.1"
    RECV_PORT = 50001
    SEND_PORT = 49000

    env = EnvironmentLanding(IP, RECV_PORT, SEND_PORT)
    agent = DDPG(env)
    
    # Set up summary Ops
    summary_ops, summary_vars = build_summaries()
    
    writer = tf.summary.FileWriter(SUMMARY_DIR, agent.sess.graph)
    #env.monitor.start('experiments/' + ENV_NAME,force=True)

    for episode in xrange(EPISODES):
        state = env.reset()

        total_reward = 0
        ep_ave_max_q = 0
        average_height = 0
        
        for step in xrange(500000000):
            print "STEP:   ", step
            if episode < 1500:
                action = agent.noise_action(state)
            else:
                action = agent.action(state)
                
            next_state,reward,done = env.step(action, episode)
            predicted_q = agent.perceive(state,action,reward,next_state,done)
            
            state = next_state
            total_reward += reward
            try:
                ep_ave_max_q += np.amax(predicted_q)
            except ValueError:  #raised if `y` is empty.
                pass
            average_height += env.getHeight()
            step = step + 1
            
            if done:
                
                summary_str = agent.sess.run(summary_ops, feed_dict={
                    summary_vars[0]: total_reward,
                    summary_vars[1]: ep_ave_max_q / float(step + 1),
                    summary_vars[2]: average_height / float(step + 1)
                })
                
                writer.add_summary(summary_str, episode)
                writer.flush()
                build_summaries()
                print "EPISODE:    ", episode ,"|  REWARD:", total_reward, "|  Q_MAX:  ", ep_ave_max_q / float(step + 1)
                break
        ## Testing:
        #if episode % 100 == 0 and episode > 100:
			#total_reward = 0
			#for i in xrange(TEST):
				#state = env.reset()
				#for j in xrange(env.spec.timestep_limit):
					##env.render()
					#action = agent.action(state) # direct action for test
					#state,reward,done,_ = env.step(action)
					#total_reward += reward
					#if done:
						#break
			#ave_reward = total_reward/TEST
			#print 'episode: ',episode,'Evaluation Average Reward:',ave_reward
    #env.monitor.close()

if __name__ == '__main__':
    main()
