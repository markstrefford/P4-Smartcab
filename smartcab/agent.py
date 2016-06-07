import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

# TODO - Clarify logging over what is current state, previous state, next state, etc...

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.possible_actions = [None, 'forward', 'left', 'right']
        self.states = dict()        # self.states[] is just the state key-value lookup table, so no actions or rewards here!!
        self.q = dict()             # self.q[] is where we hold the actions and rewards, the state is the key from self.states[] (so typically an int!)
        self.iteration = 0
        self.prev_state, self.prev_action, self.prev_reward = None, None, 0
        self.net_reward = 0
        self.epsilon = 0.8          # If we know the state, go with it 80% of the time. Pick a random action 20% of the time
        self.alpha, self.gamma = 0.5, 0.5
        self.initial_q_value = 3    # Set deliberately high compared to rewards in order to force the agent to try different actions until all have been tried

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.prev_state, self.prev_action, self.prev_reward = None, None, 0
        self.net_reward = 0

    def set_initial_q(self):
        return self.initial_q_value

    def new_state(self, state):
        print "new_state(): state = {}".format(state)
        new_state_id = len(self.states)
        self.states[new_state_id] = state
        self.q[new_state_id] = dict({None:self.set_initial_q(),
                                      'forward':self.set_initial_q(),
                                      'left':self.set_initial_q(),
                                      'right':self.set_initial_q()})
        return new_state_id

    def find_state_id(self, state):
        state_id = None
        if [state in self.states.values()] == [True]:
            for i, s in self.states.iteritems():
                if state == s:
                    state_id = i
        return state_id

    def max_over_a(self, state_):
        state_id_ = self.find_state_id(state_)   # This is s'
        if state_id_ is not None:
            qMax = max(self.q[state_id_].values())
        else:
            qMax = self.initial_q_value
        print "max_over_a(): s'({}) = {}".format(state_, qMax)
        return qMax

    def update_qvalue(self, state, action, reward, state_):
        state_id = self.find_state_id(state)
        if state_id is not None:
            # Based on this formula https://discourse-cdn.global.ssl.fastly.net/udacity/uploads/default/original/3X/1/1/117c62ab1154fa84b606b8db21f992804203bae6.png
            self.q[state_id][action] = self.q[state_id][action] + self.alpha * (reward + self.gamma * self.max_over_a(state_) - self.q[state_id][action])
        else:
            state_id = self.new_state(state)
            self.q[state_id][action] = reward
        print "update_qvalue(): Updated the qvalues based on state {} id {}".format(state, state_id)

    def choose_action(self, state):
        best_actions = self.possible_actions
        state_id = self.find_state_id(state)
        if state_id is not None and random.random() < self.epsilon:    # We know the state but sometimes we pick a random action
            print "update_action(): Known state or explore for q-values {}".format(self.q[state_id])
            best_actions = [action for action, q in self.q[state_id].iteritems() if q == max(self.q[state_id].values())]
            print "possible actions {} based on q-value {} for state {}".format(best_actions, self.q[state_id], state)
        action = random.choice(best_actions)
        print "choose_action(): Action to take {}".format(action)
        return action

    #
    # 1) Sense the environment (see what changes occur naturally in the environment) - store it as state_0
    # 2) Take an action/reward - store as action_0 & reward_0
    #
    # In the next iteration
    # 1) Sense environment (see what changes occur naturally and from an action) - store as state_1
    # 2) Update the Q-table using state_0, action_0, reward_0, state_1
    # 3) Take an action - get a reward
    # 4) Repeat
    #
    # So for iterations > 0 we need to see if the state exists, and if it does update the action/rewards accordingly
    # and if it doesn't then create a new state with default action/rewards
    # So I need to pass in a state (s), an action taken (a) and a reward (r) for taking that action
    # But I am currently in a new state (s'), so really what is passed into update_qvalue() is the previous s, a, r
    #
    def update(self, t):
        print "***********************************\nupdate(): Iteration {}".format(self.iteration)
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = (("lights", inputs['light']),
                      ('oncoming', inputs['oncoming']),
                      ('right', inputs['right']),
                      ('left', inputs['left']),
                      ("waypoint", self.next_waypoint))
        if self.iteration == 0:
            self.new_state(self.state)
        else:
            # Now we know the reward for a specific action, we can update the previous state with what we know
            # Previous state is the state s in which we took action a to get reward r and put us in current state s'
            self.update_qvalue(self.prev_state, self.prev_action, self.prev_reward, self.state)

        # Select action according to your policy
        action = self.choose_action(self.state)

        # Execute action and get reward
        reward = self.env.act(self, action)
        self.net_reward = self.net_reward + reward

        # Save this state, etc. for the next iteration as prev_state
        self.iteration = self.iteration + 1  # Let's keep a count
        self.prev_state = self.state
        self.prev_action = action
        self.prev_reward = reward

        # TODO: Learn policy based on state, action, reward

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}, net_reward = {}"\
            .format(deadline, inputs, action, reward, self.net_reward)  # [debug]


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
