import gym
import sys

sys.path.append('../lib/HeartsEnv')
from hearts.single import SingleEnv as HeartsEnv
from bot import GymBotBase


def main():
    bot = GymBotBase(HeartsEnv.PLAYER)
    env = HeartsEnv()
    obs = env.reset()
    mode = 'human'
    done = False

    while not done:
        env.render(mode)

        n_round, start_pos, cur_pos, exchanged, hearts_occur, n_game,\
                board, first_draw, bank = obs[1]
        player_obs = obs[0]

        action = bot.declare_action(player_obs, obs[1], env)
        obs, rew, done, _ = env.step(action)

    env.render(mode)


if __name__ == '__main__':
    main()
