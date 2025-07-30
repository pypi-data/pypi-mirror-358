from unittest.mock import patch
import os
import json
import pandas as pd
from tests.utils import fixtures_path

from hestia_earth.distribution.utils.MCMC_mv import (
    calculate_fit_2d, calculate_fit_mv, update_mv, update_all_mv, read_mv,
    find_likelihood_from_static_file
)
from hestia_earth.distribution.utils.cycle import (
    YIELD_COLUMN, FERTILISER_COLUMNS, PESTICIDE_COLUMN, IRRIGATION_COLUMN
)

class_path = 'hestia_earth.distribution.utils.MCMC_mv'


def fake_generate_likl_file(folder: str):
    def run(country_id, product_id, *args):
        likl_file = os.path.join(fixtures_path, folder, 'likelihood_files', f"{'_'.join([country_id, product_id])}.csv")
        return pd.read_csv(likl_file, na_values='-') if os.path.exists(likl_file) else pd.DataFrame()
    return run


def fake_download_lookup(folder: str):
    def run(country_id, product_id, *args):
        likl_file = os.path.join(fixtures_path, folder, 'likelihood_files', f"{'_'.join([country_id, product_id])}.csv")
        return pd.read_csv(likl_file, na_values='-') if os.path.exists(likl_file) else pd.DataFrame()
    return run


def fake_mv_folder(folder: str):
    def run(country_id, product_id, *args):
        return os.path.join(fixtures_path, folder, f'mv_samples_{country_id}_{product_id}')
    return run


@patch(f"{class_path}.generate_likl_file", side_effect=fake_generate_likl_file('utils'))
def test_calculate_fit_2d_yield_vs_n(*args):
    likelihood_a, *args = calculate_fit_2d([150, 3500], 'GADM-GBR', 'wheatGrain')
    likelihood_b, *args = calculate_fit_2d([150, 8500], 'GADM-GBR', 'wheatGrain')
    assert likelihood_a < 0.05
    assert likelihood_b > 0.75


@patch(f"{class_path}.generate_likl_file", side_effect=fake_generate_likl_file('utils'))
def test_calculate_fit_2d_yield_vs_p2o5(*args):
    likelihood_c, *args = calculate_fit_2d([80, 2500], 'GADM-GBR', 'wheatGrain',
                                           columns=[FERTILISER_COLUMNS[1], YIELD_COLUMN])
    likelihood_d, *args = calculate_fit_2d([5, 8500], 'GADM-GBR', 'wheatGrain',
                                           columns=[FERTILISER_COLUMNS[1], YIELD_COLUMN])
    assert likelihood_c < 0.05
    assert likelihood_d > 0.9


@patch(f"{class_path}.generate_likl_file", side_effect=fake_generate_likl_file('utils'))
def test_calculate_fit_2d_yield_vs_k2o(*args):
    likelihood_a, *args = calculate_fit_2d([80, 2500], 'GADM-CHN', 'wheatGrain',
                                           columns=[FERTILISER_COLUMNS[2], YIELD_COLUMN])
    likelihood_b, *args = calculate_fit_2d([20, 8500], 'GADM-GBR', 'wheatGrain',
                                           columns=[FERTILISER_COLUMNS[2], YIELD_COLUMN])
    assert likelihood_a is None
    assert likelihood_b > 0.75


@patch(f"{class_path}.generate_likl_file", side_effect=fake_generate_likl_file('utils'))
def test_calculate_fit_2d_yield_vs_pest(*args):
    likelihood_a, *args = calculate_fit_2d([10, 2500], 'GADM-GBR', 'wheatGrain',
                                           columns=[PESTICIDE_COLUMN, YIELD_COLUMN])
    likelihood_b, *args = calculate_fit_2d([0.5, 8500], 'GADM-GBR', 'wheatGrain',
                                           columns=[PESTICIDE_COLUMN, YIELD_COLUMN])
    assert likelihood_a < 0.05
    assert likelihood_b > 0.75


@patch(f"{class_path}.generate_likl_file", side_effect=fake_generate_likl_file('utils'))
def test_calculate_fit_2d_yield_vs_water(*args):
    likelihood_a, *args = calculate_fit_2d([10, 2500], 'GADM-GBR', 'wheatGrain',
                                           columns=[IRRIGATION_COLUMN, YIELD_COLUMN])
    likelihood_b, *args = calculate_fit_2d([0.1, 8500], 'GADM-GBR', 'wheatGrain',
                                           columns=[IRRIGATION_COLUMN, YIELD_COLUMN])
    assert likelihood_a < 0.05
    assert likelihood_b > 0.75


@patch(f"{class_path}.generate_likl_file", side_effect=fake_generate_likl_file('utils'))
def test_calculate_fit_2d_yield_vs_npk(*args):
    likelihood_a, *args = calculate_fit_mv([180, 50, 50, 1500], 'GADM-GBR', 'wheatGrain',
                                           columns=FERTILISER_COLUMNS[:3] + [YIELD_COLUMN])
    likelihood_b, *args = calculate_fit_mv([180, 20, 20, 8500], 'GADM-GBR', 'wheatGrain',
                                           columns=FERTILISER_COLUMNS[:3] + [YIELD_COLUMN])
    assert likelihood_a < 0.05
    assert likelihood_b > 0.75


@patch(f"{class_path}.generate_likl_file", side_effect=fake_generate_likl_file('utils'))
def test_calculate_fit_2d_return_z(*args):
    likelihood, Z = calculate_fit_2d([180, 8500], 'GADM-GBR', 'wheatGrain', return_z=True)
    assert likelihood > 0.05
    assert Z.shape == (100, 100)


@patch(f"{class_path}.generate_likl_file", side_effect=fake_generate_likl_file('utils'))
@patch(f"{class_path}._mv_filename", side_effect=fake_mv_folder('utils'))
@patch(f"{class_path}.write_to_storage")
@patch(f"{class_path}.file_exists", return_value=False)
def test_update_mv(*args):
    output_likl, sample_grid = update_mv('GADM-GBR', 'wheatGrain', sample_size=3)
    assert output_likl.shape == (3, 3, 3, 3)
    assert output_likl[0, 0, 0, 0] < 1


@patch(f"{class_path}.get_product_ids", return_value=['wheatGrain'])
@patch(f"{class_path}.update_mv")
def test_update_all_mv(mock_update_mv, *args):
    update_all_mv('GADM-GBR', sample_size=5)
    mock_update_mv.assert_called_once()


def fake_load_mv(filename: str):
    filepath = filename if 'mv_files' in filename else os.path.join('mv_files', filename)
    with open(os.path.join(fixtures_path, 'utils', filepath), 'r') as f:
        return f.read()


@patch(f"{class_path}.load_from_storage", side_effect=fake_load_mv)
def test_read_mv(*args):
    lk, grids = read_mv('mv_samples_size5.json')
    assert len(lk) == 5 and len(grids) == 5


def fake_read_mv_file(folder: str):
    def read_file(*args):
        with open(os.path.join(fixtures_path, folder, 'mv_files', 'mv_samples_size5.json'), 'r') as f:
            return json.load(f)
    return read_file


@patch(f"{class_path}.load_from_storage", side_effect=fake_load_mv)
@patch('hestia_earth.distribution.utils.priors.load_from_storage', side_effect=fake_read_mv_file('utils'))
def test_find_likelihood_from_static_file(*args):
    lk, loc = find_likelihood_from_static_file([200, 50, 50, 8500], 'GADM-GBR', 'wheatGrain')
    assert len(loc) == 4
