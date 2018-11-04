import pytest

import pandas as pd
import logging

from autofocus.util import discard_duplicate_rows


class TestDiscardDuplicateRows:

    def test_no_dupes(self):
        """
        Tests that passing in a dataframe with no duplicate rows does nothing.
        """
        expected_df = pd.DataFrame.from_dict({
            "lions": [1, 2, 3],
            "tigers": ["a", "b", "c"],
            "bears": [0., 1., 3.14]
        })
        test_df = expected_df.copy()
        with pytest.warns(None) as record:
            discard_duplicate_rows(test_df)
        assert len(record) == 0
        assert test_df.equals(expected_df)

    def test_with_dupe(self, caplog):
        """
        Tests passing in dataframe with duplicate rows for expected output and
        expected warning.
        """
        test_df = pd.DataFrame.from_dict({
            "lions": [1, 2, 1, 3, 2],
            "tigers": ["a", "b", "a", "c", "b"],
            "bears": [0., 1., 0., 3.14, 1.]
        })
        expected_df = pd.DataFrame.from_dict({
            "lions": [1, 2, 3],
            "tigers": ["a", "b", "c"],
            "bears": [0., 1., 3.14]
        })

        with caplog.at_level(logging.WARNING):
            discard_duplicate_rows(test_df)

            assert len(caplog.records) == 1
            assert caplog.records[0].levelname == "WARNING"

        test_df.reset_index(drop=True, inplace=True)
        assert test_df.equals(expected_df)
