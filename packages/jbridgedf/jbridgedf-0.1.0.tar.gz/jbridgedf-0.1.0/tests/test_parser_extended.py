from jbridgedf.parser import APIDataParser
import pytest
import pandas as pd


class MockResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json


def test_validate_nested_dict():
    parser = APIDataParser()
    data = {"payload": {"series": {"x": 10, "y": 20}}}
    mock = MockResponse(data)
    result = parser._validate_json(
        mock, is_list=False, cols=["x", "y"], data_key="payload"
    )
    assert isinstance(result, list)
    assert result[0]["x"] == 10


def test_parse_json_to_df_with_freq():
    parser = APIDataParser()
    data = [
        {"date": "2023-01-01", "value": 10},
        {"date": "2023-02-01", "value": 20},
        {"date": "2023-03-01", "value": 30}
    ]
    df = parser._parse_json_to_df(
        json_data=data,
        is_list=True,
        cols=["date", "value"],
        frequency="auto",
        col_freq="date",
        date_as_index=True
    )
    assert isinstance(df, pd.DataFrame)
    assert "value" in df.columns
    assert df.index.name == "date"


def test_parse_empty():
    parser = APIDataParser()
    df = parser._parse_json_to_df(json_data=[], is_list=True)
    assert df is None
