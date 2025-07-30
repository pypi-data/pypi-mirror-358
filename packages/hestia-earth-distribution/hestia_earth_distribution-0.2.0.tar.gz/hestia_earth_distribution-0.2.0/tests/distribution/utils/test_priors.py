from unittest.mock import patch
import os
from tests.utils import fixtures_path, fake_read_prior_file

from hestia_earth.distribution.utils.priors import get_prior_by_country_by_product


def read_prior_file(*args):
    with open(os.path.join(fixtures_path, 'result.csv'), 'rb') as f:
        return f.read()


@patch('hestia_earth.distribution.utils.priors.load_from_storage', side_effect=fake_read_prior_file('prior_yield'))
def test_get_prior_by_country_by_product_yield(*args):
    country_id = 'GADM-GBR'
    product_id = 'wheatGrain'
    prior_filename = os.path.join(fixtures_path, 'prior_yield', 'result.csv')
    vals = get_prior_by_country_by_product(prior_filename, country_id, product_id)
    assert [round(v) for v in vals] == [819, 609, 10, 58]


@patch('hestia_earth.distribution.utils.priors.load_from_storage', side_effect=fake_read_prior_file('prior_fert'))
def test_get_prior_by_country_by_product_fert(*args):
    country_id = 'GADM-AFG'
    product_id = 'inorganicNitrogenFertiliserUnspecifiedKgN'
    prior_filename = os.path.join(fixtures_path, 'prior_fert', 'result.csv')
    vals = get_prior_by_country_by_product(prior_filename, country_id, product_id)
    assert [round(v) for v in vals] == [8, 14, 10, 5]


@patch('hestia_earth.distribution.utils.priors.load_from_storage', side_effect=fake_read_prior_file('prior_pest'))
def test_get_prior_by_country_by_product_pest(*args):
    country_id = 'GADM-GBR'
    product_id = 'pesticideUnspecifiedAi'
    prior_filename = os.path.join(fixtures_path, 'prior_pest', 'result.csv')
    vals = get_prior_by_country_by_product(prior_filename, country_id, product_id)
    assert [round(v) for v in vals] == [3, 2, 4, 0]


@patch('hestia_earth.distribution.utils.priors.load_from_storage', side_effect=fake_read_prior_file('prior_irrigation'))
def test_get_prior_by_country_by_product_irrigation(*args):
    country_id = 'GADM-GBR'
    product_id = 'waterSourceUnspecified'
    prior_filename = os.path.join(fixtures_path, 'prior_irrigation', 'result.csv')
    vals = get_prior_by_country_by_product(prior_filename, country_id, product_id)
    assert [round(v) for v in vals] == [13, 12, 10, 3]
