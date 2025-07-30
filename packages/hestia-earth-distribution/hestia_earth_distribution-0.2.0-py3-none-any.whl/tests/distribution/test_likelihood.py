from unittest.mock import patch
import os
import pandas as pd
import json
from tests.utils import fixtures_path, round_df_column

from hestia_earth.distribution.likelihood import generate_likl_file, _read_likl_file

class_path = 'hestia_earth.distribution.likelihood'
fixtures_folder = os.path.join(fixtures_path, 'likelihood')

with open(os.path.join(fixtures_folder, 'cycles.jsonld'), 'r') as f:
    cycles = json.load(f)


def read_likl_file(*args):
    with open(os.path.join(fixtures_folder, 'result.csv'), 'rb') as f:
        return f.read()


@patch(f"{class_path}.load_from_storage", side_effect=read_likl_file)
def test_read_likl_file(*args):
    result = _read_likl_file('file')
    assert len(result) > 0


@patch(f"{class_path}.find_cycles", return_value=cycles)
@patch(f"{class_path}.file_exists", return_value=False)
@patch(f"{class_path}.write_to_storage")
def test_generate_likl_file(*args):
    country_id = 'GADM-GBR'
    product_id = 'wheatGrain'

    expected = pd.read_csv(os.path.join(fixtures_folder, 'result.csv'), index_col=0)
    result = generate_likl_file(country_id, product_id)
    for col in result.columns:
        if 'completeness' not in col:
            round_df_column(result, col)
    assert result.to_csv() == expected.to_csv()
