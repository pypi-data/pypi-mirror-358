"""Tests for the core NATO phonetic alphabet functionality."""

import pytest

from nato_phonetic.core import (
    NATO_PHONETIC_ALPHABET,
    lookup_letter,
    spell_word,
    get_full_alphabet,
    is_valid_letter,
)


class TestNATOPhoneticAlphabet:
    """Test the NATO phonetic alphabet data."""

    def test_alphabet_contains_all_letters(self):
        """Test that the alphabet contains all 26 letters."""
        letters = [chr(i) for i in range(ord("A"), ord("Z") + 1)]
        for letter in letters:
            assert letter in NATO_PHONETIC_ALPHABET

    def test_alphabet_contains_numbers(self):
        """Test that the alphabet contains numbers 0-9."""
        numbers = [str(i) for i in range(10)]
        for number in numbers:
            assert number in NATO_PHONETIC_ALPHABET

    def test_alphabet_values_are_strings(self):
        """Test that all phonetic values are strings."""
        for value in NATO_PHONETIC_ALPHABET.values():
            assert isinstance(value, str)
            assert len(value) > 0


class TestLookupLetter:
    """Test the lookup_letter function."""

    def test_lookup_uppercase_letter(self):
        """Test looking up an uppercase letter."""
        result = lookup_letter("A")
        assert result == "Alpha"

    def test_lookup_lowercase_letter(self):
        """Test looking up a lowercase letter."""
        result = lookup_letter("a")
        assert result == "Alpha"

    def test_lookup_number(self):
        """Test looking up a number."""
        result = lookup_letter("5")
        assert result == "Five"

    def test_lookup_invalid_character(self):
        """Test looking up an invalid character."""
        result = lookup_letter("!")
        assert result is None

    def test_lookup_empty_string(self):
        """Test looking up an empty string."""
        result = lookup_letter("")
        assert result is None


class TestSpellWord:
    """Test the spell_word function."""

    def test_spell_simple_word(self):
        """Test spelling a simple word."""
        result = spell_word("HELLO")
        expected = [
            ("H", "Hotel"),
            ("E", "Echo"),
            ("L", "Lima"),
            ("L", "Lima"),
            ("O", "Oscar"),
        ]
        assert result == expected

    def test_spell_word_with_numbers(self):
        """Test spelling a word with numbers."""
        result = spell_word("ABC123")
        expected = [
            ("A", "Alpha"),
            ("B", "Bravo"),
            ("C", "Charlie"),
            ("1", "One"),
            ("2", "Two"),
            ("3", "Three"),
        ]
        assert result == expected

    def test_spell_word_with_spaces(self):
        """Test spelling a word with spaces."""
        result = spell_word("A B")
        expected = [
            ("A", "Alpha"),
            (" ", "Space"),
            ("B", "Bravo"),
        ]
        assert result == expected

    def test_spell_word_with_special_characters(self):
        """Test spelling a word with special characters."""
        result = spell_word("A!B")
        expected = [
            ("A", "Alpha"),
            ("!", "Special"),
            ("B", "Bravo"),
        ]
        assert result == expected

    def test_spell_empty_word(self):
        """Test spelling an empty word."""
        result = spell_word("")
        assert result == []

    def test_spell_mixed_case(self):
        """Test spelling a word with mixed case."""
        result = spell_word("HeLLo")
        expected = [
            ("H", "Hotel"),
            ("E", "Echo"),
            ("L", "Lima"),
            ("L", "Lima"),
            ("O", "Oscar"),
        ]
        assert result == expected


class TestGetFullAlphabet:
    """Test the get_full_alphabet function."""

    def test_get_full_alphabet(self):
        """Test getting the full alphabet."""
        result = get_full_alphabet()
        assert isinstance(result, dict)
        assert result == NATO_PHONETIC_ALPHABET
        assert result is not NATO_PHONETIC_ALPHABET  # Should be a copy


class TestIsValidLetter:
    """Test the is_valid_letter function."""

    def test_valid_uppercase_letter(self):
        """Test a valid uppercase letter."""
        assert is_valid_letter("A") is True

    def test_valid_lowercase_letter(self):
        """Test a valid lowercase letter."""
        assert is_valid_letter("a") is True

    def test_valid_number(self):
        """Test a valid number."""
        assert is_valid_letter("5") is True

    def test_invalid_character(self):
        """Test an invalid character."""
        assert is_valid_letter("!") is False

    def test_empty_string(self):
        """Test an empty string."""
        assert is_valid_letter("") is False
