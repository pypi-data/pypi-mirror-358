from hestia_earth.utils.model import find_primary_product

from tests.utils import is_empty
from tests.integration.utils import load_posterior_cycles, validate_value, calculate_false_rates
from hestia_earth.distribution.posterior_pest import get_post
from hestia_earth.distribution.utils.cycle import sum_pesticides

# avoid getting the same value multiple times
_posterior_data = {}


def _load_posterior(country_id: str, product_id: str):
    global _posterior_data

    if not _posterior_data.get(country_id, {}).get(product_id):
        mu, sd = get_post(country_id, product_id)
        _posterior_data[country_id] = _posterior_data.get(country_id, {})
        _posterior_data[country_id][product_id] = (mu, sd)

    return _posterior_data.get(country_id).get(product_id)


def _should_validate(cycle: dict):
    return cycle.get('completeness', {}).get('pesticideVeterinaryDrug', False)


def _validate_cycle(cycle: dict):
    country_id = cycle.get('site', {}).get('country', {}).get('@id')
    product = find_primary_product(cycle)
    product_id = product.get('term', {}).get('@id')
    print(f"Validating Cycle: {cycle.get('@id', cycle.get('id'))}, product {product_id} in {country_id}")

    value = sum_pesticides(cycle)
    mu, sd = _load_posterior(country_id, product_id)
    return validate_value(value, mu, sd)


def test_validate_cycles():
    cycles, df = load_posterior_cycles()
    # All entries without a value or incomplete should be ignored
    results = list(map(_validate_cycle, filter(_should_validate, cycles)))
    expected = [v for v in df['valid_pest'].to_list() if not is_empty(v)]

    falsepos, falseneg = calculate_false_rates(results, expected)
    assert falsepos < 0.1
    assert falseneg < 0.1
