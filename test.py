from card import *

print(f"{serializedb(DECK)}")

cards = [card("S", "Q"), card("D", "2"), card("H", "5"), card("C", "X")]
print(f"{serializepr(cards)}")
