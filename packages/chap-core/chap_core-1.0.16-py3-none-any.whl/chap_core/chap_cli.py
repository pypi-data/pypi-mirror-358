"""
NOTE: This file is not used in the current implementation of the CHAP-app. The functionanality is deprecated and this file will
be removed in the future.
"""

from pathlib import Path
import logging
import json

from cyclopts import App

from chap_core.api_types import PredictionRequest
from chap_core.assessment.forecast import forecast_ahead
from chap_core.assessment.prediction_evaluator import evaluate_model
from chap_core.datatypes import FullData
from chap_core.rest_api_src.worker_functions import dataset_from_request_v1
from chap_core.spatio_temporal_data.temporal_dataclass import DataSet
from chap_core.time_period import delta_month
from chap_core.geoutils import buffer_point_features, inspect_feature_collection

# model_type = Literal[*model_dict.keys()]
from chap_core.predictor.model_registry import registry

logger = logging.getLogger(__name__)


# def _get_model(model_id: str):
#     if model_id == "naive_model":
#         return NaiveEstimator()
#     elif model_id == "chap_ewars_monthly":
#         return get_model_from_directory_or_github_url(
#             "https://github.com/sandvelab/chap_auto_ewars"
#         )
#     elif model_id == "chap_ewars_weekly":
#         return get_model_from_directory_or_github_url(
#             "https://github.com/sandvelab/chap_auto_ewars_weekly")
#     else:
#         raise ValueError(
#             f"Unknown model id: {model_id}, expected one of 'naive_model', 'chap_ewars'"
#         )


def harmonize(input_filename: Path, output_filename: Path, point_buffer: float = None):
    """
    Harmonize health and population data from dhis2 with climate data from google earth engine.

    Parameters
    ----------
    input_filename: Path
        The path to the input json-file downloaded from the CHAP-app
    output_filename: Path
        The path to the output csv-file with climate data and health data harmonized
    point_buffer : float (optional)
        If the input file contains facilities/point geometries, use this to create a buffer area around each point.
        Specified as a numeric distance given in the same coordinate system units as the point geometry.
        For latitude-longitude geometries, a distance of 0.1 is approximately 10 km at the equator but increases towards
        the poles.
    """

    logger.info(f"Converting {input_filename} to {output_filename}")
    polygons_filename = output_filename.with_suffix(".geojson")

    # load input geojson
    with open(input_filename, "r") as f:
        text = f.read()
    request_data = PredictionRequest.model_validate_json(text)

    # inspect data
    stats = inspect_feature_collection(request_data.orgUnitsGeoJson)
    logger.info(f"Input feature stats:\n{json.dumps(stats, indent=4)}")

    # convert points to polygons by adding a buffer
    request_data.orgUnitsGeoJson = buffer_point_features(request_data.orgUnitsGeoJson, point_buffer)

    # write to geojson
    geojson = request_data.orgUnitsGeoJson.model_dump_json()
    with open(polygons_filename, "w") as f:
        f.write(geojson)

    # harmonize
    dataset = dataset_from_request_v1(request_data, usecwd_for_credentials=True)

    # write to csv
    dataset.to_csv(output_filename)


def evaluate(
    data_filename: Path,
    output_filename: Path,
    model_id: registry.model_type,
    prediction_length: int = None,
    n_test_sets: int = None,
):
    """
    Evaluate how well a model would predict on the last year of the given dataset. Writes a report to the output file.

    Parameters
    ----------
    data_filename: Path
        The path to the dataset to evaluate, typically created by chap-cli harmonize
    output_filename: Path
        The path to the output pdf-file with the evaluation report
    model_id: str
        The id of the model to evaluate.
    prediction_length: int
        The number of periods to predict ahead. Defaults to 3 months for monthly data and 12 weeks for weekly data
    n_test_sets: int
        The number of test sets to evaluate on. Defaults to a value so that the lenght of the test set is one year
    """
    data_set = DataSet.from_csv(data_filename, FullData)
    if prediction_length is None:
        prediction_length = 3 if data_set.period_range.delta == delta_month else 12
    if n_test_sets is None:
        n_periods = 12 if data_set.period_range.delta == delta_month else 52
        n_test_sets = n_periods - prediction_length + 1
    logger.info(
        f"Evaluating {model_id} on {data_filename} with {n_test_sets} test sets for {prediction_length} periods ahead"
    )
    model = registry.get_model(model_id)
    results = evaluate_model(
        model,
        data_set,
        prediction_length=prediction_length,
        n_test_sets=n_test_sets,
        report_filename=output_filename,
    )
    logger.info(results[0])


def predict(
    data_filename: Path,
    output_filename: Path,
    model_id: registry.model_type,
    prediction_length: int = None,
    do_summary=False,
):
    """
    Predict ahead using the given model trained by the given dataset. Writes the predictions to the output file.
    If do_summary is True, the output file will contain summaries of the predictions, otherwise the full samples.

    Parameters
    ----------
    data_filename: Path
        The path to the dataset to predict ahead on, typically created by chap-cli harmonize
    output_filename: Path
        The path to the output csv-file with the predictions
    model_id: str
        The id of the model to predict with.
    """
    data_set = DataSet.from_csv(data_filename, FullData)
    if prediction_length is None:
        prediction_length = 3 if data_set.period_range.delta == delta_month else 12
    model = registry.get_model(model_id)
    samples = forecast_ahead(model, data_set, prediction_length)
    if do_summary:
        predictions = DataSet({location: samples.summaries() for location, samples in samples.items()})
    else:
        predictions = samples
    predictions.to_csv(output_filename)


def main():
    app = App()
    print("!!!\nTHE COMMANDS UNDER CHAP-CLI ARE DEPRECATED AND WILL BE REMOVED IN THE FUTURE\n!!!")
    app.command(harmonize)
    app.command(evaluate)
    app.command(predict)
    app()
