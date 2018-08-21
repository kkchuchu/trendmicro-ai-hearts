from bot import TrendBotBase

class A3C(TrendBotBase):

    def declare_action(self, player_obs, table_obs):
        action = [self.idx]

        score, (hand,), (income,) = player_obs
        n_round, start_pos, cur_pos, exchanged, hearts_occur, n_game,\
                board, (first_draw,), bank = table_obs
        
        hand_card = [c for c in hand if c[0] != -1 or c[1] != -1]
        board_card = [c for c in board]

        if not exchanged and n_game % 4 != 0:
            # 3 cards
            draws = random.sample(hand, 3)
        else:
            # 1 card
            if self.idx == start_pos and n_round == 0:
                draws = [array([0, 3])]
            else:
                for card in hand_card:
                    if card[1] == first_draw[1]:
                        draws = [card]
                        break
                else:
                    for card in hand_card:
                        (rank, suit) = (card[0], card[1])
                        if n_round == 0:
                            if suit != 1 and not all(card == (10, 0)):
                                draws = [card]
                                break
                        elif not hearts_occur and suit != 1:
                            draws = [card]
                            break
                    else:
                        draws = [random.choice(hand_card)]

            draws += [array([-1, -1]), array([-1, -1])]

        action.append(tuple(draws))
        return tuple(action)
