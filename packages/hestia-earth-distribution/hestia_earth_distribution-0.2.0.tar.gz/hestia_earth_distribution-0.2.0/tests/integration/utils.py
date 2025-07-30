import os
import json
import pandas as pd
import numpy as np
from tests.utils import fixtures_path

fixtures_folder = os.path.join(fixtures_path, 'integration')


def load_integration_file(type: str, id: str):
    with open(os.path.join(fixtures_path, 'integration', f"{type}s", f"{id}.jsonld"), 'r') as json_file:
        return json.load(json_file)


def load_posterior_cycles(filename: str = 'posterior_GADM-GBR_wheatGrain.csv'):
    df = pd.read_csv(os.path.join(fixtures_folder, filename),
                     index_col='cycle.id',
                     na_values='-')
    return [load_integration_file('cycle', cycle_id) for cycle_id in df.index], df


def validate_value(value: float, mu: float, sd: float, Z: float = 1.96):
    _min = max(0, mu-(Z*sd)) if mu is not None else None
    _max = mu+(Z*sd) if mu is not None else None
    return _min <= value <= _max if mu is not None else True


def calculate_false_rates(results: list, expected: list):
    res = np.array(results).astype(bool)
    exp = np.array(expected).astype(bool)
    false_pos = len([f for f in np.where(res)[0] if f in np.where(~exp)[0]]) / len(res) if len(res) > 0 else 0
    false_neg = len([f for f in np.where(~res)[0] if f in np.where(exp)[0]]) / len(res) if len(res) > 0 else 0
    print(f"False positive rate: {false_pos}, false negative rate: {false_neg}")
    return false_pos, false_neg
