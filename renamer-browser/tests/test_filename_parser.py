"""Tests for filename parsing and pattern recognition."""
import sys
import unittest
from pathlib import Path

# Ensure the renamer-browser package root is on sys.path for direct test execution
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.filename_parser import FilenameParser


class FilenameParserTestCase(unittest.TestCase):
    """Test the FilenameParser class."""

    def setUp(self):
        """Set up test fixtures."""
        self.known_tags = ['comics', 'nancy', 'sluggo', 'popart', 'warhol']
        self.parser = FilenameParser(known_tags=self.known_tags)

    def test_parse_filename_basic(self):
        """Test basic filename parsing with underscores."""
        result = self.parser.parse_filename('image_001_test.jpg')
        self.assertEqual(result, ['image', '001', 'test'])

    def test_parse_filename_with_hyphens(self):
        """Test parsing filenames with hyphens."""
        result = self.parser.parse_filename('image-001-test.png')
        self.assertEqual(result, ['image', '001', 'test'])

    def test_parse_filename_with_spaces(self):
        """Test parsing filenames with spaces."""
        result = self.parser.parse_filename('image 001 test.jpg')
        self.assertEqual(result, ['image', '001', 'test'])

    def test_parse_filename_mixed_separators(self):
        """Test parsing filenames with mixed separators."""
        result = self.parser.parse_filename('image_001-test final.jpg')
        self.assertEqual(result, ['image', '001', 'test', 'final'])

    def test_parse_filename_no_extension(self):
        """Test parsing filenames without extension."""
        result = self.parser.parse_filename('image_001_test')
        self.assertEqual(result, ['image', '001', 'test'])

    def test_identify_tags_in_filename(self):
        """Test identifying known tags in filename."""
        result = self.parser.identify_tags_in_filename('comics_nancy_001.jpg')
        self.assertEqual(set(result), {'comics', 'nancy'})

    def test_identify_tags_case_insensitive(self):
        """Test tag identification is case-insensitive."""
        result = self.parser.identify_tags_in_filename('Comics_NANCY_001.jpg')
        self.assertEqual(set(result), {'comics', 'nancy'})

    def test_identify_tags_no_matches(self):
        """Test with filename containing no known tags."""
        result = self.parser.identify_tags_in_filename('random_image_001.jpg')
        self.assertEqual(result, [])

    def test_find_common_patterns_empty_list(self):
        """Test pattern finding with empty list."""
        result = self.parser.find_common_patterns([])
        self.assertEqual(result['suggested_tags'], [])
        self.assertEqual(result['suggested_prefix'], '')
        self.assertEqual(result['suggested_suffix'], '')

    def test_find_common_patterns_same_tags(self):
        """Test finding common tags across multiple files."""
        filenames = [
            'comics_nancy_001.jpg',
            'comics_nancy_002.jpg',
            'comics_nancy_003.jpg',
        ]
        result = self.parser.find_common_patterns(filenames)
        self.assertEqual(set(result['suggested_tags']), {'comics', 'nancy'})

    def test_find_common_patterns_common_prefix(self):
        """Test detecting common prefix."""
        filenames = [
            'myproject_comics_001.jpg',
            'myproject_nancy_002.jpg',
            'myproject_sluggo_003.jpg',
        ]
        result = self.parser.find_common_patterns(filenames)
        self.assertEqual(result['suggested_prefix'], 'myproject')

    def test_find_common_patterns_common_suffix(self):
        """Test detecting common suffix."""
        filenames = [
            'comics_final_version.jpg',
            'nancy_final_version.jpg',
            'sluggo_final_version.jpg',
        ]
        result = self.parser.find_common_patterns(filenames)
        self.assertEqual(result['suggested_suffix'], 'final_version')

    def test_find_common_patterns_prefix_suffix_and_tags(self):
        """Test detecting prefix, suffix, and tags together."""
        filenames = [
            'project_comics_nancy_final.jpg',
            'project_popart_warhol_final.jpg',
            'project_comics_sluggo_final.jpg',
        ]
        result = self.parser.find_common_patterns(filenames)
        self.assertEqual(result['suggested_prefix'], 'project')
        self.assertEqual(result['suggested_suffix'], 'final')
        # Comics appears in 2 out of 3, which is >= 50%
        self.assertIn('comics', result['suggested_tags'])

    def test_find_common_patterns_no_common_elements(self):
        """Test with files that have no common patterns."""
        filenames = [
            'abc_xyz_123.jpg',
            'def_uvw_456.jpg',
            'ghi_rst_789.jpg',
        ]
        result = self.parser.find_common_patterns(filenames)
        self.assertEqual(result['suggested_prefix'], '')
        self.assertEqual(result['suggested_suffix'], '')
        self.assertEqual(result['suggested_tags'], [])

    def test_tag_frequency_counting(self):
        """Test that tag frequency is correctly counted."""
        filenames = [
            'comics_nancy_001.jpg',
            'comics_sluggo_002.jpg',
            'popart_warhol_003.jpg',
            'comics_004.jpg',
        ]
        result = self.parser.find_common_patterns(filenames)
        self.assertEqual(result['tag_frequency']['comics'], 3)
        self.assertEqual(result['tag_frequency']['nancy'], 1)
        self.assertEqual(result['tag_frequency']['sluggo'], 1)
        self.assertEqual(result['tag_frequency']['popart'], 1)
        self.assertEqual(result['tag_frequency']['warhol'], 1)

    def test_suggested_tags_threshold(self):
        """Test that only tags appearing in >50% of files are suggested."""
        filenames = [
            'comics_nancy_001.jpg',
            'comics_sluggo_002.jpg',
            'popart_003.jpg',
            'warhol_004.jpg',
        ]
        result = self.parser.find_common_patterns(filenames)
        # Comics appears in 2/4 = 50%, should be included
        self.assertIn('comics', result['suggested_tags'])
        # Others appear in only 1/4 = 25%, should not be included
        self.assertNotIn('nancy', result['suggested_tags'])
        self.assertNotIn('sluggo', result['suggested_tags'])
        self.assertNotIn('popart', result['suggested_tags'])
        self.assertNotIn('warhol', result['suggested_tags'])

    def test_analyze_filenames(self):
        """Test the high-level analyze_filenames method."""
        filenames = [
            'project_comics_nancy_final.jpg',
            'project_comics_sluggo_final.jpg',
            'project_comics_warhol_final.jpg',
        ]
        result = self.parser.analyze_filenames(filenames)
        
        # Check structure
        self.assertIn('suggested_tags', result)
        self.assertIn('suggested_prefix', result)
        self.assertIn('suggested_suffix', result)
        self.assertIn('analysis', result)
        
        # Check content
        self.assertEqual(result['suggested_prefix'], 'project')
        self.assertEqual(result['suggested_suffix'], 'final')
        self.assertIn('comics', result['suggested_tags'])
        
        # Check analysis metadata
        self.assertEqual(result['analysis']['total_files'], 3)
        self.assertTrue(result['analysis']['has_common_prefix'])
        self.assertTrue(result['analysis']['has_common_suffix'])

    def test_long_filenames(self):
        """Test with very long filenames."""
        long_filename = '_'.join(['part' + str(i) for i in range(50)]) + '.jpg'
        result = self.parser.parse_filename(long_filename)
        self.assertEqual(len(result), 50)

    def test_unusual_characters(self):
        """Test with filenames containing unusual characters."""
        # Should still parse by separators
        result = self.parser.parse_filename('file@123_test#456.jpg')
        self.assertIn('file@123', result)
        self.assertIn('test#456', result)

    def test_unicode_filenames(self):
        """Test with unicode characters in filenames."""
        result = self.parser.parse_filename('文件_001_test.jpg')
        self.assertIn('文件', result)
        self.assertIn('001', result)
        self.assertIn('test', result)

    def test_single_file_analysis(self):
        """Test analyzing a single file."""
        result = self.parser.find_common_patterns(['comics_nancy_001.jpg'])
        # All tags should be suggested for a single file
        self.assertEqual(set(result['suggested_tags']), {'comics', 'nancy'})

    def test_parser_without_known_tags(self):
        """Test parser initialized without known tags."""
        parser = FilenameParser(known_tags=None)
        result = parser.identify_tags_in_filename('comics_nancy_001.jpg')
        self.assertEqual(result, [])

    def test_empty_known_tags(self):
        """Test parser with empty known tags list."""
        parser = FilenameParser(known_tags=[])
        result = parser.identify_tags_in_filename('comics_nancy_001.jpg')
        self.assertEqual(result, [])


class FilenameParserEdgeCasesTestCase(unittest.TestCase):
    """Test edge cases and error conditions."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = FilenameParser(known_tags=['tag1', 'tag2', 'tag3'])

    def test_empty_filename(self):
        """Test with empty filename."""
        result = self.parser.parse_filename('')
        self.assertEqual(result, [])

    def test_filename_only_extension(self):
        """Test with filename that is only an extension."""
        # Path('.jpg').stem returns '.jpg' since it's treated as a filename, not extension
        result = self.parser.parse_filename('.jpg')
        self.assertEqual(result, ['.jpg'])

    def test_filename_only_separators(self):
        """Test with filename containing only separators."""
        result = self.parser.parse_filename('___---   .jpg')
        self.assertEqual(result, [])

    def test_duplicate_tags_in_filename(self):
        """Test handling of duplicate tags in a single filename."""
        result = self.parser.identify_tags_in_filename('tag1_tag1_tag2.jpg')
        # Should include duplicates as found
        self.assertEqual(result, ['tag1', 'tag1', 'tag2'])

    def test_very_large_file_list(self):
        """Test with a large number of files."""
        filenames = [f'file_{i:04d}.jpg' for i in range(1000)]
        result = self.parser.find_common_patterns(filenames)
        self.assertEqual(result['suggested_prefix'], 'file')

    def test_mixed_case_tags_in_different_files(self):
        """Test that mixed case tags are normalized correctly."""
        filenames = [
            'TAG1_test_001.jpg',
            'tag1_test_002.jpg',
            'Tag1_test_003.jpg',
        ]
        result = self.parser.find_common_patterns(filenames)
        # Should all be recognized as the same tag
        self.assertIn('tag1', result['suggested_tags'])
        self.assertEqual(result['tag_frequency']['tag1'], 3)


if __name__ == '__main__':
    unittest.main()
