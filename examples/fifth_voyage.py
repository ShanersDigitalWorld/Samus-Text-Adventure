import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from game_content.scenarios.fifth_voyage import build

game = build()
print(game.start("Control Deck"))
game.run()
