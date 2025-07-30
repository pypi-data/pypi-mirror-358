from unittest.mock import patch
import os
import numpy as np
import pandas as pd
from hestia_earth.utils.tools import list_average
from hestia_earth.utils.model import find_primary_product

from tests.utils import fixtures_path
from tests.integration.utils import load_posterior_cycles, calculate_false_rates
from hestia_earth.distribution.utils.MCMC_mv import calculate_fit_2d, calculate_fit_mv
from hestia_earth.distribution.utils.cycle import (
    YIELD_COLUMN, FERTILISER_COLUMNS, PESTICIDE_COLUMN,
    sum_fertilisers, sum_pesticides
)

class_path = 'hestia_earth.distribution.utils.MCMC_mv'


def fake_generate_likl_file():
    def run(country_id, product_id, *args):
        likl_file = os.path.join(fixtures_path, 'integration', f"posterior_{'_'.join([country_id, product_id])}.csv")
        return pd.read_csv(likl_file, na_values='-') if os.path.exists(likl_file) else pd.DataFrame()
    return run


@patch(f"{class_path}.generate_likl_file", side_effect=fake_generate_likl_file())
def _validate_cycle(cycle: dict, *args):
    country_id = cycle.get('site', {}).get('country', {}).get('@id')
    product = find_primary_product(cycle)
    product_id = product.get('term', {}).get('@id')
    print(f"Validating Cycle: {cycle.get('@id', cycle.get('id'))}, product {product_id} in {country_id}")

    avg_yield = list_average(product.get('value'), 0)
    fertilisers_values = sum_fertilisers(cycle)
    pesticides_value = sum_pesticides(cycle)

    input_cols = FERTILISER_COLUMNS[:3] + [PESTICIDE_COLUMN]
    values = {
        FERTILISER_COLUMNS[0]: fertilisers_values[FERTILISER_COLUMNS[0]],
        FERTILISER_COLUMNS[1]: fertilisers_values[FERTILISER_COLUMNS[1]],
        FERTILISER_COLUMNS[2]: fertilisers_values[FERTILISER_COLUMNS[2]],
        PESTICIDE_COLUMN: pesticides_value
        # IRRIGATION_COLUMN: sum_water(cycle)
    }

    scores = [calculate_fit_2d([values[inp], avg_yield], country_id, product_id,
                               columns=[inp, YIELD_COLUMN])[0] if not np.isnan(values[inp]) else 1
              for inp in input_cols]
    print('scores=', scores)
    return [s >= 0.05 for s in scores]


@patch(f"{class_path}.generate_likl_file", side_effect=fake_generate_likl_file())
def _validate_cycle_mv(cycle: dict, *args):
    country_id = cycle.get('site', {}).get('country', {}).get('@id')
    product = find_primary_product(cycle)
    product_id = product.get('term', {}).get('@id')
    print(f"Validating Cycle: {cycle.get('@id', cycle.get('id'))}, product {product_id} in {country_id}")

    avg_yield = list_average(product.get('value'), 0)
    fertilisers_values = sum_fertilisers(cycle)

    values = {
        FERTILISER_COLUMNS[0]: fertilisers_values[FERTILISER_COLUMNS[0]],
        FERTILISER_COLUMNS[1]: fertilisers_values[FERTILISER_COLUMNS[1]],
        FERTILISER_COLUMNS[2]: fertilisers_values[FERTILISER_COLUMNS[2]]
    }

    score_mv = calculate_fit_mv(list(values.values()) + [avg_yield], country_id, product_id,
                                columns=FERTILISER_COLUMNS[:3] + [YIELD_COLUMN])[0]
    print('score_mv=', score_mv)
    return np.nan if score_mv is None else score_mv >= 0.05


def test_validate_cycles_n():
    cycles, df = load_posterior_cycles()
    # All entries incomplete should be ignored
    results = list(map(_validate_cycle, cycles))
    results = np.transpose(results)
    expected = df['valid_bi_n'].to_list()

    falsepos, falseneg = calculate_false_rates(results[0], expected)
    assert falsepos < 0.1
    assert falseneg < 0.1


def test_validate_cycles_p():
    cycles, df = load_posterior_cycles()
    # All entries incomplete should be ignored
    results = list(map(_validate_cycle, cycles))
    results = np.transpose(results)
    expected = df['valid_bi_p'].to_list()

    falsepos, falseneg = calculate_false_rates(results[1], expected)
    assert falsepos < 0.1
    assert falseneg < 0.1


def test_validate_cycles_k():
    cycles, df = load_posterior_cycles()
    # All entries incomplete should be ignored
    results = list(map(_validate_cycle, cycles))
    results = np.transpose(results)
    expected = df['valid_bi_p'].to_list()

    falsepos, falseneg = calculate_false_rates(results[2], expected)
    assert falsepos < 0.1
    assert falseneg < 0.1


def test_validate_cycles_pest():
    cycles, df = load_posterior_cycles()
    # All entries incomplete should be ignored
    results = list(map(_validate_cycle, cycles))
    results = np.transpose(results)
    expected = df['valid_bi_pest'].to_list()

    falsepos, falseneg = calculate_false_rates(results[3], expected)
    assert falsepos < 0.1
    assert falseneg < 0.1


def test_validate_cycles_mv():
    cycles, df = load_posterior_cycles()
    # All entries incomplete should be ignored
    results = list(map(_validate_cycle_mv, cycles))
    expected = df['valid_mv'].to_list()

    falsepos, falseneg = calculate_false_rates(results, expected)
    assert falsepos < 0.1
    assert falseneg < 0.1
