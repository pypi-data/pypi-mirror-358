"""Defines the Metric class for evaluating data quality metrics."""

from enum import Enum

from ctapipe.core import Component, TelescopeComponent
from ctapipe.core.traits import Bool, List, Unicode
from ctapipe.core.traits import Enum as TraitEnum
from traitlets.config import Config

from .criterion import *  # noqa: F403
from .descriptor import *  # noqa: F403

__all__ = ["ArrayElement", "DataCategory", "Metric"]


class ArrayElement(Enum):
    """Enumeration of array elements."""

    DUMMY = "DUMMY"
    SUBARRAY = "SUBARRAY"
    LST = "LST"
    MST = "MST"
    SST = "SST"
    FRAM = "FRAM"
    LIDAR = "LIDAR"
    WEATHER_STATION = "WEATHER_STATION"


class DataCategory(Enum):
    """Enumeration of data categories."""

    DL0_EVENT = "DL0_EVENT"
    DL1_EVENT = "DL1_EVENT"
    DL2_EVENT = "DL2_EVENT"
    DL3_EVENT = "DL3_EVENT"
    DL0_SERVICE = "DL0_SERVICE"
    DL1_SERVICE = "DL1_SERVICE"
    DL2_SERVICE = "DL2_SERVICE"
    DL3_SERVICE = "DL3_SERVICE"
    DL0_MONITORING = "DL0_MONITORING"
    DL1_MONITORING = "DL1_MONITORING"
    DL2_MONITORING = "DL2_MONITORING"
    DL3_MONITORING = "DL3_MONITORING"


class Metric(Component):
    """Defines a data quality metric that applies a descriptor to input data and evaluates quality criteria."""

    name = Unicode(help="Metric name").tag(config=True)
    input_source = Unicode(
        help="HDF5 table path and column name, e.g., '/table/column'"
    ).tag(config=True)
    array_element = TraitEnum(
        ArrayElement,
        help="Array element",
    ).tag(config=True)
    data_category = TraitEnum(
        DataCategory,
        help="Data category (DataLevel/DataType)",
    ).tag(config=True)
    telescope_specific = Bool(
        False, help="Flag to indicate if this is a telescope-specific metric"
    ).tag(config=True)
    descriptor = Unicode(
        None,
        allow_none=True,
        help="Configuration for the descriptor",
    ).tag(config=True)
    criteria = List(help="List of configurations for quality criteria").tag(config=True)

    def __init__(self, **kwargs):
        self.subarray = kwargs.pop("subarray", None)
        super().__init__(**kwargs)

        # Load descriptor (trivial if none is provided)
        if self.telescope_specific:
            base_component_class = TelescopeComponent
            kwargs_dict = {"subarray": self.subarray}
        else:
            base_component_class = Component
            kwargs_dict = {}

        if self.descriptor:
            self._descriptor = base_component_class.from_name(
                self.descriptor, parent=self, **kwargs_dict
            )
        else:
            self._descriptor = (
                lambda data, tel_id=None: data
            )  # Trivial descriptor (identity function)

        # Load quality criteria
        self._criteria = [
            base_component_class.from_name(
                next(iter(criterion)), config=Config(criterion), **kwargs_dict
            )
            for criterion in self.criteria
        ]
        self.log.debug("Metric %s initialized", self.name)
        self.log.debug("Metric's descriptor: %s", self.descriptor)
        self.log.debug("Metric's criteria:")
        for criterion in self._criteria:
            self.log.debug(criterion)

    def __call__(self, data, tel_id=None):
        """Compute the metric value using the descriptor and evaluate quality criteria."""
        if self.telescope_specific and tel_id is None:
            raise ValueError("Telescope-specific metric requires a telescope ID")
        transformed_data = self._descriptor(data, tel_id)

        results = {
            criterion.__class__.__name__: {
                "config": criterion.get_current_config(),
                "result": criterion(
                    transformed_data, tel_id if self.telescope_specific else None
                ),
            }
            for criterion in self._criteria
        }
        return results
