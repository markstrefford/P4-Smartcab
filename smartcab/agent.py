import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import numpy as np
import pandas as pd

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.actions = [None, 'forward', 'left', 'right']
        self.dict_actions = dict()   # Default dict for q-values
        self.dict_actions = {'None':    self.set_initial_q(),
                             'forward': self.set_initial_q(),
                             'left':    self.set_initial_q(),
                             'right':   self.set_initial_q()}
        self.states = self.setup_states() # TODO - is this needed now?
        self.q = dict()

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.states = self.setup_states() # TODO - is this needed now?

    def setup_states(self):
        self.states = dict()

    def determine_state(self, inputs, planner_action):
        if inputs == {'light': 'green', 'oncoming': None, 'right': None, 'left': None}:
            state_id = 1
        elif inputs == {'light': 'green', 'oncoming': 'forward', 'right': None, 'left': None} and planner_action == 'left':
            state_id = 2
        elif inputs == {'light': 'red', 'oncoming': None, 'right': None, 'left': None}:
            state_id = 3
        elif inputs == {'light': 'red', 'oncoming': None, 'right': None, 'left': None} and planner_action == 'right':
            state_id = 4
        elif inputs == {'light': 'red', 'oncoming': 'forward', 'right': None, 'left': None} and planner_action == 'left':
            state_id = 5
        elif inputs == {'light': 'red', 'oncoming': 'left', 'right': None, 'left': None} and planner_action == 'right':
            state_id = 6
        elif inputs == {'light': 'red', 'oncoming': None, 'right': 'forward', 'left': None}:
            state_id = 7
        elif inputs == {'light': 'red', 'oncoming': None, 'right': 'forward', 'left': 'forward'}:
            state_id = 8
        else:
            state_id = 0 # Catch-all state that shouldn't really happen, but does occasionally!
        return state_id

    def determine_action(self, state, actions):
        # We are adding qvalues based on an action, so there are times when we won't have any q-values defined
        # In that case then pick an action from the possible actions
        possible_actions = actions
        if state in self.q or random.random() < 0.2 :  # Try something new 20% of the time
            print "Determining optimal action based on state {} and q-values {}".format(state, self.q[state])
            # From http://stackoverflow.com/a/268350/1378071
            # Assumes a single best action, or if not it'll take the first one
            #possible_actions = max(self.q[state], key=lambda k: self.q[state][k])
            possible_actions = [action for action, q in self.q[state].iteritems() if q == max(self.q[state].values())]
            print "possible actions {} based on q-value {} for state {}".format(possible_actions, self.q[state], state)

        action = random.choice(possible_actions)
        print "action {} picked from possible actions {}".format(action, possible_actions)
        if action == 'None':
            action = None
        return action

    def set_initial_q(self):
        #TODO - Determine optimal initialisation value
        return 0

    def update_q(self, current_value, reward):
        #TODO: Implement stuff around alpha and gamma here???
        new_q = reward
        print "qvalue changing from {} to {}".format(current_value, new_q)
        return new_q

    def update_qvalue(self, state, action, reward):
        if state in self.q:
            print "Updating qvalue for state {} and action {} to {}".format(state, action, reward)
            print "Before {}".format(self.q[state][action])
            self.q[state][action] = self.update_q(self.q[state][action], reward)
            print "After {}".format(self.q[state][action])
        else:
            self.q[state] = dict()
            self.q[state] = self.dict_actions
            self.q[state][action] = self.update_q(self.q[state][action], reward)

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        self.state = self.determine_state(inputs, self.next_waypoint)

        # TODO: Select action according to your policy
        #action = random.choice(self.actions)  # Initial random movement
        action = self.determine_action(self.state, self.actions)

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        # Start with simply storing the reward that we get - determine which one is best here!!
        #self.states[self.state, str(action)] = reward
        self.update_qvalue(self.state, str(action), reward)

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]
        print "LearningAgent.update(): state = {}, waypoint = {}".format(self.state, self.next_waypoint)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=False)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.5, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
