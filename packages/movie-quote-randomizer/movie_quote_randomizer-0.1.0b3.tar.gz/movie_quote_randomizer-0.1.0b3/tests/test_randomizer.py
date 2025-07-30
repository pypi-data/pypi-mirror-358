import pytest
import json
from unittest import mock
from mq_randomizer.randomizer import MQRandomizer
from mq_randomizer.quote_types import MQuote
from mq_randomizer import data
from mq_randomizer import pkg_resources  # Added import

class TestMQRandomizer:
    @pytest.fixture
    def mock_data(self):
        return {
            "meta": {
                "media_title": "Test Movie",
                "media_type": "movie",
                "year": 2023,
                "description": "A test movie"
            },
            "quotes": [
                {
                    "characters": ["Character1"],
                    "lines": [{"Character1": "Line 1"}]
                },
                {
                    "characters": ["Character2"],
                    "lines": [{"Character2": "Line 2"}]
                }
            ]
        }

    @pytest.fixture
    def randomizer(self, mock_data):
        with mock.patch.object(data, 'DEFAULT_QUOTES_JSON', 'test_quotes.json'):
            with mock.patch.object(pkg_resources, 'data_location_as_path', return_value='mock/path'):  # Fixed patch
                with mock.patch('builtins.open', mock.mock_open(read_data=json.dumps(mock_data))):
                    return MQRandomizer()

    def test_initialization(self, randomizer):
        assert randomizer._media_title == "Test Movie"
        assert randomizer._media_type == "movie"
        assert randomizer._year == 2023
        assert len(randomizer._quotes) == 2
        assert isinstance(randomizer._quotes[0], MQuote)

    def test_populate_quotes(self, randomizer, mock_data):
        quotes = randomizer._populate_quotes(mock_data["quotes"])
        assert len(quotes) == 2
        assert all(isinstance(q, MQuote) for q in quotes)

    def test_random_quote(self, randomizer):
        quote = randomizer.random_quote()
        assert isinstance(quote, MQuote)
        assert len(randomizer._quotes) > 0

    def test_random_quote_empty(self, randomizer):
        randomizer._quotes = []
        with pytest.raises(IndexError):
            randomizer.random_quote()
