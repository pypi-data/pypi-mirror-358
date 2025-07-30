import pandas as pd
import os
import json
from tests.utils import fixtures_path, round_df_column

from hestia_earth.distribution.utils.cycle import (
    INDEX_COLUMN, YIELD_COLUMN, PESTICIDE_COLUMN, IRRIGATION_COLUMN,
    get_input_group, _convert_to_nutrient
)
from hestia_earth.distribution.cycle import (
    cycle_yield_distribution, group_cycle_inputs
)

fixtures_folder = os.path.join(fixtures_path, 'cycle')


def test_cycle_yield_distribution():
    with open(f"{fixtures_folder}/cycles.jsonld", encoding='utf-8') as f:
        cycles = json.load(f)

    expected = pd.read_csv(os.path.join(fixtures_folder, 'distribution.csv'), index_col=INDEX_COLUMN)
    result = cycle_yield_distribution(cycles)
    round_df_column(result, YIELD_COLUMN)
    round_df_column(result, 'Nitrogen (kg N)')
    assert result.to_csv() == expected.to_csv()


def test_group_cycle_inputs():
    with open(f"{fixtures_folder}/cycles.jsonld", encoding='utf-8') as f:
        cycles = json.load(f)
    results = group_cycle_inputs(cycles[0])
    assert results.get('Nitrogen (kg N)') == 192


def test_get_input_group():
    assert get_input_group({'term': {'termType': 'organicFertiliser', 'units': 'kg N'}}) == 'Nitrogen (kg N)'
    assert get_input_group({'term': {'termType': 'organicFertiliser', 'units': 'kg K2O'}}) == 'Potassium (kg K2O)'
    assert get_input_group({'term': {'termType': 'organicFertiliser', 'units': 'kg CaCO3'}}) is None
    assert get_input_group({'term': {'termType': 'pesticideAI'}}) == PESTICIDE_COLUMN
    assert get_input_group({'term': {'termType': 'water'}}) == IRRIGATION_COLUMN


def test_convert_to_nutrient():
    with open(f"{fixtures_folder}/input.jsonld", encoding='utf-8') as f:
        input = json.load(f)

    assert _convert_to_nutrient(input, 'kg N') == 84
    assert _convert_to_nutrient(input, 'kg P2O5') == 48
    assert _convert_to_nutrient(input, 'kg K2O') == 96
