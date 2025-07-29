from pathlib import Path  # noqa: I001

import numpy as np
import pytest
import yaml
from ctapipe.core import Component, TelescopeComponent
from ctapipe.instrument import SubarrayDescription

from qualpipe.core.criterion import (
    RangeCriterion,  # noqa: F401
    TelescopeRangeCriterion,  # noqa: F401
    ThresholdCriterion,  # noqa: F401
    TelescopeThresholdCriterion,  # noqa: F401
)  # noqa: F401
from traitlets.config import Config
from traitlets import TraitError

project_root = Path(__file__).resolve().parents[2]
data_path = project_root / "tests" / "data"


@pytest.fixture()
def range_criterion():
    criterion_config_yaml = """
    RangeCriterion:
      min_value: 0
      max_value: 15
    """
    criterion_config_dict = yaml.safe_load(criterion_config_yaml)
    criterion_config = Config(criterion_config_dict)
    criterion = Component.from_name(
        list(criterion_config.keys())[0], config=criterion_config
    )
    return criterion


@pytest.fixture()
def telescope_range_criterion():
    subarray = SubarrayDescription.from_hdf(f"{data_path}/MonteCarloArray.hdf")
    criterion_config_yaml = """
    TelescopeRangeCriterion:
      min_value:
        - [type, LST*, 3.]
        - [type, MST*, 11]
      max_value:
        - [type, LST*, 10]
        - [type, MST*, 20]
    """
    criterion_config_dict = yaml.safe_load(criterion_config_yaml)
    criterion_config = Config(criterion_config_dict)
    criterion = TelescopeComponent.from_name(
        list(criterion_config.keys())[0], subarray, config=criterion_config
    )
    return criterion


@pytest.fixture()
def threshold_criterion():
    criterion_config_yaml = """
    ThresholdCriterion:
      threshold: 10
      above: True
    """
    criterion_config_dict = yaml.safe_load(criterion_config_yaml)
    criterion_config = Config(criterion_config_dict)
    criterion = Component.from_name(
        list(criterion_config.keys())[0], config=criterion_config
    )
    return criterion


@pytest.fixture()
def telescope_threshold_criterion():
    subarray = SubarrayDescription.from_hdf(f"{data_path}/MonteCarloArray.hdf")
    criterion_config_yaml = """
    TelescopeThresholdCriterion:
      threshold:
        - [type, LST*, 10]
        - [type, MST*, 20]
      above: True
    """
    criterion_config_dict = yaml.safe_load(criterion_config_yaml)
    criterion_config = Config(criterion_config_dict)
    criterion = TelescopeComponent.from_name(
        list(criterion_config.keys())[0], subarray, config=criterion_config
    )
    return criterion


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_range_criterion_call(range_criterion):
    data_within_range = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    data_outside_range = np.array([16, 17, 18])
    assert range_criterion(data_within_range)
    assert not range_criterion(data_outside_range)


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_telescope_range_criterion_call(telescope_range_criterion):
    data_within_range_tel1 = np.array([4, 5, 6, 7, 8, 9])
    data_outside_range_tel1 = np.array([1, 2, 3, 10, 11, 12])
    data_within_range_tel5 = np.array([16, 17, 18, 19])
    data_outside_range_tel5 = np.array([1, 2, 3, 16, 17, 18])
    assert telescope_range_criterion(data_within_range_tel1, tel_id=1)
    assert not telescope_range_criterion(data_outside_range_tel1, tel_id=1)
    assert telescope_range_criterion(data_within_range_tel5, tel_id=5)
    assert not telescope_range_criterion(data_outside_range_tel5, tel_id=5)


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_threshold_criterion_call(threshold_criterion):
    data_above_threshold = np.array([11, 12, 13])
    data_below_threshold = np.array([8, 9])
    assert threshold_criterion(data_above_threshold)
    assert not threshold_criterion(data_below_threshold)


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_telescope_threshold_criterion_call(telescope_threshold_criterion):
    data_above_threshold_tel1 = np.array([11, 12, 13])
    data_below_threshold_tel1 = np.array([8, 9])
    data_above_threshold_tel5 = np.array([21, 22, 23])
    data_below_threshold_tel5 = np.array([18, 19])
    assert telescope_threshold_criterion(data_above_threshold_tel1, tel_id=1)
    assert not telescope_threshold_criterion(data_below_threshold_tel1, tel_id=1)
    assert telescope_threshold_criterion(data_above_threshold_tel5, tel_id=5)
    assert not telescope_threshold_criterion(data_below_threshold_tel5, tel_id=5)


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_missing_min_value_in_range_criterion_config():
    """Missing entirely 'min_value: 0' item."""

    wrong_criterion_config_yaml = """
    RangeCriterion:
      max_value: 15
    """
    wrong_criterion_config_dict = yaml.safe_load(wrong_criterion_config_yaml)
    wrong_criterion_config = Config(wrong_criterion_config_dict)
    criterion = Component.from_name(
        list(wrong_criterion_config.keys())[0], config=wrong_criterion_config
    )
    datapoint = np.array([0, 1, 2, 3, 4])

    # Verify that a TraitError is raisesd when calling the RangeCriterion component
    with pytest.raises(
        TraitError,
    ) as exc_info:
        criterion(datapoint)

    # Access the original cause of the TraitError
    original_exception = exc_info.value.__context__
    assert isinstance(original_exception, KeyError)
    assert "'min_value'" in str(original_exception)


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_missing_max_value_in_range_criterion_config():
    """Missing entirely 'max_value: 15' item."""

    wrong_criterion_config_yaml = """
    RangeCriterion:
      min_value: 0
    """
    wrong_criterion_config_dict = yaml.safe_load(wrong_criterion_config_yaml)
    wrong_criterion_config = Config(wrong_criterion_config_dict)
    wrong_criterion = Component.from_name(
        list(wrong_criterion_config.keys())[0], config=wrong_criterion_config
    )
    datapoint = np.array([0, 1, 2, 3, 4])

    # Verify that a TraitError is raisesd when calling the RangeCriterion component
    with pytest.raises(
        TraitError,
    ) as exc_info:
        wrong_criterion(datapoint)

    # Access the original cause of the TraitError
    original_exception = exc_info.value.__context__
    assert isinstance(original_exception, KeyError)
    assert "'max_value'" in str(original_exception)


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_missing_min_value_in_telescope_range_criterion_config():
    """Missing entirely 'min_value: - [type, LST*, 3.]' item"""

    subarray = SubarrayDescription.from_hdf(f"{data_path}/MonteCarloArray.hdf")
    wrong_criterion_config_yaml = """
    TelescopeRangeCriterion:
      max_value:
        - [type, LST*, 10]
        - [type, MST*, 20]
    """
    wrong_criterion_config_dict = yaml.safe_load(wrong_criterion_config_yaml)
    wrong_criterion_config = Config(wrong_criterion_config_dict)
    wrong_criterion = TelescopeComponent.from_name(
        list(wrong_criterion_config.keys())[0],
        subarray,
        config=wrong_criterion_config,
    )
    datapoint = np.array([0, 1, 2, 3, 4])

    # Verify that a KeyError is raised when calling the TelescopeRangeCriterion component
    with pytest.raises(
        KeyError,
        match="TelescopeParameterLookup: no parameter value was set for telescope with tel_id=1. Please set it explicitly, or by telescope type or '*'.",
    ):
        wrong_criterion(datapoint, tel_id=1)


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_missing_max_value_in_telescope_range_criterion_config():
    """Missing entirely 'max_value: - [type, LST*, 20]' item"""

    subarray = SubarrayDescription.from_hdf(f"{data_path}/MonteCarloArray.hdf")
    wrong_criterion_config_yaml = """
    TelescopeRangeCriterion:
      min_value:
        - [type, LST*, 3.]
        - [type, MST*, 11]
    """
    wrong_criterion_config_dict = yaml.safe_load(wrong_criterion_config_yaml)
    wrong_criterion_config = Config(wrong_criterion_config_dict)
    wrong_criterion = TelescopeComponent.from_name(
        list(wrong_criterion_config.keys())[0],
        subarray,
        config=wrong_criterion_config,
    )
    datapoint = np.array([12, 13, 14, 15, 16])

    # Verify that a KeyError is raised when calling the TelescopeRangeCriterion component
    with pytest.raises(
        KeyError,
        match="TelescopeParameterLookup: no parameter value was set for telescope with tel_id=1. Please set it explicitly, or by telescope type or '*'.",
    ):
        wrong_criterion(datapoint, tel_id=1)


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_missing_threshold_parameter_in_threshold_criterion_config():
    """Missing entirely 'threshold: 10' item."""

    wrong_criterion_config_yaml = """
    ThresholdCriterion:
      above: True
    """
    wrong_criterion_config_dict = yaml.safe_load(wrong_criterion_config_yaml)
    wrong_criterion_config = Config(wrong_criterion_config_dict)
    criterion = Component.from_name(
        list(wrong_criterion_config.keys())[0], config=wrong_criterion_config
    )
    datapoint = np.array([0, 1, 2, 3, 4])

    # Verify that a TraitError is raisesd when calling the ThresholdCriterion component
    with pytest.raises(
        TraitError,
    ) as exc_info:
        criterion(datapoint)

    # Access the original cause of the TraitError
    original_exception = exc_info.value.__context__
    assert isinstance(original_exception, KeyError)
    assert "'threshold'" in str(original_exception)


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_missing_above_parameter_in_threshold_criterion_config():
    """Missing entirely 'above: True' item."""

    wrong_criterion_config_yaml = """
    ThresholdCriterion:
      threshold: 10
    """
    wrong_criterion_config_dict = yaml.safe_load(wrong_criterion_config_yaml)
    wrong_criterion_config = Config(wrong_criterion_config_dict)
    wrong_criterion = Component.from_name(
        list(wrong_criterion_config.keys())[0], config=wrong_criterion_config
    )
    datapoint = np.array([0, 1, 2, 3, 4])

    # Verify that a TraitError is raisesd when calling the ThresholdCriterion component
    with pytest.raises(
        TraitError,
        match="The 'above' trait of a ThresholdCriterion instance expected a boolean, not the NoneType None.",
    ) as exc_info:
        wrong_criterion(datapoint)

    # Access the original cause of the TraitError
    original_exception = exc_info.value.__context__
    assert isinstance(original_exception, KeyError)
    assert "'above'" in str(original_exception)


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_missing_threshold_parameter_in_telescope_threshold_criterion_config():
    """Missing entirely 'threshold: - [type, LST*, 10]' item"""

    subarray = SubarrayDescription.from_hdf(f"{data_path}/MonteCarloArray.hdf")
    wrong_criterion_config_yaml = """
    TelescopeThresholdCriterion:
      above: True
    """
    wrong_criterion_config_dict = yaml.safe_load(wrong_criterion_config_yaml)
    wrong_criterion_config = Config(wrong_criterion_config_dict)
    wrong_criterion = TelescopeComponent.from_name(
        list(wrong_criterion_config.keys())[0],
        subarray,
        config=wrong_criterion_config,
    )
    datapoint = np.array([0, 1, 2, 3, 4])

    # Verify that a KeyError is raised when calling the TelescopeThresholdCriterion component
    with pytest.raises(
        KeyError,
        match="TelescopeParameterLookup: no parameter value was set for telescope with tel_id=1. Please set it explicitly, or by telescope type or '*'.",
    ):
        wrong_criterion(datapoint, tel_id=1)


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_missing_above_parameter_in_telescope_threshold_criterion_config():
    """Missing entirely 'above: True' item"""

    subarray = SubarrayDescription.from_hdf(f"{data_path}/MonteCarloArray.hdf")
    wrong_criterion_config_yaml = """
    TelescopeThresholdCriterion:
      threshold:
        - [type, LST*, 10]
        - [type, MST*, 20]
    """
    wrong_criterion_config_dict = yaml.safe_load(wrong_criterion_config_yaml)
    wrong_criterion_config = Config(wrong_criterion_config_dict)
    wrong_criterion = TelescopeComponent.from_name(
        list(wrong_criterion_config.keys())[0],
        subarray,
        config=wrong_criterion_config,
    )
    datapoint = np.array([0, 1, 2, 3, 4])

    # Verify that a TraitError is raisesd when calling the TelescopeThresholdCriterion component
    with pytest.raises(
        TraitError,
        match="The 'above' trait of a TelescopeThresholdCriterion instance expected a boolean, not the NoneType None.",
    ) as exc_info:
        wrong_criterion(datapoint)

    # Access the original cause of the TraitError
    original_exception = exc_info.value.__context__
    assert isinstance(original_exception, KeyError)
    assert "'above'" in str(original_exception)
