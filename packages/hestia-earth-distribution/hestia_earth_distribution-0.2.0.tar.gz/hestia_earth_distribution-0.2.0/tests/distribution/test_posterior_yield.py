from unittest.mock import patch
from hestia_earth.distribution.posterior_yield import (
    update_all_post, get_post, get_post_ensemble
)

class_path = 'hestia_earth.distribution.posterior_yield'


@patch(f"{class_path}.get_post_ensemble_data")
def test_get_post_ensemble(mock_get_post_ensemble_data):
    get_post_ensemble('GADM-COL', 'bananaFruit')
    mock_get_post_ensemble_data.assert_called_once()


@patch(f"{class_path}.generate_prior_yield_file", return_value={})
@patch(f"{class_path}.update_all_post_data")
def test_update_all_post(mock_update_all_post_data, *args):
    update_all_post('GADM-COL')
    mock_update_all_post_data.assert_called_once()


@patch(f"{class_path}.get_post_data")
def test_get_post(mock_get_post_data):
    get_post('GADM-COL', 'bananaFruit')
    mock_get_post_data.assert_called_once()
