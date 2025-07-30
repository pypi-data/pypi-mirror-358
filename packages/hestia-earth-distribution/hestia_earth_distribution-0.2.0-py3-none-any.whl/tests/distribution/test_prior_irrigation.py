from unittest.mock import patch
import os
from tests.utils import fixtures_path, fake_read_prior_file
from hestia_earth.distribution.utils.priors import read_prior_stats

from hestia_earth.distribution.prior_irrigation import (
    generate_prior_irrigation_file, get_fao_irrigated, get_prior
)

class_path = 'hestia_earth.distribution.prior_irrigation'
fixtures_folder = os.path.join(fixtures_path, 'prior_irrigation')
country_ids = ['GADM-AFG', 'GADM-ALB', 'GADM-AUT', 'GADM-COL', 'GADM-GBR']


def test_get_fao_irrigated():
    val = get_fao_irrigated('GADM-AFG')
    assert len(val[0]) == 10


@patch('hestia_earth.distribution.utils.priors.get_country_ids', return_value=country_ids)
@patch('hestia_earth.distribution.utils.priors.load_from_storage', side_effect=fake_read_prior_file('prior_irrigation'))
@patch('hestia_earth.distribution.utils.priors.write_to_storage')
def test_generate_prior_irrigation_file(*args):
    result = generate_prior_irrigation_file(overwrite=True)
    expected = read_prior_stats(os.path.join(fixtures_folder, 'result.csv'))
    assert result.to_csv() == expected.to_csv()


@patch('hestia_earth.distribution.utils.priors.load_from_storage', side_effect=fake_read_prior_file('prior_irrigation'))
def test_get_prior(*args):
    mu, sd = get_prior('GADM-ALB')
    assert mu == 811.75689629
    assert sd == 715.48754505


@patch('hestia_earth.distribution.utils.priors.load_from_storage', side_effect=fake_read_prior_file('prior_irrigation'))
def test_get_prior_missing(*args):
    # data is not present
    mu, sd = get_prior('GADM-FRA')
    assert mu is None
    assert sd is None


@patch('hestia_earth.distribution.utils.priors.load_from_storage', side_effect=fake_read_prior_file('prior_irrigation'))
def test_get_prior_empty(*args):
    # data is not present
    mu, sd = get_prior('GADM-CHN')
    assert mu is None
    assert sd is None
