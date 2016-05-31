import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator


class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.possible_actions = [None, 'forward', 'left', 'right']
        self.init_actions_rewards = dict({'None': self.set_initial_q(),
                             'forward': self.set_initial_q(),
                             'left': self.set_initial_q(),
                             'right': self.set_initial_q()})
        # self.states = self.setup_states()  # TODO - is this needed now?
        self.q = dict()
        self.iteration_0 = True

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.iteration_0 = True  # TODO: Assume we do this every time for now...

    def set_initial_q(self):
        #TODO - Determine optimal initialisation value
        return 0

    # TODO - Make this work with multiple actions and rewards!
    def new_state(self, state, structure = {"state": {}, "actions_rewards": {}}):
        next_entry = len(self.q)
        self.q[next_entry] = dict(structure)
        self.q[next_entry]["state"] = state
        self.q[next_entry]["actions_rewards"] = self.init_actions_rewards()
        return next_entry

    def set_state(self, id, state):
        self.q[id]["state"] = state

    def set_action(self, id, state, action, reward):
        #TODO - Rework this whole thing!!
        # Needs to find out if we can find a matching state first,
        # create one if we don't
        # Set the relevant action's reward (or modify it using q-learning eventually!)
        self.q[id]["actions_rewards"] = action


    # 1) Sense the environment (see what changes occur naturally in the environment) - store it as state_0
    # 2) Take an action/reward - store as action_0 & reward_0
    #
    # In the next iteration
    # 1) Sense environment (see what changes occur naturally and from an action) - store as state_1
    # 2) Update the Q-table using state_0, action_0, reward_0, state_1
    # 3) Take an action - get a reward
    # 4) Repeat
    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        if self.iteration_0 == True:
            # TODO: Make this more elegant!!! And searchable!!
            self.q[0] = dict()
            self.q[0] = {"state": {}, "actions_rewards": {}}
            self.q[0]["state"] = dict()
            self.q[0]["state"] = { "inputs": inputs, "agent_action": self.next_waypoint}
            print "update(): Setting q[0][state] to {}".format(self.q[0]["state"])

        # TODO: Select action according to your policy
        # action = None
        action = random.choice(self.possible_actions)

        # Execute action and get reward
        reward = self.env.act(self, action)
        if self.iteration_0 == True:
            self.q[0]["action"] = action
            self.q[0]["reward"] = reward
            print "update(): Setting q[0][action & reward] to {} & {}".format(self.q[0]["action"], self.q[0]["reward"])
            self.iteration_0 = False
            # TODO - Save this state, etc. for the next iteration as prev_state

        # TODO: Learn policy based on state, action, reward

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs,
                                                                                                    action,
                                                                                                    reward)  # [debug]


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
