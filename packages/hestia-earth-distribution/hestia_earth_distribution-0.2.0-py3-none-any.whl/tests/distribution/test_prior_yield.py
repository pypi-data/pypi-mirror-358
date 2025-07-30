from unittest.mock import patch
import os
import numpy as np
from tests.utils import fixtures_path, fake_read_prior_file
from hestia_earth.distribution.utils.priors import read_prior_stats
from hestia_earth.distribution.utils import get_country_ids

from hestia_earth.distribution.prior_yield import (
    generate_prior_yield_file, get_prior
)

class_path = 'hestia_earth.distribution.prior_yield'
fixtures_folder = os.path.join(fixtures_path, 'prior_yield')
country_ids = ['GADM-AFG', 'GADM-ALB', 'GADM-BDI', 'GADM-COL', 'GADM-GBR']


@patch('hestia_earth.distribution.utils.priors.get_country_ids', return_value=country_ids)
@patch('hestia_earth.distribution.utils.priors.load_from_storage', side_effect=fake_read_prior_file('prior_yield'))
@patch('hestia_earth.distribution.utils.priors.write_to_storage')
@patch(f"{class_path}.get_product_ids", return_value=['bananaFruit', 'wheatGrain'])
def test_generate_prior_yield_file(*args):
    result = generate_prior_yield_file(overwrite=True)
    expected = read_prior_stats(os.path.join(fixtures_folder, 'result.csv'))
    assert result.to_csv() == expected.to_csv()


@patch('hestia_earth.distribution.utils.priors.load_from_storage', side_effect=fake_read_prior_file('prior_yield'))
def test_get_prior(*args):
    mu, sd = get_prior('GADM-AFG', 'wheatGrain')
    assert mu == 206.3769989
    assert sd == 153.50022963


@patch('hestia_earth.distribution.utils.priors.load_from_storage', side_effect=fake_read_prior_file('prior_yield'))
def test_get_prior_missing(*args):
    # data is empty
    mu, sd = get_prior('GADM-AFG', 'genericCropSeed')
    assert mu is None
    assert sd is None

    # data is not present
    mu, sd = get_prior('GADM-FRA', 'wheatGrain')
    assert mu is None
    assert sd is None


def prior_density_at_zero(product_id: str):
    country_ids = get_country_ids()
    lower_bounds = []
    for i, country_id in enumerate(country_ids):
        mu, sigma = get_prior(country_id, product_id)
        if mu is not None:
            lower_bounds.append(max(mu - sigma, 0))
    return int((len(lower_bounds) - np.count_nonzero(lower_bounds))/len(lower_bounds) * 100)


@patch('hestia_earth.distribution.utils.priors.get_country_ids', return_value=country_ids)
@patch('hestia_earth.distribution.utils.priors.load_from_storage', side_effect=fake_read_prior_file('prior_yield'))
def test_prior_density_at_zero(*args):
    assert prior_density_at_zero('wheatGrain') == 20
