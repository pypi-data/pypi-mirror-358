import os
import pandas as pd
from tests.utils import fixtures_path

from hestia_earth.distribution.utils.csv import drop_incomplete_cycles

class_path = 'hestia_earth.distribution.utils'
fixtures_folder = os.path.join(fixtures_path, 'utils')


def test_drop_incomplete_cycles():
    df = pd.read_csv(os.path.join(fixtures_folder, 'incomplete.csv'), index_col=None)
    result = drop_incomplete_cycles(df, 'completeness.fertiliser')
    assert len(result.index) == 2

    df = pd.read_csv(os.path.join(fixtures_folder, 'incomplete.csv'), index_col=None)
    result = drop_incomplete_cycles(df)
    assert len(result.index) == 1
