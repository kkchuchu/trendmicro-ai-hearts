import gym
import sys

sys.path.append('../lib/HeartsEnv')
from hearts.single import SingleEnv as HeartsEnv
from bot import BaseBot
from rule_bot import GameInfo
from card import INT_TO_RANK

class AlbertBot(BaseBot):
    def declare_action(self, info):
        return info.candidate[0]


def main():
    env = HeartsEnv()
    obs = env.reset()
    mode = 'human'
    done = False
    last_first_draw = None
    albert = AlbertBot()

    while not done:
        env.render(mode)

        info = GameInfo()

        opponent = obs[0][0]
        my_score = obs[0][1]
        my_hand = obs[0][2]
        my_income = obs[0][3]

        table = obs[1]
        info.table.n_round, _, _, info.table.exchanged, _, info.table.n_game, \
        info.table.finish_expose, info.table.heart_exposed, board, (first_draw,), backup = table

        for idx, card in enumerate(backup):
            info.table.opening_card.add_card(convert_array_to_card(card))
            if last_first_draw and card[1] != last_first_draw[1]:
                info.players[idx].no_suit.add(INT_TO_SUIT[card[1]])

        last_first_draw = first_draw

        first_draw = convert_array_to_card(first_draw)
        info.table.first_draw = first_draw

        for idx, card in enumerate(board):
            card = convert_array_to_card(card)
            info.table.append(card)
            if first_draw and first_draw[1] != card[1]:
                info.players[idx].no_suit.add(card[1])


        action = albert.declare_action(info)
        obs, rew, done, _ = env.step(action)
        
        last_n_game = n_game

    env.render(mode)


if __name__ == '__main__':
    main()
