"""NATO Phonetic Alphabet CLI package."""

__version__ = "0.1.0"
__author__ = "trtmn"
__email__ = "trtmn@trtmn.io"

from .core import NATO_PHONETIC_ALPHABET, lookup_letter, spell_word

__all__ = [
    "NATO_PHONETIC_ALPHABET",
    "lookup_letter",
    "spell_word",
]
