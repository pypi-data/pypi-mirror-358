import pytest
from mq_randomizer.quote_types import MQuote

class TestMQuote:
    @pytest.fixture
    def sample_quote(self):
        quote_dict = {
            "characters": ["Neo"],
            "lines": [{"Neo": "Remember... there is no spoon."}]
        }
        return MQuote(quote_dict, "The Matrix", "movie", 1999)

    def test_initialization(self, sample_quote):
        assert sample_quote["media_title"] == "The Matrix"
        assert sample_quote["media_type"] == "movie"
        assert sample_quote["year"] == 1999
        assert sample_quote["characters"] == ["Neo"]
        assert sample_quote["lines"] == [{"Neo": "Remember... there is no spoon."}]

    def test_characters_property(self, sample_quote):
        assert sample_quote.characters == ["Neo"]

    def test_lines_property(self, sample_quote):
        assert sample_quote.lines == [{"Neo": "Remember... there is no spoon."}]

    def test_str_representation(self, sample_quote):
        expected = "Neo: Remember... there is no spoon."
        assert str(sample_quote) == expected

    def test_unattributed_line(self):
        quote_dict = {
            "characters": ["Unattributed"],
            "lines": [{"__none__": "This is a line without attribution."}]
        }
        quote = MQuote(quote_dict, "Test Movie", "movie", 2023)
        assert str(quote) == "This is a line without attribution."
