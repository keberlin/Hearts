import random
from card import *
from distribution import *

class Player():
    def __init__(self,id):
        self.id = id
        self.cards = []
        self.points = 0

    def deal(self,cards):
        #print(self.id,'deal:',serialize(cards))
        self.cards += cards
        #print(self.id,'cards:',serialize(self.cards))

    def pass_cards(self,direction):
        # TODO Determine best cards to pass
        ret = []
        for i in range(3):
            r = random.choice(self.cards)
            self.cards.remove(r)
            ret.append(r)
        #print(self.id,'pass_cards:',serialize(ret))
        #print(self.id,'cards:',serialize(self.cards))
        return ret

    def play_turn(self,round,playable):
        #print(self.id,'play_turn:',serialize(playable))
        # TODO Determine best card to play
        ret = random.choice(playable)
        self.cards.remove(ret)
        return ret

    def add_points(self,points):
        print(self.id,'add_points:',points)
        self.points += points
        print(self.id,'points:',self.points)

