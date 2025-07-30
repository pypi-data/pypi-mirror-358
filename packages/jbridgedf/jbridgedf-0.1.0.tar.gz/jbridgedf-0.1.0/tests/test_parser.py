from jbridgedf.parser import APIDataParser
import pytest


class MockResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json


def test_clean_metadata():
    parser = APIDataParser()
    data = [
        {"a": 1, "b": 2},
        {"a": 3, "b": 4, "c": 5},
        {"a": 6, "b": 7}
    ]
    result = parser.clean_metadata(data)
    assert result == [
        {"a": 1, "b": 2},
        {"a": 3, "b": 4},
        {"a": 6, "b": 7}
    ]


def test_validate_json_list():
    parser = APIDataParser()
    mock = MockResponse([{"x": 1}, {"x": 2}])
    result = parser._validate_json(mock, is_list=True)
    assert isinstance(result, list)
    assert len(result) == 2
