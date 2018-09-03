import gym
import bots
import gym
import sys

sys.path.append('../lib/HeartsEnv')
from hearts.single import SingleEnv as HeartsEnv
from bot import GymConnector
from bots.pg.policy_gradient import Foo
import numpy as np

DISPLAY_REWARD_THRESHOLD = 400  # renders environment if total episode reward is greater then this threshold
RENDER = False  # rendering wastes time


def main():
    bot = GymConnector(3, Foo(52, output_graph=True, is_restore=True))
    env = HeartsEnv()
    mode = 'human'
    done = False

    for i_episode in range(3000):
        running_reward = None
        observation = env.reset()
        while True:
            n_round, _, _, exchanged, _, n_game, finish_expose, heart_exposed, board, (first_draw,), backup = observation[1]
            if n_round is 0 and n_game % 4 != 0:
                action = env.action_space.sample()
                observation_, reward, done, _ = env.step(action)
                observation = observation_
                continue
            t = bot.declare_action(observation, env.action_space.get_all_valid_actions())
            action = np.array([(t%13, int(t/13))])
            observation_, reward, done, _ = env.step(action)

            train_observation = bot.get_train_observation(observation, env.action_space.get_all_valid_actions())
            game_info = bot._gym2game_info(observation, env.action_space.get_all_valid_actions())
            if reward > 0:
                print("Shooting Moon: update rewards")
                for i, _ in enumerate(bot.ML.ep_rs):
                    bot.ML.ep_rs[i] = reward
            bot.ML.store_transition(train_observation, t, float(reward))


            if n_round % 13 is 0:
                vt = bot.ML.learn(i_episode)
                ep_rs_sum = sum(bot.ML.ep_rs)
                if running_reward is None:
                    running_reward = ep_rs_sum
                running_reward = running_reward * 0.99 + ep_rs_sum * 0.01
                print("episode:", i_episode, "  reward:", int(running_reward), "vt:", vt)

            if done:
                break

            observation = observation_

    env.render(mode)


if __name__ == '__main__':
    main()
