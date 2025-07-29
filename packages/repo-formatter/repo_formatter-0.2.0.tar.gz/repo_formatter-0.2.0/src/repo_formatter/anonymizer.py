import re
import os
from typing import Dict, Optional

class Anonymizer:
    def __init__(self, rules: Optional[Dict[str, str]] = None):
        self.rules = rules or {}
        self._compiled_patterns = self._compile_patterns()

    def _compile_patterns(self) -> Optional[re.Pattern]:
        if not self.rules:
            return None
        # Create a single regex pattern with case-insensitivity
        # Sort by length descending to match longer strings first (e.g., "OrgName" before "Org")
        sorted_keys = sorted(self.rules.keys(), key=len, reverse=True)
        pattern = '|'.join(re.escape(key) for key in sorted_keys)
        return re.compile(pattern, re.IGNORECASE)

    def _replacement_function(self, match: re.Match) -> str:
        """
        Performs replacement while preserving original case pattern.
        """
        matched_text = match.group(0)
        # Find which rule key matched (case-insensitively)
        replacement = ""
        for key, value in self.rules.items():
            if matched_text.lower() == key.lower():
                replacement = value
                break

        # Try to mimic the original case
        if matched_text.islower():
            return replacement.lower()
        elif matched_text.isupper():
            return replacement.upper()
        elif matched_text.istitle():
            # Handle multi-word replacements correctly for title case
            return ' '.join(word.capitalize() for word in replacement.split())
        else:
            # Default to the replacement value as is for mixed case or complex cases
            # More sophisticated case mapping could be added if needed
            return replacement

    def anonymize(self, text: str) -> str:
        """
        Anonymizes the given text based on the loaded rules.
        """
        if not self._compiled_patterns or not text:
            return text
        return self._compiled_patterns.sub(self._replacement_function, text)

    def anonymize_path(self, path_str: str) -> str:
        """
        Anonymizes components of a path string.
        """
        if not self.rules or not path_str:
            return path_str

        parts = path_str.split(re.escape(os.path.sep))
        anonymized_parts = [self.anonymize(part) for part in parts]
        return os.path.sep.join(anonymized_parts)
