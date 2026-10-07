import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from game_content.scenarios.fifth_voyage import build


def streamline(game):
    game.do("go west")
    game.do("use beta scanner")
    game.do("use delta archive")
    game.do("go east")


class TestFifthVoyage(unittest.TestCase):
    def setUp(self):
        self.game = build()
        self.game.start("Control Deck")

    def test_start_room(self):
        self.assertEqual(self.game.current.name, "Control Deck")

    def test_move_west(self):
        out = self.game.do("go west")
        self.assertEqual(self.game.current.name, "Process Bay West")
        self.assertIn("scanner rigs", out)

    def test_move_east(self):
        out = self.game.do("go east")
        self.assertEqual(self.game.current.name, "Process Bay East")
        self.assertIn("gamma archive", out)

    def test_blocked_north(self):
        out = self.game.do("go north")
        self.assertEqual(self.game.current.name, "Control Deck")
        self.assertIn("sealed", out)

    def test_panel_initial(self):
        out = self.game.do("use status panel")
        self.assertIn("Load: 16", out)

    def test_elias_initial(self):
        out = self.game.do("talk to elias")
        self.assertIn("beta scanner", out)
        self.assertIn("delta archive", out)
        self.assertIn("Load at 16", out)

    def test_toggle_redundant(self):
        self.game.do("go west")
        out = self.game.do("use beta scanner")
        self.assertIn("Redundant load shed", out)
        self.assertFalse(self.game.flags.get("run_beta", True))

    def test_toggle_critical_fault(self):
        out = self.game.do("use alpha scanner")
        self.assertIn("Fault", out)
        self.assertIn("critical", out)

    def test_restart_clears_fault(self):
        self.game.do("use alpha scanner")
        out = self.game.do("use alpha scanner")
        self.assertIn("restart", out)
        out = self.game.do("use status panel")
        self.assertIn("No faults", out)

    def test_elias_fault_dialogue(self):
        self.game.do("go east")
        self.game.do("use gamma archive")
        self.game.do("go west")
        out = self.game.do("talk to elias")
        self.assertIn("critical and offline", out)

    def test_full_streamline(self):
        streamline(self.game)
        self.assertTrue(self.game.flags.get("streamlined"))
        out = self.game.do("go north")
        self.assertEqual(self.game.current.name, "Optimization Core")

    def test_critical_blocks_streamline(self):
        self.game.do("use alpha scanner")
        self.game.do("go west")
        self.game.do("use beta scanner")
        self.game.do("use delta archive")
        self.game.do("go east")
        self.assertFalse(self.game.flags.get("streamlined"))
        out = self.game.do("go north")
        self.assertEqual(self.game.current.name, "Control Deck")

    def test_elias_streamlined_dialogue(self):
        streamline(self.game)
        out = self.game.do("talk to elias")
        self.assertIn("Load optimal", out)

    def test_panel_after_streamline(self):
        streamline(self.game)
        out = self.game.do("use status panel")
        self.assertIn("Load: 9", out)

    def test_manual(self):
        out = self.game.do("look operations manual")
        self.assertIn("duplicates", out)

    def test_win_path(self):
        streamline(self.game)
        self.game.do("go north")
        out = self.game.do("use optimization core")
        self.assertTrue(self.game.won)
        self.assertTrue(self.game.over)
        self.assertIn("Fifth Voyage: complete", out)

    def test_unknown_command(self):
        out = self.game.do("dance")
        self.assertIn("do not understand", out)

    def test_talk_unknown_character(self):
        self.assertIn("no one", self.game.do("talk to spock").lower())


if __name__ == "__main__":
    unittest.main()
