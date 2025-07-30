from hestia_earth.utils.tools import list_average
from hestia_earth.utils.model import find_primary_product

from tests.integration.utils import load_posterior_cycles, validate_value, calculate_false_rates
from hestia_earth.distribution.posterior_yield import get_post

# avoid getting the same value multiple times
_posterior_data = {}


def _load_posterior(country_id: str, product_id: str):
    global _posterior_data

    if not _posterior_data.get(country_id, {}).get(product_id):
        mu, sd = get_post(country_id, product_id)
        _posterior_data[country_id] = _posterior_data.get(country_id, {})
        _posterior_data[country_id][product_id] = (mu, sd)

    return _posterior_data.get(country_id).get(product_id)


def _validate_cycle(cycle: dict):
    country_id = cycle.get('site', {}).get('country', {}).get('@id')
    product = find_primary_product(cycle)
    product_id = product.get('term', {}).get('@id')
    print(f"Validating Cycle: {cycle.get('@id', cycle.get('id'))}, product {product_id} in {country_id}")

    avg_yield = list_average(product.get('value'), 0)
    mu, sd = _load_posterior(country_id, product_id)
    return validate_value(avg_yield, mu, sd)


def test_validate_cycles():
    cycles, df = load_posterior_cycles()
    # All entries incomplete should be ignored
    results = list(map(_validate_cycle, cycles))
    expected = df['valid_yield'].to_list()
    # assert results == expected

    falsepos, falseneg = calculate_false_rates(results, expected)
    assert falsepos < 0.1
    assert falseneg < 0.1
