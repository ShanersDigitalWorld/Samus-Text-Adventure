import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from game_content.scenarios.first_voyage import build


class TestFirstVoyage(unittest.TestCase):
    def setUp(self):
        self.game = build()
        self.game.start("Holodeck Grid")

    def test_start_room(self):
        self.assertEqual(self.game.current.name, "Holodeck Grid")

    def test_move_north(self):
        out = self.game.do("go north")
        self.assertEqual(self.game.current.name, "Ship Corridor")
        self.assertIn("Corridor", out)

    def test_short_direction(self):
        self.game.do("n")
        self.assertEqual(self.game.current.name, "Ship Corridor")

    def test_blocked_exit(self):
        self.game.do("go north")
        self.game.do("go east")
        out = self.game.do("go north")
        self.assertEqual(self.game.current.name, "Engineering")
        self.assertIn("no power", out)

    def test_take_power_cell(self):
        out = self.game.do("take power cell")
        self.assertIn("take the power cell", out)
        self.assertEqual(len(self.game.inventory), 1)

    def test_talk_to_adam_before_cell(self):
        self.game.do("go north")
        out = self.game.do("talk to adam")
        self.assertIn("power cell", out)

    def test_talk_to_adam_with_cell(self):
        self.game.do("take power cell")
        self.game.do("go north")
        out = self.game.do("talk adam")
        self.assertIn("Engineering", out)

    def test_tricorder_hint(self):
        self.game.do("go north")
        self.game.do("take tricorder")
        out = self.game.do("use tricorder")
        self.assertIn("Power failure", out)

    def test_restore_power(self):
        self.game.do("take power cell")
        self.game.do("go north")
        self.game.do("go east")
        out = self.game.do("use power cell")
        self.assertIn("warp core", out)
        self.assertTrue(self.game.flags.get("power"))

    def test_power_cell_wrong_room(self):
        self.game.do("take power cell")
        out = self.game.do("use power cell")
        self.assertIn("nothing to power", out)
        self.assertFalse(self.game.flags.get("power"))

    def test_win_path(self):
        self.game.do("take power cell")
        self.game.do("go north")
        self.game.do("go east")
        self.game.do("use power cell")
        self.game.do("go north")
        self.assertEqual(self.game.current.name, "Bridge")
        out = self.game.do("use helm console")
        self.assertTrue(self.game.won)
        self.assertTrue(self.game.over)
        self.assertIn("complete", out)

    def test_talk_unknown_character(self):
        self.game.do("go north")
        self.assertIn("no one", self.game.do("talk to spock").lower())

    def test_unknown_command(self):
        out = self.game.do("dance")
        self.assertIn("do not understand", out)

    def test_help(self):
        out = self.game.do("help")
        self.assertIn("take", out)

    def test_inventory(self):
        self.assertIn("nothing", self.game.do("inventory"))
        self.game.do("take power cell")
        self.assertIn("power cell", self.game.do("inventory"))


if __name__ == "__main__":
    unittest.main()
