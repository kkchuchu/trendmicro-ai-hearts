import gym
import bots
import gym
import sys

sys.path.append('../lib/HeartsEnv')
from hearts.single import SingleEnv as HeartsEnv
from bots.pg.policy_gradient import MyPolicyBot

DISPLAY_REWARD_THRESHOLD = 400  # renders environment if total episode reward is greater then this threshold
RENDER = False  # rendering wastes time


def main():
    bot = MyPolicyBot(3)
    env = HeartsEnv()
    mode = 'human'
    done = False
    last_n_game = 1

    for i_episode in range(3000):
        observation = env.reset()
        while True:
            n_round, _, _, _, _, n_game, *_ = observation[1]
            if n_game > last_n_game:
                bot.reset()
            action = bot.choose_action(observation)
            observation_, reward, done, _ = env.step(action)
            bot.store_transition(observation, action, reward)

            if done:
                ep_rs_sum = sum(bot.Model.ep_rs)

                if 'running_reward' not in globals():
                    print("Idk what this mean")
                    running_reward = ep_rs_sum
                else:
                    running_reward = running_reward * 0.99 + ep_rs_sum * 0.01
                if running_reward > DISPLAY_REWARD_THRESHOLD: RENDER = True     # rendering
                print("episode:", i_episode, "  reward:", int(running_reward))

                vt = bot.Model.learn()

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
