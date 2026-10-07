import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from game_content.scenarios.second_voyage import build


class TestSecondVoyage(unittest.TestCase):
    def setUp(self):
        self.game = build()
        self.game.start("Vault Antechamber")

    def test_start_room(self):
        self.assertEqual(self.game.current.name, "Vault Antechamber")

    def test_move_east(self):
        out = self.game.do("go east")
        self.assertEqual(self.game.current.name, "AND Gallery")
        self.assertIn("truth tables", out)

    def test_move_west(self):
        self.game.do("go west")
        self.assertEqual(self.game.current.name, "OR Gallery")

    def test_door_blocked(self):
        out = self.game.do("go north")
        self.assertEqual(self.game.current.name, "Vault Antechamber")
        self.assertIn("sealed", out)

    def test_levers_start_at_zero(self):
        for metal in ("brass", "silver", "copper"):
            self.assertEqual(self.game.flags.get("lever_" + metal, 0), 0)

    def test_lever_flips(self):
        out = self.game.do("use silver lever")
        self.assertIn("clicks to 1", out)
        self.assertEqual(self.game.flags.get("lever_silver"), 1)
        out = self.game.do("use silver lever")
        self.assertIn("clicks to 0", out)
        self.assertEqual(self.game.flags.get("lever_silver"), 0)

    def test_manual_text(self):
        out = self.game.do("look vault manual")
        self.assertIn("1 AND 0", out)
        self.assertIn("NOT 1", out)

    def test_and_plaque_text(self):
        self.game.do("go east")
        out = self.game.do("look and plaque")
        self.assertIn("both inputs", out)

    def test_or_plaque_text(self):
        self.game.do("go west")
        out = self.game.do("look or plaque")
        self.assertIn("any input", out)

    def test_blake_intro(self):
        out = self.game.do("talk to blake")
        self.assertIn("Silver is wrong", out)
        self.assertIn("1 OR 0", out)

    def test_blake_spots_wrong_brass(self):
        self.game.do("use brass lever")
        out = self.game.do("talk to blake")
        self.assertIn("Brass is wrong", out)
        self.assertIn("1 AND 0", out)

    def test_blake_all_correct(self):
        self.game.do("use silver lever")
        out = self.game.do("talk to blake")
        self.assertIn("holds true", out)
        self.assertIn("core door", out)

    def test_door_stays_sealed_when_wrong(self):
        out = self.game.do("use core door")
        self.assertIn("stays sealed", out)
        self.assertFalse(self.game.flags.get("door_open"))
        self.game.do("go north")
        self.assertEqual(self.game.current.name, "Vault Antechamber")

    def test_door_opens_when_true(self):
        self.game.do("use silver lever")
        out = self.game.do("use core door")
        self.assertIn("slides open", out)
        self.assertTrue(self.game.flags.get("door_open"))
        self.game.do("go north")
        self.assertEqual(self.game.current.name, "Binary Core")

    def test_blake_after_open(self):
        self.game.do("use silver lever")
        self.game.do("use core door")
        out = self.game.do("talk to blake")
        self.assertIn("core is open", out)

    def test_win_path(self):
        self.game.do("use silver lever")
        self.game.do("use core door")
        self.game.do("go north")
        out = self.game.do("use binary core")
        self.assertTrue(self.game.won)
        self.assertTrue(self.game.over)
        self.assertIn("Second Voyage: complete", out)

    def test_unknown_command(self):
        out = self.game.do("dance")
        self.assertIn("do not understand", out)

    def test_help(self):
        out = self.game.do("help")
        self.assertIn("take", out)


if __name__ == "__main__":
    unittest.main()
