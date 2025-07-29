"""Main tool for QualPipe backend that coordinates the reading of the metrics and application of criteria."""

import json

from ctapipe.core import Tool
from ctapipe.core.telescope_component import TelescopePatternList
from ctapipe.core.traits import List, Path, Unicode
from ctapipe.instrument import SubarrayDescription
from ctapipe.io import read_table
from traitlets.config import Config

from ..core.metric import Metric


class CustomJSONEncoder(json.JSONEncoder):
    """Encoder for TelescopePatternList."""

    def default(self, obj):
        """Convert TelescopePatternList to a list of tuples."""
        if isinstance(obj, TelescopePatternList):
            # Convert TelescopePatternList to a list of tuples
            return list(obj)
        return super().default(obj)


class MetricEvaluator(Tool):
    """
    Main class to run the automatic QualPipe.

    The MetricEvaluator class is responsible for managing the sequence of operations required to
    prepare metrics and criteria according to the configuration files. It coordinates the retrieval,
    computation, and application of metrics and criteria within QualPipe.


    :Example:

    Configuration example:

    .. code-block:: yaml

        MetricEvaluator:
          input_url: "dummy_data_file.h5"
          metrics:
            - name: my_array_measurement                # this name will be used in report to identify the measurement
              input_source: "/my_table/my_data_array"   # path to the data in the HDF5 file
              array_element: LST
              data_category: DL1_EVENT
              telescope_specific: False
              descriptor: MeanDescriptor
              criteria:
                - RangeCriterion:
                    min_value: 0
                    max_value: 5

            - name: my_float_measurement
              input_source: "/my_table/my_data_float"
              array_element: LST
              data_category: DL1_EVENT
              telescope_specific: False
              descriptor: Descriptor
              criteria:
                - RangeCriterion:
                    min_value: 0.3
                    max_value: 0.4
          output_url: "report.json"
    """

    input_url = Path(
        help="URL of the input file containing monitoring data",
        allow_none=False,
        exists=True,
        directory_ok=False,
        file_ok=True,
    ).tag(config=True)
    metrics = List(help="List of configs for metrics", minlen=1).tag(config=True)
    output_url = Unicode(
        help="URL of the output report file",
        allow_none=False,
    ).tag(config=True)

    aliases = {
        "input-url": "MetricEvaluator.input_url",
        "output-url": "MetricEvaluator.output_url",
    }

    MONITORING_TEL_GROUP = "/dl1/monitoring/telescope/"

    classes = [Metric]

    def setup(self):
        """Set up the MetricEvaluator class."""
        self._metrics = []
        for metric_dict in self.metrics:
            self.log.debug("MetricEvaluator : Loading metric %s", metric_dict)
            metric_cfg = Config(metric_dict)
            if "telescope_specific" in metric_dict["Metric"]:
                subarray = SubarrayDescription.from_hdf(self.input_url)
                self._metrics.append(
                    Metric(
                        config=Config(metric_cfg),
                        subarray=subarray,
                    )
                )
            else:
                self._metrics.append(Metric(Config(metric_cfg)))

    def _read_data(self, metric, tel_id=None):
        """Read data from the input source."""
        # Implement the logic to read data from the input source
        # For the moment, only DL1 data following the reference DL1 implementation in ctapipe is supported.
        if "DL1" not in metric.data_category:
            raise NotImplementedError("Only DL1 data is supported for the moment")

        table_path, column = metric.input_source.rsplit("/", 1)
        if metric.telescope_specific:
            if tel_id is None:
                raise ValueError("Telescope-specific metric requires a telescope ID")
            data = read_table(
                self.input_url,
                f"{table_path}/tel_{tel_id:03d}",
            )
        else:
            data = read_table(self.input_url, f"{table_path}")

        return data[column]

    def start(self):
        """Loop over all metrics and apply criteria."""
        self.results = {}
        for metric in self._metrics:
            self.results[metric.name] = {}
            if metric.telescope_specific:
                for tel_id in metric.subarray.tel_ids:
                    data = self._read_data(metric, tel_id)
                    results = metric(data, tel_id)
                    id_info = f"{metric.array_element}-{tel_id:03d}"
                    self.results[metric.name][id_info] = results
            else:
                data = self._read_data(metric)
                results = metric(data)
                self.results[metric.name][metric.array_element] = results

    def finish(self):
        """Finish the job and write the final report."""
        self.log.debug("MetricEvaluator : Results: %s", self.results)
        with open(self.output_url, "w") as f:
            json.dump(self.results, f, cls=CustomJSONEncoder, indent=4)
        self.log.info("MetricEvaluator : Finish running automatic QualPipe")


def main():
    """Run the MetricEvaluator tool."""
    tool = MetricEvaluator()
    tool.run()
