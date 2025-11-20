import json
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure the renamer-browser package root is on sys.path for direct test execution
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.tag_manager import TagManager


class TagManagerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.manager = TagManager(config_dir=self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_initializes_with_defaults_when_file_missing(self) -> None:
        tags = self.manager.get_all_tags()
        self.assertGreater(len(tags), 0)
        self.assertTrue(self.manager.tags_file.exists())

    def test_add_tag_persists_between_instances(self) -> None:
        success, _ = self.manager.add_tag("retro")
        self.assertTrue(success)
        fresh = TagManager(config_dir=self.temp_dir.name)
        self.assertIn("retro", fresh.get_all_tags())

    def test_duplicate_tag_rejected_case_insensitive(self) -> None:
        self.manager.add_tag("Gallery")
        success, message = self.manager.add_tag("gallery")
        self.assertFalse(success)
        self.assertEqual(message, "Tag already exists")

    def test_invalid_characters_rejected(self) -> None:
        success, message = self.manager.add_tag("bad tag!")
        self.assertFalse(success)
        self.assertIn("only contain", message)

    def test_metadata_timestamps_update_on_change(self) -> None:
        meta_before = self.manager.get_metadata()
        self.manager.add_tag("fresh")
        meta_after = self.manager.get_metadata()
        self.assertNotEqual(meta_before["last_modified"], meta_after["last_modified"])

    def test_remove_tag(self) -> None:
        baseline = self.manager.get_all_tags()[0]
        success, _ = self.manager.remove_tag(baseline)
        self.assertTrue(success)
        self.assertNotIn(baseline, self.manager.get_all_tags())

    def test_corrupted_file_resets_to_defaults(self) -> None:
        with open(self.manager.tags_file, "w", encoding="utf-8") as fh:
            fh.write("{{ not valid json")
        self.manager.reload()
        self.assertEqual(self.manager.get_all_tags(), TagManager.DEFAULT_TAGS)

    def test_reset_to_defaults_restores_original_list(self) -> None:
        self.manager.add_tag("conceptart")
        self.manager.reset_to_defaults()
        self.assertEqual(self.manager.get_all_tags(), TagManager.DEFAULT_TAGS)


if __name__ == "__main__":
    unittest.main()
