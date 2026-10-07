import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from game_content.scenarios.sixth_voyage import build


def collect_all(game):
    game.do("go west")
    game.do("take logic plate")
    game.do("take ferrite coil")
    game.do("go east")
    game.do("go east")
    game.do("take resonant crystal")
    game.do("go west")


class TestSixthVoyage(unittest.TestCase):
    def setUp(self):
        self.game = build()
        self.game.start("Foundry Floor")

    def test_start_room(self):
        self.assertEqual(self.game.current.name, "Foundry Floor")

    def test_move_west(self):
        out = self.game.do("go west")
        self.assertEqual(self.game.current.name, "Component Vault West")
        self.assertIn("logic plate", out)

    def test_move_east(self):
        out = self.game.do("go east")
        self.assertEqual(self.game.current.name, "Component Vault East")
        self.assertIn("resonant crystal", out)

    def test_blocked_north(self):
        out = self.game.do("go north")
        self.assertEqual(self.game.current.name, "Foundry Floor")
        self.assertIn("sealed", out)

    def test_take_components(self):
        self.game.do("go west")
        self.game.do("take logic plate")
        self.game.do("take ferrite coil")
        self.assertEqual(len(self.game.inventory), 2)

    def test_catalog_partial(self):
        self.game.do("go west")
        self.game.do("take logic plate")
        self.game.do("go east")
        out = self.game.do("use catalog")
        self.assertIn("Missing:", out)
        self.assertIn("resonant crystal", out)
        self.assertFalse(self.game.flags.get("indexed"))

    def test_catalog_lists_indexed(self):
        self.game.do("go west")
        self.game.do("take ferrite coil")
        self.game.do("take logic plate")
        self.game.do("go east")
        out = self.game.do("use catalog")
        self.assertIn("logic plate at index 1", out)
        self.assertIn("ferrite coil at index 3", out)

    def test_rig_idle(self):
        out = self.game.do("use test rig")
        self.assertIn("idle", out)

    def test_rig_with_component(self):
        self.game.do("go west")
        self.game.do("take logic plate")
        self.game.do("go east")
        out = self.game.do("use test rig")
        self.assertIn("resonates at index 1", out)

    def test_felix_initial(self):
        out = self.game.do("talk to felix")
        self.assertIn("Missing:", out)
        self.assertIn("Experiment freely", out)

    def test_full_index(self):
        collect_all(self.game)
        out = self.game.do("use catalog")
        self.assertIn("Catalog complete", out)
        self.assertTrue(self.game.flags.get("indexed"))
        out = self.game.do("go north")
        self.assertEqual(self.game.current.name, "Fabrication Lab")

    def test_felix_after_index(self):
        collect_all(self.game)
        self.game.do("use catalog")
        out = self.game.do("talk to felix")
        self.assertIn("Build the prototype", out)

    def test_manual(self):
        out = self.game.do("look foundry manual")
        self.assertIn("index 2", out)

    def test_win_path(self):
        collect_all(self.game)
        self.game.do("use catalog")
        self.game.do("go north")
        out = self.game.do("use fabricator")
        self.assertTrue(self.game.won)
        self.assertTrue(self.game.over)
        self.assertIn("Sixth Voyage: complete", out)

    def test_unknown_command(self):
        out = self.game.do("dance")
        self.assertIn("do not understand", out)

    def test_talk_unknown_character(self):
        self.assertIn("no one", self.game.do("talk to spock").lower())


if __name__ == "__main__":
    unittest.main()
