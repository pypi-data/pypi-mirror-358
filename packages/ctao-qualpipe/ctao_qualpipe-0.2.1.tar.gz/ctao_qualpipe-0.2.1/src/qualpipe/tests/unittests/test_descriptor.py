import pytest
from qualpipe.core.descriptor import (
    MeanDescriptor,
    MedianDescriptor,
    PercentageDescriptor,
    TelescopeMeanDescriptor,
    TelescopeMedianDescriptor,
    TelescopePercentageDescriptor,
)


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_median_descriptor():
    datapoint = [0, 1, 2, 3, 4]
    descriptor = MedianDescriptor()
    assert descriptor(datapoint) == 2


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_percentage_descriptor():
    datapoint = [0, 0, 0, 1, 0]
    descriptor = PercentageDescriptor()
    assert descriptor(datapoint) == 20  # %


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_mean_descriptor():
    datapoint = [0, 1, 2, 3, 4]
    descriptor = MeanDescriptor()
    assert descriptor(datapoint) == 2


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_telescope_median_descriptor():
    datapoint = [0, 1, 2, 3, 4]
    descriptor = TelescopeMedianDescriptor(subarray=None)
    assert descriptor(datapoint, tel_id=1) == 2


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_telescope_percentage_descriptor():
    datapoint = [0, 0, 0, 1, 0]
    descriptor = TelescopePercentageDescriptor(subarray=None)
    assert descriptor(datapoint, tel_id=1) == 20  # %


@pytest.mark.verifies_usecase("UC-140-1.2.1")
def test_telescope_mean_descriptor():
    datapoint = [0, 1, 2, 3, 4]
    descriptor = TelescopeMeanDescriptor(subarray=None)
    assert descriptor(datapoint, tel_id=1) == 2
