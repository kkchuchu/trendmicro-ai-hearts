import gym
import bots
import gym
import sys

sys.path.append('../lib/HeartsEnv')
from hearts.single import SingleEnv as HeartsEnv
from bot import GymConnector
from bots.pg.policy_gradient import PolicyGradient
import numpy as np

DISPLAY_REWARD_THRESHOLD = 400  # renders environment if total episode reward is greater then this threshold
RENDER = False  # rendering wastes time


def main():
    bot = GymConnector(3, PolicyGradient(52))
    env = HeartsEnv()
    mode = 'human'
    done = False
    last_n_game = 1

    for i_episode in range(3000):
        running_reward = None
        observation = env.reset()
        while True:
            n_round, _, _, exchanged, _, n_game, *_ = observation[1]
            if n_round is 0 and n_game % 4 != 0:
                action = env.action_space.sample()
                observation_, reward, done, _ = env.step(action)
                observation = observation_
                continue
            t = bot.declare_action(observation, env.action_space.get_all_valid_actions())
            action = np.array([(t%13, int(t/13))])
            observation_, reward, done, _ = env.step(action)

            train_observation = bot.get_train_observation(observation, env.action_space.get_all_valid_actions())
            bot.ML.store_transition(train_observation, t, float(reward))

            if done:
                ep_rs_sum = sum(bot.ML.ep_rs)
                if running_reward is None:
                    running_reward = ep_rs_sum
                running_reward = running_reward * 0.99 + ep_rs_sum * 0.01
                if running_reward > DISPLAY_REWARD_THRESHOLD: RENDER = True     # rendering
                print("episode:", i_episode, "  reward:", int(running_reward))

                vt = bot.ML.learn()
                last_n_game = n_game
                break

            observation = observation_

    env.render(mode)


if __name__ == '__main__':
    main()
