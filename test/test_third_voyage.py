import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from game_content.scenarios.third_voyage import build


class TestThirdVoyage(unittest.TestCase):
    def setUp(self):
        self.game = build()
        self.game.start("Synthesis Deck")

    def test_start_room(self):
        self.assertEqual(self.game.current.name, "Synthesis Deck")

    def test_move_west(self):
        out = self.game.do("go west")
        self.assertEqual(self.game.current.name, "Coolant Exchange")
        self.assertIn("Coolant", out)

    def test_move_east(self):
        out = self.game.do("go east")
        self.assertEqual(self.game.current.name, "Plasma Manifold")
        self.assertIn("Plasma", out)

    def test_blocked_north(self):
        out = self.game.do("go north")
        self.assertEqual(self.game.current.name, "Synthesis Deck")
        self.assertIn("sealed", out)

    def test_cyrus_initial_dialogue(self):
        out = self.game.do("talk to cyrus")
        self.assertIn("Alpha dial reads 1", out)
        self.assertIn("Beta dial reads 1", out)
        self.assertIn("Gamma dial reads 3", out)

    def test_dial_cycle(self):
        out = self.game.do("use alpha dial")
        self.assertIn("clicks to 2", out)
        self.assertEqual(self.game.flags["alpha"], 2)

    def test_dial_wrap(self):
        out = self.game.do("go east")
        out = self.game.do("use gamma dial")
        self.assertIn("clicks to 1", out)
        self.assertEqual(self.game.flags["gamma"], 1)

    def test_cyrus_after_alpha_fixed(self):
        self.game.do("use alpha dial")
        out = self.game.do("talk to cyrus")
        self.assertNotIn("Alpha dial reads", out)
        self.assertIn("Beta dial reads 1", out)

    def test_full_calibration(self):
        self.game.do("use alpha dial")
        self.game.do("go west")
        self.game.do("use beta dial")
        self.game.do("use beta dial")
        self.game.do("go east")
        self.game.do("go east")
        self.game.do("use gamma dial")
        self.assertTrue(self.game.flags.get("yield"))
        self.assertEqual(self.game.current.name, "Plasma Manifold")

    def test_calibration_unblocks_north(self):
        self.game.do("use alpha dial")
        self.game.do("go west")
        self.game.do("use beta dial")
        self.game.do("use beta dial")
        self.game.do("go east")
        self.game.do("go east")
        self.game.do("use gamma dial")
        self.game.do("go west")
        out = self.game.do("go north")
        self.assertEqual(self.game.current.name, "Yield Core Chamber")
        self.assertIn("Yield Core", out)

    def test_win_path(self):
        self.game.do("use alpha dial")
        self.game.do("go west")
        self.game.do("use beta dial")
        self.game.do("use beta dial")
        self.game.do("go east")
        self.game.do("go east")
        self.game.do("use gamma dial")
        self.game.do("go west")
        self.game.do("go north")
        out = self.game.do("use synthesis core")
        self.assertTrue(self.game.won)
        self.assertTrue(self.game.over)
        self.assertIn("complete", out)

    def test_core_too_early(self):
        self.game.do("use alpha dial")
        self.game.do("go west")
        self.game.do("use beta dial")
        self.game.do("use beta dial")
        self.game.do("go east")
        self.game.do("go east")
        self.game.do("use gamma dial")
        self.game.do("go west")
        self.game.flags["yield"] = False
        self.game.do("go north")
        out = self.game.do("use synthesis core")
        self.assertFalse(self.game.won)
        self.assertIn("too low", out)

    def test_plaque_beta(self):
        self.game.do("go west")
        out = self.game.do("look efficiency plaque")
        self.assertIn("level 3", out)

    def test_plaque_gamma(self):
        self.game.do("go east")
        out = self.game.do("look resonance plaque")
        self.assertIn("level 1", out)

    def test_manual(self):
        out = self.game.do("look deck manual")
        self.assertIn("level 2", out)

    def test_cyrus_optimal_dialogue(self):
        self.game.do("use alpha dial")
        self.game.do("go west")
        self.game.do("use beta dial")
        self.game.do("use beta dial")
        self.game.do("go east")
        self.game.do("go east")
        self.game.do("use gamma dial")
        self.game.do("go west")
        out = self.game.do("talk to cyrus")
        self.assertIn("optimal", out)

    def test_unknown_command(self):
        out = self.game.do("dance")
        self.assertIn("do not understand", out)

    def test_talk_unknown_character(self):
        self.assertIn("no one", self.game.do("talk to spock").lower())


if __name__ == "__main__":
    unittest.main()
