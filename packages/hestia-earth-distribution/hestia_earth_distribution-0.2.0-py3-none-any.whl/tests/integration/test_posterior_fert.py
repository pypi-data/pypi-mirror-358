from hestia_earth.utils.model import find_primary_product

from tests.utils import is_empty
from tests.integration.utils import load_posterior_cycles, validate_value, calculate_false_rates
from hestia_earth.distribution.utils.cycle import get_fert_ids, sum_fertilisers
from hestia_earth.distribution.posterior_fert import get_post

# avoid getting the same value multiple times
_posterior_data = {}


def _load_posterior(country_id: str, product_id: str, fert_id: str):
    global _posterior_data

    if not _posterior_data.get(country_id, {}).get(product_id, {}).get(fert_id):
        mu, sd = get_post(country_id, product_id, fert_id)
        _posterior_data[country_id] = _posterior_data.get(country_id, {})
        _posterior_data[country_id][product_id] = _posterior_data[country_id].get(product_id, {})
        _posterior_data[country_id][product_id][fert_id] = (mu, sd)

    return _posterior_data.get(country_id).get(product_id).get(fert_id)


def _should_validate(cycle: dict):
    # TODO: make sure at least one fertilisers type has a value, otherwise should not validate
    return cycle.get('completeness', {}).get('fertiliser', False)


def _validate_cycle(cycle: dict):
    country_id = cycle.get('site', {}).get('country', {}).get('@id')
    product = find_primary_product(cycle)
    product_id = product.get('term', {}).get('@id')
    print(f"Validating Cycle: {cycle.get('@id', cycle.get('id'))}, product {product_id} in {country_id}")

    fertilisers_values = sum_fertilisers(cycle)
    passes = []
    for val, fert_id in zip(fertilisers_values.values(), get_fert_ids()):
        mu, sd = _load_posterior(country_id, product_id, fert_id)
        passes.append(validate_value(val, mu, sd))
    return all(passes)


def test_validate_cycles():
    cycles, df = load_posterior_cycles()
    # All entries without a value or incomplete should be ignored
    results = list(map(_validate_cycle, filter(_should_validate, cycles)))
    expected = [v for v in df['valid_fert'].to_list() if not is_empty(v)]
    # assert results == expected

    falsepos, falseneg = calculate_false_rates(results, expected)
    assert falsepos < 0.1
    assert falseneg < 0.1
