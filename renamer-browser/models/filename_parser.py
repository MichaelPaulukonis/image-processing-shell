"""Filename parsing utilities for tag detection and pattern recognition."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class FilenameParser:
    """Parse image filenames to detect tags, prefixes, and suffixes."""

    # Common separators used in filenames
    SEPARATORS = r'[_\-\s]+'
    
    def __init__(self, known_tags: Optional[List[str]] = None):
        """
        Initialize the filename parser.
        
        Args:
            known_tags: List of known tags to match against filenames
        """
        self.known_tags = set(known_tags or [])
        # Create case-insensitive lookup
        self._tag_lookup = {tag.lower(): tag for tag in self.known_tags}
    
    def parse_filename(self, filename: str) -> List[str]:
        """
        Parse a filename into its component parts.
        
        Args:
            filename: The filename to parse (with or without extension)
            
        Returns:
            List of parts split by common separators
        """
        # Strip extension
        name_without_ext = Path(filename).stem
        
        # Split by common separators
        parts = re.split(self.SEPARATORS, name_without_ext)
        
        # Filter out empty parts
        return [part for part in parts if part]
    
    def identify_tags_in_filename(self, filename: str) -> List[str]:
        """
        Identify which parts of a filename match known tags.
        
        Args:
            filename: The filename to analyze
            
        Returns:
            List of matched tags in their canonical form
        """
        parts = self.parse_filename(filename)
        matched_tags = []
        
        for part in parts:
            # Case-insensitive lookup
            canonical_tag = self._tag_lookup.get(part.lower())
            if canonical_tag:
                matched_tags.append(canonical_tag)
        
        return matched_tags
    
    def find_common_patterns(
        self, 
        filenames: List[str]
    ) -> Dict[str, object]:
        """
        Analyze multiple filenames to find common patterns.
        
        Args:
            filenames: List of filenames to analyze
            
        Returns:
            Dictionary containing:
            - common_tags: Tags that appear in multiple files
            - common_prefix: Common prefix across files (if any)
            - common_suffix: Common suffix across files (if any)
            - tag_frequency: How often each tag appears
            - suggested_tags: Tags that should be pre-selected
            - suggested_prefix: Prefix that should be pre-filled
            - suggested_suffix: Suffix that should be pre-filled
        """
        if not filenames:
            return {
                'common_tags': [],
                'common_prefix': '',
                'common_suffix': '',
                'tag_frequency': {},
                'suggested_tags': [],
                'suggested_prefix': '',
                'suggested_suffix': '',
            }
        
        # Parse all filenames
        all_parts = [self.parse_filename(fn) for fn in filenames]
        
        # Find tags in each filename
        all_tags = [self.identify_tags_in_filename(fn) for fn in filenames]
        
        # Count tag frequency
        tag_counter = Counter()
        for tags in all_tags:
            tag_counter.update(tags)
        
        # Tags that appear in more than half the files are suggested
        threshold = len(filenames) / 2
        suggested_tags = [
            tag for tag, count in tag_counter.items() 
            if count >= threshold
        ]
        
        # Find common prefix (parts at the beginning that match across all files)
        common_prefix_parts = self._find_common_prefix(all_parts)
        
        # Find common suffix (parts at the end that match across all files)
        common_suffix_parts = self._find_common_suffix(all_parts)
        
        # Filter out parts that are tags from prefix/suffix
        common_prefix_filtered = [
            part for part in common_prefix_parts 
            if part.lower() not in self._tag_lookup
        ]
        common_suffix_filtered = [
            part for part in common_suffix_parts 
            if part.lower() not in self._tag_lookup
        ]
        
        # Join prefix/suffix with underscores
        suggested_prefix = '_'.join(common_prefix_filtered) if common_prefix_filtered else ''
        suggested_suffix = '_'.join(common_suffix_filtered) if common_suffix_filtered else ''
        
        return {
            'common_tags': list(tag_counter.keys()),
            'common_prefix': suggested_prefix,
            'common_suffix': suggested_suffix,
            'tag_frequency': dict(tag_counter),
            'suggested_tags': suggested_tags,
            'suggested_prefix': suggested_prefix,
            'suggested_suffix': suggested_suffix,
        }
    
    def _find_common_prefix(self, all_parts: List[List[str]]) -> List[str]:
        """
        Find common prefix parts across all filename part lists.
        
        Args:
            all_parts: List of parsed filename parts
            
        Returns:
            List of common prefix parts
        """
        if not all_parts:
            return []
        
        # Start with the first filename's parts
        common = []
        min_length = min(len(parts) for parts in all_parts)
        
        for i in range(min_length):
            # Get the part at position i from all filenames
            parts_at_i = [parts[i].lower() for parts in all_parts]
            
            # If all are the same, it's part of common prefix
            if len(set(parts_at_i)) == 1:
                common.append(all_parts[0][i])
            else:
                # Stop at first difference
                break
        
        return common
    
    def _find_common_suffix(self, all_parts: List[List[str]]) -> List[str]:
        """
        Find common suffix parts across all filename part lists.
        
        Args:
            all_parts: List of parsed filename parts
            
        Returns:
            List of common suffix parts
        """
        if not all_parts:
            return []
        
        # Reverse all part lists to check from the end
        reversed_parts = [list(reversed(parts)) for parts in all_parts]
        
        # Use the prefix logic on reversed lists
        common_reversed = self._find_common_prefix(reversed_parts)
        
        # Reverse back to get suffix
        return list(reversed(common_reversed))
    
    def analyze_filenames(
        self, 
        filenames: List[str]
    ) -> Dict[str, object]:
        """
        High-level analysis of filenames for UI pre-population.
        
        This is the main method to call from the API endpoint.
        
        Args:
            filenames: List of filenames to analyze
            
        Returns:
            Dictionary with suggested tags, prefix, and suffix
        """
        patterns = self.find_common_patterns(filenames)
        
        return {
            'suggested_tags': patterns['suggested_tags'],
            'suggested_prefix': patterns['suggested_prefix'],
            'suggested_suffix': patterns['suggested_suffix'],
            'tag_frequency': patterns['tag_frequency'],
            'analysis': {
                'total_files': len(filenames),
                'unique_tags_found': len(patterns['common_tags']),
                'has_common_prefix': bool(patterns['common_prefix']),
                'has_common_suffix': bool(patterns['common_suffix']),
            }
        }
