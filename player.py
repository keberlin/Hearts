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

    def play_turn(
        self,
        turn,
        lead_suit,
        cards_in_turn,
        hand,
        playable,
        points_round,
        points_game,
        turns_played,
        cards_remaining,
        cards_dealt,
        direction,
        cards_passed,
        cards_received,
    ):
        pass

    def played_hand(self, cards_in_turn, mine, points_round):
        pass

    def played_game(self, points_game, hands_played):
        pass
