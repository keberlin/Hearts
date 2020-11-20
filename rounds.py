from card import *

ROUND_LOGFILE = "rounds.log"

with open(ROUND_LOGFILE, "rb") as f:
    while True:
        line = f.read(33)
        if not line:
            break
        line = list(line)
        cards_dealt = line[0:13]
        cards_passed = line[13:16]
        cards_received = line[16:19]
        cards_played = line[19:32]
        points_game = line[32]
        print(
            f"dealt: {serialize(cards_dealt)}, passed: {serialize(cards_passed)}, received: {serialize(cards_received)}, played: {serialize(cards_played)}, points: {points_game}"
        )
        cards = set(cards_dealt)
        cards_passed = set(filter(lambda x: x < 52, cards_passed))
        if cards_passed:
            cards -= cards_passed
        cards_received = set(filter(lambda x: x < 52, cards_received))
        if cards_received:
            cards |= cards_received
        cards_played = set(cards_played)
        if cards != cards_played:
            print("Bad!!")
