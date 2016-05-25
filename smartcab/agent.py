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
        self.actions = None, 'forward', 'left', 'right'
        self.states = self.setup_states()

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.states = self.setup_states()

    def setup_states(self):
        self.states = []

    def determine_state_id(self, inputs, planner_action):
        if inputs == {'light': 'green', 'oncoming': None, 'right': None, 'left': None}:
            self.state_id = 0
        elif inputs == {'light': 'green', 'oncoming': 'forward', 'right': None, 'left': None} and planner_action == 'left':
            self.state_id = 1
        elif inputs == {'light': 'red', 'oncoming': None, 'right': None, 'left': None}:
            self.state_id = 2
        elif inputs == {'light': 'red', 'oncoming': None, 'right': None, 'left': None} and planner_action == 'right':
            self.state_id = 3
        elif inputs == {'light': 'red', 'oncoming': 'forward', 'right': None, 'left': None} and planner_action == 'left':
            self.state_id = 4
        elif inputs == {'light': 'red', 'oncoming': 'left', 'right': None, 'left': None} and planner_action == 'right':
            self_state_id = 5
        elif inputs == {'light': 'red', 'oncoming': None, 'right': forward, 'left': None}:
            self.state_id = 6
        elif inputs == {'light': 'red', 'oncoming': None, 'right': forward, 'left': 'forward'}:
            self.state_id = 7




    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        self.state = (self.next_waypoint, inputs)

        # TODO: Select action according to your policy
        action = random.choice(self.actions)  # Initial random movement

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward

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
