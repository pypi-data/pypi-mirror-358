from unittest.mock import patch
import os
from tests.utils import fixtures_path, fake_read_prior_file
from hestia_earth.distribution.utils.priors import read_prior_stats

from hestia_earth.distribution.prior_pest import (
    generate_prior_pest_file, get_fao_pest, get_prior
)

class_path = 'hestia_earth.distribution.prior_pest'
fixtures_folder = os.path.join(fixtures_path, 'prior_pest')
country_ids = ['GADM-AFG', 'GADM-ALB', 'GADM-AUT', 'GADM-COL', 'GADM-GBR']


def test_get_fao_pest():
    val = get_fao_pest('GADM-GBR')
    assert len(val[0]) == 4


@patch('hestia_earth.distribution.utils.priors.get_country_ids', return_value=country_ids)
@patch('hestia_earth.distribution.utils.priors.load_from_storage', side_effect=fake_read_prior_file('prior_pest'))
@patch('hestia_earth.distribution.utils.priors.write_to_storage')
def test_generate_prior_pest_file(*args):
    result = generate_prior_pest_file(overwrite=True)
    expected = read_prior_stats(os.path.join(fixtures_folder, 'result.csv'))
    assert result.to_csv() == expected.to_csv()


@patch('hestia_earth.distribution.utils.priors.load_from_storage', side_effect=fake_read_prior_file('prior_pest'))
def test_get_prior(*args):
    mu, sd = get_prior('GADM-GBR')
    assert mu == 2.73500001
    assert sd == 2.20443522


@patch('hestia_earth.distribution.utils.priors.load_from_storage', side_effect=fake_read_prior_file('prior_pest'))
def test_get_prior_missing(*args):
    # data is not present
    mu, sd = get_prior('region-eastern-africa')
    assert mu is None
    assert sd is None
