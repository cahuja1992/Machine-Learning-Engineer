import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import math
from collections import namedtuple
from QLearningAgent import QLearningAgent
import pprint
import numpy as np
import pandas as pd
import os


class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        """
        initializes the environment variables
        input: env, initializes the environment variable for sensing

        working: also responsible for initializing the color of the car,
        initializing the route planner and the reward and previous action.
        """
        super(LearningAgent, self).__init__(env)  
        self.color = 'black'  
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        self.previous_reward = 0
        self.previous_action = None
        self.n_actions = 0.0
        self.n_rewards = 0.0
        self.n_penalty = 0.0
        self.trial = 1
        self.output_writer = []

        try:
        	os.remove("agent1.csv")
        	os.remove("qLearningTunning1.csv")
        except:
        	pass


    def reset(self, destination=None):
        """
        reset values to start a new trial run
        """
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.previous_reward = 0
        self.previous_action = None
        self.state = None
        
        self.n_actions = 0.0
        self.n_rewards = 0.0
        self.n_penalty = 0.0

        self.trial+=0

    def update(self, t):
        """
        Main update method that is responsible for updating the agent action.
        """
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # Update state
        ## currently using two states called random and initiated
        # if(self.state == None):
        #     #self.state = 'Random'
        #self.state = 'light: {}, left: {}, oncoming: {}, next_waypoint: {}'.format(inputs['light'],inputs['left'],inputs['oncoming'],self.next_waypoint)

        self.state = 'light: {}, left: {}, oncoming: {}, next_waypoint: {}'.format(inputs['light'],inputs['left'],inputs['oncoming'],self.next_waypoint)
        current_env_state = self.env.sense(self)
        action = None

        possible_actions = []
        if(current_env_state['light'] == 'red'):
            if(current_env_state['oncoming'] != 'left'):
                possible_actions = ['right', None]
        else:
            # traffic ligh is green and now check for oncoming
            #if no oncoming 
            if(current_env_state['oncoming'] == 'forward'):
                possible_actions = [ 'forward','right']
            else:
                possible_actions = ['right','forward', 'left']
        
        # TODO: Select action according to your policy
        if possible_actions != [] and self.state == 'Random':
            action_int =  random.randint(0,len(possible_actions)-1)
            action = possible_actions[action_int]
        elif possible_actions != [] and self.state == 'Initiated':
            action = self.previous_action
            
        # Execute action and get reward
        reward = self.env.act(self, action)

        if(action != None):
            if(reward > self.previous_reward):
                self.state = 'Initiated'
                self.previous_action = action
                self.previous_reward = reward
            else:
                self.state = 'Random'
                self.previous_action = action
                self.previous_reward = reward

        self.n_actions += 1.0
        self.n_rewards += reward

        if reward < 0: 
        	self.n_penalty += 1
        	print "Negative reward: inputs = {}, action = {}, reward = {}, waypoint {}".format(inputs, action, reward, self.next_waypoint)

        # with open("agent.csv", "a") as myfile:
        # 	myfile.write("{},{},{},{},{}{}".format(self.n_actions, inputs, action, reward, self.next_waypoint,'\n'))

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}, waypoint = {}".format(deadline, inputs, action, reward, self.next_waypoint)  # [debug]

###
def parameterTunning(alphas=[],gammas=[]):
    for alpha in alphas:
        for gamma in gammas:
            print "alpha: {}, gamma = {}".format(alpha,gamma)
            
            a = run(isQLearn=True,alpha=alpha, gamma=gamma)

            with open("qLearningTunning1.csv", "a") as myfile:
            	myfile.write("{},{},{},{},{}{}".format(alpha,gamma,a.n_actions,a.n_rewards,a.n_penalty,'\n'))


def allPossibleStates():
    states = ["next_waypoint","destination","location",
                "destination","light","oncoming","left","right","heading"]
    return states

def run(isQLearn=False,alpha=0.00,gamma=0.00):
    """Run the agent for a finite number of trials."""
    agent = None

    e = Environment()  # create environment (also adds some dummy traffic)
    qLearnAgent = e.create_agent(QLearningAgent,alpha,gamma)  # create agent
    randomLearnAgent = e.create_agent(LearningAgent)  # create agent

    if(isQLearn):
    	agent=qLearnAgent
    else:
    	agent=randomLearnAgent

    e.set_primary_agent(agent, enforce_deadline=True)
    sim = Simulator(e, update_delay=0.00001)  # reduce update_delay to speed up simulation
    sim.run(n_trials=100)  # press Esc or close pygame window to quit

    return agent


if __name__ == '__main__':
	alphas = [num*1.0/10 for num in range(1,10)]
	gammas = [num*1.0/10 for num in range(1,10)]

	#parameterTunning(alphas,gammas)

	run(True,0.9,0.3)
