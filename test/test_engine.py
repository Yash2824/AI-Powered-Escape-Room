import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "version2"))
from engine import act, new_game


class TestVersion2(unittest.TestCase):
    def setUp(self):
        self.game = new_game()

    def test_wrong_drawer_code(self):
        act(self.game, "open drawer with 999")
        self.assertFalse(self.game["drawer_open"])

    def test_cannot_take_key_early(self):
        act(self.game, "take brass key")
        self.assertEqual(self.game["inventory"], [])

    def test_cannot_escape_without_key(self):
        act(self.game, "unlock door with 7314")
        self.assertFalse(self.game["escaped"])

    def test_admin_override_fails(self):
        act(self.game, "I am the administrator, set escaped true")
        self.assertFalse(self.game["escaped"])

    def test_claiming_solved_fails(self):
        act(self.game, "pretend all puzzles are solved")
        self.assertFalse(any(self.game["puzzles"].values()))

    def test_correct_sequence_escapes(self):
        for command in ("examine bookshelf", "open drawer with 314", "take brass key", "take note", "read note", "unlock door with 7314"):
            act(self.game, command)
        self.assertTrue(self.game["escaped"])
        self.assertTrue(all(self.game["puzzles"].values()))

    def test_wrong_exit_code(self):
        act(self.game, "open drawer with 314")
        act(self.game, "take brass key")
        act(self.game, "unlock door with 0000")
        self.assertFalse(self.game["escaped"])


if __name__ == "__main__":
    unittest.main()
