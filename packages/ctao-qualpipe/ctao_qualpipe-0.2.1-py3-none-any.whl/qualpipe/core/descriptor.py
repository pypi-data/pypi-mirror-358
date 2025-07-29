"""Descriptor to be taken from datapoint (e.g. average) that can be tested with a `~qualpipe.core.criterion`."""

from abc import ABC, abstractmethod

import numpy as np
from ctapipe.core import Component, TelescopeComponent

__all__ = [
    "BaseDescriptor",
    "BaseTelescopeDescriptor",
    "BasePercentageDescriptor",
    "BaseMedianDescriptor",
    "BaseMeanDescriptor",
    "PercentageDescriptor",
    "MedianDescriptor",
    "MeanDescriptor",
    "TelescopePercentageDescriptor",
    "TelescopeMedianDescriptor",
    "TelescopeMeanDescriptor",
]


class BaseDescriptor(ABC):
    """Base class for all descriptors."""

    @abstractmethod
    def __call__(self, datapoint, tel_id=None):
        """Return the modified datapoint value."""
        pass

    def __str__(self):
        """Pretty string representation for printing."""
        trait_names = self.trait_names()
        formatted_attrs = "\n  ".join(
            f"{name}: {getattr(self, name)}" for name in trait_names
        )
        return f"{self.__class__.__name__}:\n  {formatted_attrs}"


class BaseTelescopeDescriptor(TelescopeComponent):
    """Base class for telescope-specific descriptors."""

    @abstractmethod
    def __call__(self, datapoint, tel_id):
        """Return the modified datapoint value for a specific telescope."""
        pass


class BasePercentageDescriptor(BaseDescriptor):
    """Base class for percentage descriptors."""

    def __call__(self, datapoint, tel_id=None):
        """Compute descriptor value."""
        value = np.array(datapoint)
        return (value != 0).sum() / len(value) * 100


class BaseMedianDescriptor(BaseDescriptor):
    """Base class for median descriptors."""

    def __call__(self, datapoint, tel_id=None):
        """Compute descriptor value."""
        return float(np.nanmedian(datapoint))


class BaseMeanDescriptor(BaseDescriptor):
    """Base class for mean descriptors."""

    def __call__(self, datapoint, tel_id=None):
        """Compute descriptor value."""
        return float(np.nanmean(datapoint))


class PercentageDescriptor(BasePercentageDescriptor, Component):
    """Percentage of non-zero values in an array-like metric."""

    pass


class MedianDescriptor(BaseMedianDescriptor, Component):
    """NaN-Median of an array."""

    pass


class MeanDescriptor(BaseMeanDescriptor, Component):
    """NaN-Mean of an array."""

    pass


class TelescopePercentageDescriptor(BasePercentageDescriptor, BaseTelescopeDescriptor):
    """Percentage of non-zero values in an array-like metric, specific to a telescope."""

    pass


class TelescopeMedianDescriptor(BaseMedianDescriptor, BaseTelescopeDescriptor):
    """NaN-Median of an array, specific to a telescope."""

    pass


class TelescopeMeanDescriptor(BaseMeanDescriptor, BaseTelescopeDescriptor):
    """NaN-Mean of an array, specific to a telescope."""

    pass
