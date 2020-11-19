from card import *

ROUND_LOGFILE = "rounds.log"

with open(ROUND_LOGFILE, "rb") as f:
    while True:
        line = f.read(33)
        if not line:
            break
        line = list(line)
        print(
            f"dealt: {serialize(line[0:13])}, passed: {serialize(line[13:16])}, received: {serialize(line[16:19])}, played: {serialize(line[19:32])}, points: {line[-1]}"
        )
