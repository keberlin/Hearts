class Player:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return "Player " + self.name

    def dealt(self, cards_dealt):
        pass

    def pass_cards(self, cards_dealt, direction):
        pass

    def receive_cards(self, cards_received):
        pass

    def play_turn(self, turn, lead_suit, cards, playable):
        pass

    def played_hand(self, cards, mine, points):
        pass

    def played_game(self, game_points):
        pass
