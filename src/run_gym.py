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
    last_n_game = 1

    while not done:
        env.render(mode)
        player_obs = obs[0]
        n_round, _, _, _, _, n_game, *_ = obs[1]
        if n_game > last_n_game:
            from pdb import set_trace; set_trace()
            bot.reset()

        action = bot.declare_action(player_obs, obs[1], env)
        obs, rew, done, _ = env.step(action)
        
        last_n_game = n_game

    env.render(mode)


if __name__ == '__main__':
    main()
