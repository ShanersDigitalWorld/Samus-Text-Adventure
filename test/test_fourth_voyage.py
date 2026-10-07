import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from game_content.scenarios.fourth_voyage import build


def route_to_link(game):
    game.do("go west")
    game.do("use alpha relay")
    game.do("use alpha relay")
    game.do("use alpha relay")
    game.do("go east")
    game.do("go east")
    game.do("use beta relay")
    game.do("use beta relay")
    game.do("use beta relay")
    game.do("use beta relay")
    game.do("go west")
    game.do("use transmitter")


class TestFourthVoyage(unittest.TestCase):
    def setUp(self):
        self.game = build()
        self.game.start("Network Hub")

    def test_start_room(self):
        self.assertEqual(self.game.current.name, "Network Hub")

    def test_move_west(self):
        out = self.game.do("go west")
        self.assertEqual(self.game.current.name, "Relay Alpha")
        self.assertIn("Alpha relay", out)

    def test_move_east(self):
        out = self.game.do("go east")
        self.assertEqual(self.game.current.name, "Relay Beta")
        self.assertIn("Beta relay", out)

    def test_blocked_north(self):
        out = self.game.do("go north")
        self.assertEqual(self.game.current.name, "Network Hub")
        self.assertIn("dark", out)

    def test_transmitter_dead_trace(self):
        out = self.game.do("use transmitter")
        self.assertIn("dead end", out)
        self.assertIn("dead air", out)

    def test_dante_before_trace(self):
        out = self.game.do("talk to dante")
        self.assertIn("Run the transmitter", out)

    def test_dante_dead_hint(self):
        self.game.do("use transmitter")
        out = self.game.do("talk to dante")
        self.assertIn("dead air", out)

    def test_relay_cycle(self):
        self.game.do("go west")
        self.game.do("use alpha relay")
        self.assertEqual(self.game.flags["route_alpha"], "hub")
        self.game.do("use alpha relay")
        self.game.do("use alpha relay")
        self.assertEqual(self.game.flags["route_alpha"], "beta")

    def test_loop_trace(self):
        self.game.do("go west")
        self.game.do("use alpha relay")
        self.game.do("use alpha relay")
        self.game.do("go east")
        out = self.game.do("use transmitter")
        self.assertIn("looping", out)

    def test_dante_loop_hint(self):
        self.game.do("go west")
        self.game.do("use alpha relay")
        self.game.do("use alpha relay")
        self.game.do("go east")
        self.game.do("use transmitter")
        out = self.game.do("talk to dante")
        self.assertIn("Break the cycle", out)

    def test_correct_routing_links(self):
        route_to_link(self.game)
        self.assertTrue(self.game.flags.get("linked"))
        out = self.game.do("go north")
        self.assertEqual(self.game.current.name, "Core Uplink")

    def test_dante_after_link(self):
        route_to_link(self.game)
        self.game.do("go south")
        out = self.game.do("talk to dante")
        self.assertIn("Full throughput", out)

    def test_win_path(self):
        route_to_link(self.game)
        self.game.do("go north")
        out = self.game.do("use uplink core")
        self.assertTrue(self.game.won)
        self.assertTrue(self.game.over)
        self.assertIn("Fourth Voyage: complete", out)

    def test_manual(self):
        out = self.game.do("look network manual")
        self.assertIn("Relay Alpha", out)

    def test_unknown_command(self):
        out = self.game.do("dance")
        self.assertIn("do not understand", out)

    def test_talk_unknown_character(self):
        self.assertIn("no one", self.game.do("talk to spock").lower())


if __name__ == "__main__":
    unittest.main()
