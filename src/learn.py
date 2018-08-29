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
        observation = env.reset()
        while True:
            n_round, _, _, exchanged, _, n_game, *_ = observation[1]
            if n_round is 0 and n_game % 4 != 0:
                action = env.action_space.sample()
                observation_, reward, done, _ = env.step(action)
                observation = observation_
                continue
            prob_weights = bot.declare_action(observation, env.action_space.get_all_valid_actions())
            game_info = bot._gym2game_info(observation, env.action_space.get_all_valid_actions())


            t = []
            for s in ['S', 'H', 'D', 'C']:
                t = t + game_info.players[game_info.me].valid_action.df.loc[:, s].tolist()
            for i, v in enumerate(t):
                if v == 0:
                    prob_weights[0][i] = 0
            prob_weights = prob_weights / prob_weights.sum()


            t = np.random.choice(range(prob_weights.shape[1]), p=prob_weights.ravel())  # select action w.r.t the actions prob
            action = np.array([(t%13, int(t/13))])
            observation_, reward, done, _ = env.step(action)

            train_observation = bot.get_train_observation(observation, env.action_space.get_all_valid_actions())
            bot.ML.store_transition(train_observation, prob_weights, float(reward))

            if done:
                ep_rs_sum = sum(bot.ML.ep_rs)

                if 'running_reward' not in globals():
                    print("Idk what this mean")
                    running_reward = ep_rs_sum
                else:
                    running_reward = running_reward * 0.99 + ep_rs_sum * 0.01
                if running_reward > DISPLAY_REWARD_THRESHOLD: RENDER = True     # rendering
                print("episode:", i_episode, "  reward:", int(running_reward))

                vt = bot.ML.learn()

                if i_episode == 0:
                    plt.plot(vt)    # plot the episode vt
                    plt.xlabel('episode steps')
                    plt.ylabel('normalized state-action value')
                    plt.show()
                last_n_game = n_game
                break

            observation = observation_

    env.render(mode)


if __name__ == '__main__':
    main()
