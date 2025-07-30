from unittest.mock import patch

from hestia_earth.distribution.utils.cycle import find_cycles

class_path = 'hestia_earth.distribution.utils.cycle'


@patch(f"{class_path}.download_hestia", return_value={'@id': 'test'})
@patch(f"{class_path}.search", return_value=[{'@id': 'cycle-1'}])
def test_find_yield_cycles(*args):
    country_id = 'GADM-GBR'
    product_id = 'wheatGrain'

    cycles = find_cycles(country_id, product_id, 10)
    assert len(cycles) == 1
