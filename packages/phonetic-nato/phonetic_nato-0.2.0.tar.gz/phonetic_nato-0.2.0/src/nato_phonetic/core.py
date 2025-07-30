"""Core functionality for the NATO phonetic alphabet."""

from typing import Dict, List, Optional

# NATO Phonetic Alphabet mapping
NATO_PHONETIC_ALPHABET: Dict[str, str] = {
    "A": "Alpha",
    "B": "Bravo",
    "C": "Charlie",
    "D": "Delta",
    "E": "Echo",
    "F": "Foxtrot",
    "G": "Golf",
    "H": "Hotel",
    "I": "India",
    "J": "Juliet",
    "K": "Kilo",
    "L": "Lima",
    "M": "Mike",
    "N": "November",
    "O": "Oscar",
    "P": "Papa",
    "Q": "Quebec",
    "R": "Romeo",
    "S": "Sierra",
    "T": "Tango",
    "U": "Uniform",
    "V": "Victor",
    "W": "Whiskey",
    "X": "X-ray",
    "Y": "Yankee",
    "Z": "Zulu",
    "0": "Zero",
    "1": "One",
    "2": "Two",
    "3": "Three",
    "4": "Four",
    "5": "Five",
    "6": "Six",
    "7": "Seven",
    "8": "Eight",
    "9": "Nine",
}


def lookup_letter(letter: str) -> Optional[str]:
    """
    Look up the NATO phonetic equivalent for a single letter.

    Args:
        letter: The letter to look up (case-insensitive)

    Returns:
        The NATO phonetic equivalent or None if not found
    """
    return NATO_PHONETIC_ALPHABET.get(letter.upper())


def spell_word(word: str) -> List[tuple[str, str]]:
    """
    Spell out a word using the NATO phonetic alphabet.

    Args:
        word: The word to spell out

    Returns:
        List of tuples containing (letter, phonetic_equivalent)
    """
    result = []
    for char in word.upper():
        if char.isalnum():
            phonetic = NATO_PHONETIC_ALPHABET.get(char)
            if phonetic:
                result.append((char, phonetic))
            else:
                result.append((char, "Unknown"))
        elif char.isspace():
            result.append((char, "Space"))
        else:
            result.append((char, "Special"))
    return result


def get_full_alphabet() -> Dict[str, str]:
    """
    Get the complete NATO phonetic alphabet.

    Returns:
        Dictionary of all NATO phonetic alphabet mappings
    """
    return NATO_PHONETIC_ALPHABET.copy()


def is_valid_letter(letter: str) -> bool:
    """
    Check if a letter has a NATO phonetic equivalent.

    Args:
        letter: The letter to check

    Returns:
        True if the letter has a NATO phonetic equivalent
    """
    return letter.upper() in NATO_PHONETIC_ALPHABET
