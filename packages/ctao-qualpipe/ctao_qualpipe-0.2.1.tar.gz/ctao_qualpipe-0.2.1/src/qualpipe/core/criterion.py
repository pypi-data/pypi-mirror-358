"""Criteria to assess the data quality."""

from abc import ABC, abstractmethod

import numpy as np
from ctapipe.core import Component, TelescopeComponent
from ctapipe.core.traits import Bool, Float, TelescopeParameter

__all__ = [
    "BaseQualityCriterion",
    "BaseTelescopeQualityCriterion",
    "BaseRangeCriterion",
    "BaseThresholdCriterion",
    "RangeCriterion",
    "TelescopeRangeCriterion",
    "ThresholdCriterion",
    "TelescopeThresholdCriterion",
]


class BaseQualityCriterion(ABC):
    """Base class for all quality criteria."""

    @abstractmethod
    def _get_parameters(self, tel_id=None):
        """Retrieve the parameters for the criterion, either globally or per telescope."""
        pass

    @abstractmethod
    def __call__(self, metric, tel_id=None):
        """Evaluate the criterion against the metric."""
        pass

    def __str__(self):
        """Pretty string representation for printing."""
        trait_names = self.trait_names()
        formatted_attrs = "\n  ".join(
            f"{name}: {getattr(self, name)}" for name in trait_names
        )
        return f"{self.__class__.__name__}:\n  {formatted_attrs}"


class BaseTelescopeQualityCriterion(TelescopeComponent):
    """Base class for telescope-specific quality criteria."""

    @abstractmethod
    def __call__(self, metric, tel_id):
        """Evaluate the criterion against the metric for a specific telescope."""
        pass


class BaseRangeCriterion(BaseQualityCriterion):
    """Abstract base class for range-based quality criteria."""

    def _get_parameters(self, tel_id=None):
        """Retrieve the min and max values, either globally or per telescope."""
        if tel_id is not None:
            return self.min_value.tel[tel_id], self.max_value.tel[tel_id]
        return self.min_value, self.max_value

    def __call__(self, data, tel_id=None):
        """Check if all values in the metric are within the range."""
        min_value, max_value = self._get_parameters(tel_id)
        return bool(np.all((data >= min_value) & (data <= max_value)))


class RangeCriterion(BaseRangeCriterion, Component):
    """Range-based quality criterion for general components."""

    min_value = Float(
        help="Minimum allowed value", allow_none=False, default_value=None
    ).tag(config=True)
    max_value = Float(
        help="Maximum allowed value", allow_none=False, default_value=None
    ).tag(config=True)


class TelescopeRangeCriterion(BaseRangeCriterion, BaseTelescopeQualityCriterion):
    """Telescope-specific range criterion using per-telescope parameters."""

    min_value = TelescopeParameter(trait=Float(), help="Minimum allowed value").tag(
        config=True
    )
    max_value = TelescopeParameter(trait=Float(), help="Maximum allowed value").tag(
        config=True
    )


class BaseThresholdCriterion(BaseQualityCriterion):
    """Abstract base class for threshold-based criteria."""

    def _get_parameters(self, tel_id=None):
        """Retrieve the threshold value, either globally or per telescope."""
        return self.threshold.tel[tel_id] if tel_id is not None else self.threshold

    def __call__(self, data, tel_id=None):
        """Check if all values in the metric satisfy the threshold condition."""
        threshold = self._get_parameters(tel_id)
        return bool(
            np.all(data > threshold) if self.above else np.all(data < threshold)
        )


class ThresholdCriterion(BaseThresholdCriterion, Component):
    """Threshold-based quality criterion for general components."""

    threshold = Float(help="Threshold value", allow_none=False, default_value=None).tag(
        config=True
    )
    above = Bool(
        help="Check if values are above (True) or below (False) the threshold",
        allow_none=False,
        default_value=None,
    ).tag(config=True)


class TelescopeThresholdCriterion(
    BaseThresholdCriterion, BaseTelescopeQualityCriterion
):
    """Telescope-specific threshold criterion using per-telescope parameters."""

    threshold = TelescopeParameter(trait=Float(), help="Threshold value").tag(
        config=True
    )
    above = Bool(
        help="Check if values are above (True) or below (False) the threshold",
        allow_none=False,
        default_value=None,
    ).tag(config=True)
