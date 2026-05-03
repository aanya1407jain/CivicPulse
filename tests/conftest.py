import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_st():
    st = MagicMock()
    st.session_state = {}
    return st

@pytest.fixture
def sample_election_data():
    return {
        "election_name": "West Bengal Assembly Election 2026",
        "jurisdiction": "West Bengal",
        "counting_day": "2026-05-04",
        "poll_date": "2026-04-23",
    }
