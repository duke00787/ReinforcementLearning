from flappyb.environment import Environment
from numpy.random import choice



class Agent:

    def __init__(self):
        self.total_reward = 0

    def step(self, env):
        current_obs = env.get_observation_space()                 # emtpy for now
        actions = env.get_actions()                         # spacebar push
        draw = choice(actions, 1, p=(0.25, 0.75))
        obs, reward, is_done, _ = env.step(draw)
        self.total_reward += reward


env = Environment(True)
env.run_human_game()

# agent = Agent()
# env = Environment()
#
# # while True:
# while not env.is_done:
#     agent.step(env)
#
# print("Total reward = {}".format(agent.total_reward))
