from pathlib import Path

import pytest
import yaml
from ctapipe.instrument import SubarrayDescription
from qualpipe.core.metric import Metric
from traitlets.config import Config

project_root = Path(__file__).resolve().parents[2]
data_path = project_root / "tests" / "data"
datapoint = [0, 1, 2, 3, 4]


@pytest.fixture()
def setup_metric():
    metric_config_yaml = """
    Metric:
      name: "test_metric"
      input_source: "dummy_data_file.h5:/data"
      array_element: DUMMY
      data_category: DL1_EVENT
      telescope_specific: False
      descriptor: MeanDescriptor
      criteria:
        - RangeCriterion:
            min_value: 0
            max_value: 5
    """
    metric_config_dict = yaml.safe_load(metric_config_yaml)
    metric_config = Config(metric_config_dict)
    metric = Metric(config=metric_config)
    return metric


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_metric_descriptor(setup_metric):
    metric = setup_metric
    result = metric._descriptor(datapoint)
    assert result == 2


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_metric_apply_criteria(setup_metric):
    metric = setup_metric
    results = metric(datapoint)
    assert "RangeCriterion" in results
    assert results["RangeCriterion"]["result"]


@pytest.fixture()
def setup_telescope_specific_metric():
    subarray = SubarrayDescription.from_hdf(f"{data_path}/MonteCarloArray.hdf")
    metric_config_yaml = """
    Metric:
      name: "test_telescope_metric"
      input_source: "dummy_data_file.h5:/data"
      array_element: LST
      data_category: DL1_EVENT
      telescope_specific: True
      descriptor: TelescopeMeanDescriptor
      criteria:
        - TelescopeRangeCriterion:
            min_value:
              - [type, LST*, 0]
              - [type, MST*, 5]
            max_value:
              - [type, LST*, 10]
              - [type, MST*, 15]
    """
    metric_config_dict = yaml.safe_load(metric_config_yaml)
    metric_config = Config(metric_config_dict)
    metric = Metric(config=metric_config, subarray=subarray)
    return metric


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_telescope_specific_metric_descriptor(setup_telescope_specific_metric):
    metric = setup_telescope_specific_metric
    result = metric._descriptor(datapoint, tel_id=1)
    assert result == 2


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_telescope_specific_metric_apply_criteria(setup_telescope_specific_metric):
    metric = setup_telescope_specific_metric
    results = metric(datapoint, tel_id=1)
    assert "TelescopeRangeCriterion" in results
    assert results["TelescopeRangeCriterion"]["result"]


@pytest.fixture()
def setup_metric_with_multiple_criteria():
    metric_config_yaml = """
    Metric:
      name: "test_metric_multiple_criteria"
      input_source: "dummy_data_file.h5:/data"
      array_element: DUMMY
      data_category: DL1_EVENT
      telescope_specific: False
      descriptor: MeanDescriptor
      criteria:
        - RangeCriterion:
            min_value: 0
            max_value: 5
        - ThresholdCriterion:
            threshold: 2
            above: True
    """
    metric_config_dict = yaml.safe_load(metric_config_yaml)
    metric_config = Config(metric_config_dict)
    metric = Metric(config=metric_config)
    return metric


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_metric_with_multiple_criteria_descriptor(setup_metric_with_multiple_criteria):
    metric = setup_metric_with_multiple_criteria
    result = metric._descriptor(datapoint)
    assert result == 2


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_metric_with_multiple_criteria_apply_criteria(
    setup_metric_with_multiple_criteria,
):
    metric = setup_metric_with_multiple_criteria
    results = metric(datapoint)
    assert "RangeCriterion" in results
    assert results["RangeCriterion"]["result"]
    assert "ThresholdCriterion" in results
    assert not results["ThresholdCriterion"]["result"]
