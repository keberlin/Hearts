from card import *

class Distribution():
    def __init__(self):
        self.distribution = [None for i in range(CARDS_IN_DECK)]

    def __getitem__(self,index):
        return self.distribution[index]

    def __setitem__(self,index,value):
        self.distribution[index] = value

    def player_cards(self, p, suit=None):
        cards = list(filter(lambda x: x is not None, [i if l == p else None for i, l in enumerate(self.distribution)]))
        if suit is not None:
            cards = list(filter(lambda x: in_suit(x, suit), cards))
        return cards
