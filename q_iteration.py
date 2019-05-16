# Value iteration is not Q-Learning
import collections
from tensorboardX import SummaryWriter
from flappyb.environment import Environment
import random
import numpy as np

GAMMA = 0.9
TEST_EPISODES = 5
RANDOM_STEPS = 5000

NAME = 'flappy-bird-q-iteration-env-5000-steps-randomized-,2-,8-updated-env-fps-1'
MODEL_PATH = 'models/{}.pt'.format(NAME)
WRITE = True
DRAW = False
DRAW_TRAINING = False


# Contains tabled and functions
class Agent:
    def __init__(self):
        self.env = Environment(DRAW_TRAINING)
        self.state = self.env.reset()

        self.rewards = collections.defaultdict(float)
        self.transits = collections.defaultdict(collections.Counter)
        self.values = collections.defaultdict(float)

    # Gather random experience and update tables
    # we can only learn on full episodes (unlike cross entropy)
    def play_n_random_steps(self, count):
        rand = random.uniform(0.2,0.8)
        for _ in range(count):
            if _ % 1000 == 0:
                rand = random.uniform(0.2,0.8)
            # action = self.env.get_action_random()  # perform random action
            action = np.random.choice((0,1), 1, p=(rand, 1-rand))   # i should do this in env
            action = action.item(0)                
            new_state, reward, is_done, _ = self.env.step(action)

            self.rewards[(self.state, action, new_state)] = reward  # reward = s, a, news
            self.transits[(self.state, action)][new_state] += 1  # remembers occurence
            self.state = self.env.reset() if is_done else new_state
 
    # Uses calculated actions, searches the best for a given state and chooses it
    # Chooses actoin with best q value
    def select_action(self, state):
        best_action, best_value = None, None
        for action in range(self.env.get_action_size()):
            action_value = self.values[(state, action)]
            if best_value is None or best_value < action_value:
                best_value = action_value
                best_action = action
        return best_action

    # Not written into the table, cuz no randomness. Takes another env ?
    def play_episode(self, env):
        total_reward = 0.0
        state = env.reset()
        while True:
            action = self.select_action(state)
            new_state, reward, is_done, _ = env.step(action)
            self.rewards[(state, action, new_state)] = reward
            self.transits[(state, action)][new_state] += 1
            total_reward += reward
            if is_done:
                break
            state = new_state
        return total_reward

    # Loop over every state, calculate actions, update table with max value
    def q_iteration(self):
        for state in range(self.env.get_observation_size()):
            for action in range(self.env.get_action_size()):
                action_value = 0.0
                target_counts = self.transits[(state, action)]
                total = sum(target_counts.values())
                for tgt_state, count in target_counts.items():
                    reward = self.rewards[(state, action, tgt_state)]
                    best_action = self.select_action(tgt_state)
                    # action_value += (count / total) * (reward + GAMMA * self.values[(tgt_state, best_action)])
                    action_value += (count / total) * (reward + self.values[(tgt_state, best_action)])
                    self.values[(state, action)] = action_value

# Training loop whoop whoop
if __name__ == "__main__":
    test_env = Environment(DRAW)
    agent = Agent()
    writer = None
    if WRITE:
        writer = SummaryWriter(comment=NAME)

    iter_no = 0
    best_reward = 0.0
    while True:
        iter_no += 1
        print('#{}'.format(iter_no))
        agent.play_n_random_steps(RANDOM_STEPS)  # create data for table
        agent.q_iteration()  # use table to choose best action

        reward = 0.0
        for _ in range(TEST_EPISODES):
            reward += agent.play_episode(test_env)  # evaluate agent
        reward /= TEST_EPISODES
        print('Current reward: {}'.format(reward))
        if WRITE:
            writer.add_scalar('reward', reward, iter_no)
        if reward > best_reward:
            print('Best reward update %.3f -> %.3f' % (best_reward, reward))
            best_reward = reward
        if iter_no > 10000:
            print('Job Done!')
            break
    if WRITE:
        writer.close()
