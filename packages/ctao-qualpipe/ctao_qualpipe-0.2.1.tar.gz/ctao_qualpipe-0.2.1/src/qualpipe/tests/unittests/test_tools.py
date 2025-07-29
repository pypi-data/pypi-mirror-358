import json
import os

import pytest
from ctapipe.core import run_tool
from qualpipe.tools import MetricEvaluator


@pytest.fixture()
def config_file(tmp_path):
    config_content = """
    MetricEvaluator:
      metrics:
        - Metric:
            name: "atmosphere_height_measurement"
            input_source: "/simulation/service/atmosphere_density_profile/height"
            array_element: WEATHER_STATION
            data_category: DL1_EVENT
            telescope_specific: False
            criteria:
              - RangeCriterion:
                  min_value: 0.0
                  max_value: 120.0

        - Metric:
            name: "atmosphere_height_mean"
            input_source: "/simulation/service/atmosphere_density_profile/height"
            array_element: WEATHER_STATION
            data_category: DL1_EVENT
            telescope_specific: False
            descriptor: MeanDescriptor
            criteria:
              - RangeCriterion:
                  min_value: 30
                  max_value: 40

        - Metric:
            name: "obs_id"
            input_source: "/dl1/event/telescope/parameters/obs_id"
            array_element: LST
            data_category: DL1_EVENT
            telescope_specific: True
            criteria:
              - TelescopeRangeCriterion:
                  min_value: 98
                  max_value: 99
    """
    config_path = tmp_path / "config.yaml"
    config_path.write_text(config_content)
    return config_path


@pytest.fixture()
def dummy_data_file(tmp_path):
    return os.path.join(
        os.path.dirname(__file__), "../data/gamma_LSTSubarray_run99.dl1.h5"
    )


@pytest.mark.xfail(
    reason="This test is expected to fail in CI due to the absence of the test file. A proper test file will be added later."
)
def test_metric_evaluator(config_file, dummy_data_file, tmp_path):
    output_report_path = "report.json"

    # Run the MetricEvaluator tool
    run_tool(
        MetricEvaluator(),
        argv=[
            f"--config={config_file}",
            f"--input-url={dummy_data_file}",
            f"--output-url={output_report_path}",
        ],
    )

    # Check if the output report file is created
    assert os.path.exists(output_report_path)

    # Load the report and check its content
    with open(output_report_path) as f:
        report = json.load(f)

    assert "atmosphere_height_measurement" in report
    assert "atmosphere_height_mean" in report
    assert "obs_id" in report
    # Add more assertions based on the expected content of the report
