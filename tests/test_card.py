from card import *


def test_serialize():
    cards = [card("S", "Q"), card("D", "2"), card("H", "5"), card("C", "X")]
    result = serialize(cards)
    assert result == ["QS", "2D", "5H", "XC"]


def test_deserialize():
    cards = ["2S", "KH", "4C", "JD"]
    result = deserialize(cards)
    assert result == [card("S", "2"), card("H", "K"), card("C", "4"), card("D", "J")]


def test_serializedb():
    cards = [card("S", "Q"), card("D", "2"), card("H", "5"), card("C", "X")]
    result = serializedb(cards)
    assert result == "QS2D5HXC"


def test_deserializedb():
    cards = "2SKH4CJD"
    result = deserializedb(cards)
    assert result == [card("S", "2"), card("H", "K"), card("C", "4"), card("D", "J")]


def test_serializepr():
    cards = [card("S", "Q"), card("D", "2"), card("H", "5"), card("C", "X")]
    result = serializepr(cards)
    assert result == "QS 2D 5H XC"
