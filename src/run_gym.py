import gym
import sys

sys.path.append('../lib/HeartsEnv')
from hearts.hearts import HeartsEnv
from hearts.bot import BotBase, RandomBot


def main():
    bots = [RandomBot(i) for i in range(4)]
    env = HeartsEnv(render_delay=0.1)
    obs = env.reset()
    mode = 'human'
    done = False

    while not done:
        env.render(mode)

        n_round, start_pos, cur_pos, exchanged, hearts_occur, n_game,\
                board, first_draw, bank = obs[1]

        player_obs = tuple([obs[0][i]] for i in range(cur_pos*3, cur_pos*3+3))
        action = bots[cur_pos].declare_action(player_obs, obs[1])
        obs, rew, done, _ = env.step(action)

    env.render(self.mode)
    pass


if __name__ == '__main__':
    main()
