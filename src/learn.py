import gym
import bots
import gym
import sys

sys.path.append('../lib/HeartsEnv')
from hearts.single import SingleEnv as HeartsEnv
from bot import GymConnector
from bots.pg.policy_gradient import PolicyGradient

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
            if n_round is 0 and n_game is 1:
                action = env.action_space.sample()
                observation_, reward, done, _ = env.step(action)
                observation = observation_
                continue
            action = bot.declare_action(observation)
            from pdb import set_trace; set_trace()
            observation_, reward, done, _ = env.step(action)
            bot.ML.store_transition(observation, action, reward)

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
