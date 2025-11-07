"""Flag detection for CTF challenges."""

import re
from typing import List


class FlagDetector:
    """Detects CTF flag patterns in text."""
    
    # Common CTF flag patterns (note: detection uses case-insensitive matching)
    DEFAULT_PATTERNS = [
        r'flag\{[^}]+\}',  # Matches flag{...}, FLAG{...}, Flag{...} etc.
        r'CTF\{[^}]+\}',   # Matches CTF{...}, ctf{...} etc.
        r'pwned\{[^}]+\}', # Matches pwned{...}, PWNED{...} etc.
        r'\b[a-f0-9]{32,}\b',  # Long hex strings (possible hashes)
    ]
    
    def __init__(self, custom_patterns: List[str] = None):
        """Initialize flag detector with patterns.
        
        Args:
            custom_patterns: Optional custom regex patterns to detect
        """
        self.patterns = custom_patterns if custom_patterns else self.DEFAULT_PATTERNS
    
    def detect(self, text: str) -> bool:
        """Check if text contains any flag patterns.
        
        Args:
            text: Text to search for flags
            
        Returns:
            True if a flag pattern is found, False otherwise
        """
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in self.patterns)
    
    def extract_flags(self, text: str) -> List[str]:
        """Extract all flag matches from text.
        
        Args:
            text: Text to search for flags
            
        Returns:
            List of unique matched flag strings
        """
        flags = []
        for pattern in self.patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            flags.extend(matches)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_flags = []
        for flag in flags:
            flag_lower = flag.lower()
            if flag_lower not in seen:
                seen.add(flag_lower)
                unique_flags.append(flag)
        
        return unique_flags

