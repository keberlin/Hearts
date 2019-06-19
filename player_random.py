from player import *

class RandomPlayer(Player):
    def __init__(self,id):
        super().__init__(id,'Random %d'%id)

    def pass_cards(self,direction):
        ret = []
        for i in range(3):
            ret.append(self._discard(random.choice(self.cards)))
        return ret

    def play_turn(self,round,lead_suit,cards,playable, hand_points, player_points):
        return self._discard(random.choice(playable))


