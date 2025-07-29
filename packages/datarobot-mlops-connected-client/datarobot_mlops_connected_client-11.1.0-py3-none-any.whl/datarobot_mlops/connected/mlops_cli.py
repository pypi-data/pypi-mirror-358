#  Copyright (c) 2020 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2024.
#
#  DataRobot, Inc. Confidential.
#  This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.
#  The copyright notice above does not evidence any actual or intended publication of
#  such source code.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.

import argparse
import asyncio
import json
import logging
import numbers
import os
import signal
import sys
import time
from argparse import RawTextHelpFormatter
from contextlib import closing
from enum import Enum

import pandas as pd

from datarobot_mlops.common import config
from datarobot_mlops.common.connected_exception import DRMLOpsConnectedException
from datarobot_mlops.common.enums import DataType
from datarobot_mlops.common.enums import MLOpsSpoolAction
from datarobot_mlops.common.enums import SpoolerType
from datarobot_mlops.common.exception import DRCommonException
from datarobot_mlops.common.exception import DRNotFoundException
from datarobot_mlops.common.sampling import sample_dataframe
from datarobot_mlops.constants import Constants
from datarobot_mlops.metric import AggregationHelper
from datarobot_mlops.metric import SerializationConstants
from datarobot_mlops.spooler.record_spooler_factory import RecordSpoolerFactory

from .client import MLOpsClient
from .enums import DatasetSourceType
from .enums import ExitCode
from .upload_tracker import MLOpsUploadTracker

logger = logging.getLogger(__name__)


class EV:
    """Class to define environment variables used throughout the program."""

    DATAROBOT_ENDPOINT = "DATAROBOT_ENDPOINT"
    DATAROBOT_API_TOKEN = "DATAROBOT_API_TOKEN"
    MLOPS_SERVICE_URL = "MLOPS_SERVICE_URL"
    MLOPS_API_TOKEN = "MLOPS_API_TOKEN"

    MLOPS_MODEL_ID = "MLOPS_MODEL_ID"
    MLOPS_MODEL_PACKAGE_ID = "MLOPS_MODEL_PACKAGE_ID"
    MLOPS_DATASET_ID = "MLOPS_DATASET_ID"
    MLOPS_TRAINING_DATASET_ID = "MLOPS_TRAINING_DATASET_ID"
    MLOPS_HOLDOUT_DATASET_ID = "MLOPS_HOLDOUT_DATASET_ID"
    MLOPS_DEPLOYMENT_ID = "MLOPS_DEPLOYMENT_ID"
    MLOPS_DEPLOYMENT_LABEL = "MLOPS_DEPLOYMENT_LABEL"
    MLOPS_PREDICTION_ENVIRONMENT_ID = "MLOPS_PREDICTION_ENVIRONMENT_ID"
    MLOPS_MONITORING_JOB_ID = "MLOPS_MONITORING_JOB_ID"
    MLOPS_DATAROBOT_APP_VERSION = "MLOPS_DATAROBOT_APP_VERSION"
    MLOPS_BATCH_ID = "MLOPS_BATCH_ID"
    MLOPS_METRIC_ID = "MLOPS_METRIC_ID"
    MLOPS_ASSOCIATION_ID_COLUMN_NAME = "MLOPS_ASSOCIATION_ID_COLUMN_NAME"
    MLOPS_STATS_AGGREGATION_AUTO_SAMPLING_PERCENTAGE = (
        "MLOPS_STATS_AGGREGATION_AUTO_SAMPLING_PERCENTAGE"
    )


class Subjects:
    MAIN_COMMAND = "mlops-cli"
    PERF_TEST = "perf"
    PREDICTIONS = "predictions"
    ACTUALS = "actuals"
    MODEL = "model"
    DATASET = "dataset"
    DEPLOYMENT = "deployment"
    PREDICTION_ENVIRONMENT = "prediction-environment"
    SERVICE_STATS = "service-stats"
    BATCH = "batch"
    CUSTOM_METRICS = "custom_metric"
    MONITORING_JOB = "monitoring-job"

    ALL_SUBJECTS = [
        PERF_TEST,
        PREDICTIONS,
        ACTUALS,
        MODEL,
        DATASET,
        DEPLOYMENT,
        PREDICTION_ENVIRONMENT,
        SERVICE_STATS,
        BATCH,
        CUSTOM_METRICS,
        MONITORING_JOB,
    ]


class Actions:
    UPLOAD = "upload"
    DOWNLOAD = "download"
    CREATE = "create"
    GET = "get"
    FEATURES = "features"
    LIST = "list"
    DELETE = "delete"
    REPLACE = "replace"
    REPORT = "report"
    RUN = "run"
    CANCEL = "cancel"
    DEPLOY = "deploy"
    GET_MODEL = "get-model"
    COUNT = "count"
    RESTART_MONITORING_AGENT = "restart-monitoring-agent"
    RESTART_MANAGEMENT_AGENT = "restart-management-agent"

    ALL_ACTIONS = [
        UPLOAD,
        DOWNLOAD,
        CREATE,
        GET,
        FEATURES,
        LIST,
        DELETE,
        REPLACE,
        REPORT,
        RUN,
        CANCEL,
        DEPLOY,
        GET_MODEL,
        COUNT,
        RESTART_MONITORING_AGENT,
        RESTART_MANAGEMENT_AGENT,
    ]

    PERF_ACTIONS = [RUN]
    PREDICTIONS_ACTIONS = [UPLOAD, GET, REPORT, COUNT]
    ACTUALS_ACTIONS = [REPORT, COUNT]
    MODEL_ACTIONS = [DOWNLOAD, CREATE, GET, LIST, DELETE, REPLACE, DEPLOY]
    DATASET_ACTIONS = [UPLOAD, GET, LIST, DELETE]
    DEPLOYMENT_ACTIONS = [GET, LIST, DELETE, GET_MODEL]
    PREDICTION_ENVIRONMENT_ACTIONS = [
        CREATE,
        GET,
        LIST,
        DELETE,
        RESTART_MONITORING_AGENT,
        RESTART_MANAGEMENT_AGENT,
    ]
    SERVICE_STATS_ACTIONS = [GET]
    BATCH_ACTIONS = [CREATE, GET, LIST]
    CUSTOM_METRICS_ACTIONS = [CREATE, GET, LIST, REPORT]
    MONITORING_JOBS_ACTIONS = [CREATE, GET, LIST, CANCEL, UPLOAD]


SUPPORTED_ACTIONS = {
    Subjects.PERF_TEST: Actions.PERF_ACTIONS,
    Subjects.PREDICTIONS: Actions.PREDICTIONS_ACTIONS,
    Subjects.ACTUALS: Actions.ACTUALS_ACTIONS,
    Subjects.MODEL: Actions.MODEL_ACTIONS,
    Subjects.DATASET: Actions.DATASET_ACTIONS,
    Subjects.DEPLOYMENT: Actions.DEPLOYMENT_ACTIONS,
    Subjects.PREDICTION_ENVIRONMENT: Actions.PREDICTION_ENVIRONMENT_ACTIONS,
    Subjects.SERVICE_STATS: Actions.SERVICE_STATS_ACTIONS,
    Subjects.BATCH: Actions.BATCH_ACTIONS,
    Subjects.CUSTOM_METRICS: Actions.CUSTOM_METRICS_ACTIONS,
    Subjects.MONITORING_JOB: Actions.MONITORING_JOBS_ACTIONS,
}


class ArgumentsOptions:
    VERBOSE = "--verbose"
    QUIET = "--quiet"
    JSON = "--json"
    TERSE = "--terse"
    PREDICTION_ENVIRONMENT_ID = "--prediction-environment-id"
    MONITORING_JOB_ID = "--monitoring-job-id"
    DEPLOYMENT_ID = "--deployment-id"
    MODEL_ID = "--model-id"
    MODEL_PACKAGE_ID = "--model-package-id"
    DOWNLOAD_SCORING_CODE = "--download-scoring-code"
    DEPLOYMENT_LABEL = "--deployment-label"
    DATASET_ID = "--dataset-id"
    TRAINING_DATASET_ID = "--training-dataset-id"
    HOLDOUT_DATASET_ID = "--holdout-dataset-id"
    JSON_CONF = "--json-config"
    OUTPUT_DIRECTORY = "--output-dir"
    OUTPUT_FILE = "--output-file"
    MLOPS_SERVICE = "--mlops-url"
    MLOPS_API_TOKEN = "--api-token"
    NO_VERIFY_SSL = "--no-verify-ssl"
    INPUT = "--input"
    COUNT = "--count"
    ROWS = "--rows"
    TARGET_COL = "--target-col"
    PREDICTION_COLS = "--prediction-cols"
    ASSOC_ID = "--assoc-id-col"
    PREDICTION_TIME = "--prediction-time"
    TIMESTAMP_COL = "--timestamp-col"
    TIMESTAMP_FORMAT = "--timestamp-format"
    ACTED_ON_COL = "--acted-on-col"
    ACTUAL_VALUE_COL = "--actual-value-col"
    DRY_RUN = "--dry-run"
    STATUS_FILE = "--status-file"
    REASON = "--reason"
    WAIT = "--wait"
    FORCE = "--force"
    TIMEOUT = "--timeout"
    FILESYSTEM_DIR = "--filesystem-directory"
    CLASS_NAMES = "--class-names"
    FROM_SPOOL = "--from-spool"
    SEARCH = "--search"
    LIMIT = "--limit"
    NUM_CONCURRENT_REQUESTS = "--num-concurrent-requests"
    SEGMENT_ATTRIBUTES = "--segment-attributes"
    DATAROBOT_APP_VERSION = "--datarobot-app-version"
    ENABLE_BATCH_MONITORING = "--enable-batch-monitoring"
    BATCH_ID = "--batch-id"
    QUERY_BATCH_SERVICE_STATS = "--service-stats"
    QUERY_BATCH_DATA_DRIFT = "--data-drift"
    METRIC_ID = "--metric-id"
    VALUE_COL = "--value-col"
    SAMPLING_PERCENTAGE = "--sampling-percentage"


class RunMode(Enum):
    PERF_TEST = Subjects.PERF_TEST
    PREDICTIONS = Subjects.PREDICTIONS
    ACTUALS = Subjects.ACTUALS
    MODEL = Subjects.MODEL
    DATASET = Subjects.DATASET
    DEPLOYMENT = Subjects.DEPLOYMENT
    PREDICTION_ENVIRONMENT = Subjects.PREDICTION_ENVIRONMENT
    SERVICE_STATS = Subjects.SERVICE_STATS
    BATCH = Subjects.BATCH
    CUSTOM_METRICS = Subjects.CUSTOM_METRICS
    MONITORING_JOBS = Subjects.MONITORING_JOB

    @staticmethod
    def list_all():
        all_subjects = ""
        for m in RunMode:
            all_subjects = f"{all_subjects} {m.value}"
        return all_subjects


REPLACEMENT_REASONS = [
    "ACCURACY",
    "DATA_DRIFT",
    "ERRORS",
    "SCHEDULED_REFRESH",
    "SCORING_SPEED",
    "OTHER",
]


common_fields_keys = SerializationConstants.GeneralConstants
deployment_stats_keys = SerializationConstants.DeploymentStatsConstants
predictions_data_keys = SerializationConstants.PredictionsDataConstants
external_events_keys = SerializationConstants.EventConstants
custom_metric_keys = SerializationConstants.CustomMetricStatsConstants
config_keys = config.ConfigConstants


class MLOpsCliArgParser:
    SUBJECT_KEYWORD = "subject"
    ACTION_KEYWORD = "action"

    parser = None

    @staticmethod
    def _is_valid_file(arg):
        abs_path = os.path.abspath(arg)
        if not os.path.exists(arg):
            raise argparse.ArgumentTypeError(f"The file {arg} does not exist.")
        else:
            return os.path.realpath(abs_path)

    @staticmethod
    def _register_arg_version(*parsers):
        for parser in parsers:
            parser.add_argument(
                "--version",
                action="version",
                version=f"%(prog)s {Constants.MLOPS_VERSION}",
            )

    @staticmethod
    def _register_arg_verbose(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.VERBOSE,
                action="store_true",
                default=False,
                help="Set logging to DEBUG level",
            )

    @staticmethod
    def _register_arg_quiet(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.QUIET,
                action="store_true",
                default=False,
                help="Set logging to ERROR level",
            )

    @staticmethod
    def _register_arg_json(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.JSON,
                action="store_true",
                default=False,
                help="Return JSON as output for create/get/list/delete/deploy",
            )

    @staticmethod
    def _register_arg_terse(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.TERSE,
                action="store_true",
                default=False,
                help="Only return ID(s) as output for create/get/list/delete/deploy",
            )

    @staticmethod
    def _register_arg_subject(*parsers):
        for parser in parsers:
            parser.add_argument(
                dest=MLOpsCliArgParser.SUBJECT_KEYWORD, choices=Subjects.ALL_SUBJECTS
            )

    @staticmethod
    def _register_arg_action(*parsers):
        for parser in parsers:
            parser.add_argument(dest=MLOpsCliArgParser.ACTION_KEYWORD, choices=Actions.ALL_ACTIONS)

    @staticmethod
    def _register_arg_reason(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.REASON, default="OTHER", choices=REPLACEMENT_REASONS
            )

    @staticmethod
    def _register_arg_deployment_id(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.DEPLOYMENT_ID,
                default=os.environ.get(EV.MLOPS_DEPLOYMENT_ID, None),
                help="Deployment ID to use for monitoring model predictions "
                "(env: {})".format(EV.MLOPS_DEPLOYMENT_ID),
            )

    @staticmethod
    def _register_arg_pe_id(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.PREDICTION_ENVIRONMENT_ID,
                default=os.environ.get(EV.MLOPS_PREDICTION_ENVIRONMENT_ID, None),
                help="Prediction Environment ID "
                "(env: {})".format(EV.MLOPS_PREDICTION_ENVIRONMENT_ID),
            )

    @staticmethod
    def _register_arg_monitoring_job_id(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.MONITORING_JOB_ID,
                default=os.environ.get(EV.MLOPS_MONITORING_JOB_ID, None),
                help="Monitoring Job ID " "(env: {})".format(EV.MLOPS_MONITORING_JOB_ID),
            )

    @staticmethod
    def _register_arg_deployment_label(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.DEPLOYMENT_LABEL,
                default=os.environ.get(EV.MLOPS_DEPLOYMENT_LABEL, None),
                help="Deployment label to use when creating a deployment "
                "(env: {})".format(EV.MLOPS_DEPLOYMENT_LABEL),
            )

    @staticmethod
    def _register_arg_model_id(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.MODEL_ID,
                default=os.environ.get(EV.MLOPS_MODEL_ID, None),
                help="Model ID to use for model package creation or prediction monitoring "
                "(env: {})".format(EV.MLOPS_MODEL_ID),
            )

    @staticmethod
    def _register_arg_model_package_id(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.MODEL_PACKAGE_ID,
                default=os.environ.get(EV.MLOPS_MODEL_PACKAGE_ID, None),
                help="Model package ID to use for model package deployment "
                "(env: {})".format(EV.MLOPS_MODEL_PACKAGE_ID),
            )

    @staticmethod
    def _register_arg_download_scoring_code(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.DOWNLOAD_SCORING_CODE,
                default=False,
                dest="download_scoring_code",
                action="store_true",
                help="Download scoring code from registry given model package id",
            )

    @staticmethod
    def _register_arg_dataset_id(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.DATASET_ID,
                default=os.environ.get(EV.MLOPS_DATASET_ID, None),
                help="Dataset ID to use for AI catalog operations "
                "(env: {})".format(EV.MLOPS_DATASET_ID),
            )

    @staticmethod
    def _register_arg_training_dataset_id(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.TRAINING_DATASET_ID,
                default=os.environ.get(EV.MLOPS_TRAINING_DATASET_ID, None),
                help="Dataset ID to use for training set model package creation "
                "(env: {})".format(EV.MLOPS_TRAINING_DATASET_ID),
            )

    @staticmethod
    def _register_arg_holdout_dataset_id(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.HOLDOUT_DATASET_ID,
                default=os.environ.get(EV.MLOPS_HOLDOUT_DATASET_ID, None),
                help="Dataset ID to use for holdout set model package creation "
                "(env: {})".format(EV.MLOPS_HOLDOUT_DATASET_ID),
            )

    @staticmethod
    def _register_arg_json_conf(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.JSON_CONF,
                help="JSON configuration to use for object creation",
            )

    @staticmethod
    def _register_arg_output_dir(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.OUTPUT_DIRECTORY,
                dest="output_dir",
                default="/tmp/",
                help="Output directory to write model package file to",
            )

    @staticmethod
    def _register_arg_output_file(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.OUTPUT_FILE,
                dest="output_file",
                help="Output file to write feature types json",
            )

    @staticmethod
    def _register_arg_mlops_service(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.MLOPS_SERVICE,
                dest="mlops_service_url",
                default=os.environ.get(
                    EV.MLOPS_SERVICE_URL, os.environ.get(EV.DATAROBOT_ENDPOINT, None)
                ),
                help=f"MLOps service URL to use (env: {EV.MLOPS_SERVICE_URL})",
            )

    @staticmethod
    def _register_arg_mlops_api_token(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.MLOPS_API_TOKEN,
                dest="mlops_api_token",
                default=os.environ.get(
                    EV.MLOPS_API_TOKEN, os.environ.get(EV.DATAROBOT_API_TOKEN, None)
                ),
                help=f"MLOps API Token to use for connecting (env: {EV.MLOPS_API_TOKEN})",
            )

    @staticmethod
    def _register_arg_no_verify_ssl(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.NO_VERIFY_SSL,
                dest="verify_ssl",
                default=True,
                action="store_false",
                help="Do not verify SSL connection to DataRobot MLOps",
            )

    @staticmethod
    def _register_arg_search(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.SEARCH,
                dest="search",
                default=None,
                help="Search filter to use when listing items",
            )

    @staticmethod
    def _register_arg_limit(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.LIMIT,
                dest="limit",
                default=None,
                help="Maximum items to return when listing items",
            )

    @staticmethod
    def _register_arg_input(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.INPUT,
                default=None,
                type=MLOpsCliArgParser._is_valid_file,
                help="Path to an input dataset",
            )

    @staticmethod
    def _register_arg_wait(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.WAIT,
                default=False,
                action="store_true",
                help="Wait for request to MLOps to complete",
            )

    @staticmethod
    def _register_arg_force(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.FORCE,
                default=False,
                action="store_true",
                help="Only applicable for deployments owned by the Management Agent. "
                "Forcefully delete the deployment without waiting for a response from the agent.",
            )

    @staticmethod
    def _register_arg_timeout(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.TIMEOUT,
                default=120,
                type=int,
                help="Timeout value for connection in seconds (default: %(default)s s)",
            )

    @staticmethod
    def _register_arg_count(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.COUNT,
                default=5,
                type=int,
                help="Number of iterations; depends on the context in which it is called",
            )

    @staticmethod
    def _register_arg_rows(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.ROWS,
                default=-1,
                type=int,
                help="Number of rows to use from input file",
            )

    @staticmethod
    def _register_target_col(*parsers, default_value=None):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.TARGET_COL,
                default=default_value,
                type=str,
                help="Name of target column in input data",
            )

    @staticmethod
    def _register_prediction_cols(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.PREDICTION_COLS,
                default=None,
                nargs="+",
                type=str,
                help="Name of prediction column(s) in input data",
            )

    @staticmethod
    def _register_class_names(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.CLASS_NAMES,
                default=None,
                nargs="+",
                type=str,
                help="Name of classes for classification data",
            )

    @staticmethod
    def _register_prediction_time(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.PREDICTION_TIME,
                type=int,
                default=10,
                help="Time it took to compute predictions in milliseconds "
                "(default: %(default)s ms)",
            )

    @staticmethod
    def _register_assoc_id_col(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.ASSOC_ID,
                type=str,
                default=os.environ.get(EV.MLOPS_ASSOCIATION_ID_COLUMN_NAME, None),
                help="Name of association ID column in input data",
            )

    @staticmethod
    def _register_actual_value_col(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.ACTUAL_VALUE_COL,
                type=str,
                help="Name of actual value column in input data",
            )

    @staticmethod
    def _register_acted_on_col(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.ACTED_ON_COL,
                default=None,
                type=str,
                help="Name of was-acted-on column in input data",
            )

    @staticmethod
    def _register_timestamp_col(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.TIMESTAMP_COL,
                default=None,
                type=str,
                help="Name of timestamp column in input data",
            )

    @staticmethod
    def _register_value_col(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.VALUE_COL,
                type=str,
                help="Name of value column holding custom metrics values",
            )

    @staticmethod
    def _register_timestamp_format(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.TIMESTAMP_FORMAT,
                default=None,
                type=str,
                help="Format of timestamp column in input data",
            )

    @staticmethod
    def _register_dry_run(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.DRY_RUN,
                action="store_true",
                default=False,
                help="Dry run; no actual requests will be sent to DataRobot MLOps",
            )

    @staticmethod
    def _register_status_file(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.STATUS_FILE,
                default=None,
                help="Path to file tracking status of upload",
            )

    @staticmethod
    def _register_from_spool(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.FROM_SPOOL,
                action="store_true",
                default=False,
                help="Report prediction data from spooler",
            )

    @staticmethod
    def _register_filesystem_dir(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.FILESYSTEM_DIR,
                default=os.environ.get(config_keys.FILESYSTEM_DIRECTORY.name, None),
                help="Path to filesystem spool directory",
            )

    @staticmethod
    def _register_arg_num_concurrent_requests(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.NUM_CONCURRENT_REQUESTS,
                default=1,  # 1 concurrent request => synchronous
                type=int,
                help="Number of concurrent requests for async reporting",
            )

    @classmethod
    def _register_segment_attributes(cls, *parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.SEGMENT_ATTRIBUTES,
                default=None,
                type=str,
                help="Comma-separated segment names, for segment attributes analysis",
            )

    @staticmethod
    def _register_datarobot_app_version(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.DATAROBOT_APP_VERSION,
                default=os.environ.get(EV.MLOPS_DATAROBOT_APP_VERSION, Constants.MLOPS_VERSION),
                type=str,
                help="Version of the DataRobot App this client is communicating with",
            )

    @staticmethod
    def _register_arg_enable_batch_monitoring(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.ENABLE_BATCH_MONITORING,
                dest="enable_batch_monitoring",
                default=False,
                action="store_true",
                help="Enable batch monitoring on the deployment",
            )

    @staticmethod
    def _register_arg_service_stats(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.QUERY_BATCH_SERVICE_STATS,
                dest="batch_service_stats",
                default=False,
                action="store_true",
                help="Query service stats for the given batch",
            )

    @staticmethod
    def _register_arg_data_drift(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.QUERY_BATCH_DATA_DRIFT,
                dest="batch_data_drift",
                default=False,
                action="store_true",
                help="Query data drift for the given batch",
            )

    @staticmethod
    def _register_arg_batch_id(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.BATCH_ID,
                default=os.environ.get(EV.MLOPS_BATCH_ID, None),
                help="Batch ID to use for querying batch statistics (env: {})".format(
                    EV.MLOPS_BATCH_ID
                ),
            )

    @staticmethod
    def _register_arg_metric_id(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.METRIC_ID,
                default=os.environ.get(EV.MLOPS_METRIC_ID, None),
                help="Metric ID to use for querying custom metric statistics (env: {})".format(
                    EV.MLOPS_METRIC_ID
                ),
            )

    @staticmethod
    def _register_arg_sampling_percentage(*parsers):
        for parser in parsers:
            parser.add_argument(
                ArgumentsOptions.SAMPLING_PERCENTAGE,
                default=os.environ.get(EV.MLOPS_STATS_AGGREGATION_AUTO_SAMPLING_PERCENTAGE, 0.0),
                type=float,
                help="Percentage of data to sample from input dataset to report",
            )

    @staticmethod
    def _gen_parser(subcommand, help_msg, description=None):
        subparser = MLOpsCliArgParser._subparsers.add_parser(
            subcommand, help=help_msg, description=description, formatter_class=RawTextHelpFormatter
        )
        MLOpsCliArgParser._parsers[subcommand] = subparser
        return subparser

    @staticmethod
    def _add_perf_subcommand(parser):
        MLOpsCliArgParser._register_arg_input(parser)
        MLOpsCliArgParser._register_arg_count(parser)
        MLOpsCliArgParser._register_arg_rows(parser)

    @staticmethod
    def _add_predictions_subcommand(parser):
        MLOpsCliArgParser._register_prediction_time(parser)
        MLOpsCliArgParser._register_filesystem_dir(parser)
        MLOpsCliArgParser._register_from_spool(parser)
        MLOpsCliArgParser._register_arg_num_concurrent_requests(parser)
        MLOpsCliArgParser._register_segment_attributes(parser)

    @staticmethod
    def _add_actuals_subcommand(parser):
        MLOpsCliArgParser._register_arg_wait(parser)

        MLOpsCliArgParser._register_actual_value_col(parser)
        MLOpsCliArgParser._register_acted_on_col(parser)

    @staticmethod
    def _add_model_subcommand(parser):
        # for model deployment only
        MLOpsCliArgParser._register_arg_deployment_label(parser)

        # for model download only
        MLOpsCliArgParser._register_arg_output_dir(parser)
        MLOpsCliArgParser._register_arg_download_scoring_code(parser)

        # for model feature types fetch
        MLOpsCliArgParser._register_arg_output_file(parser)

        # for model package creation only
        MLOpsCliArgParser._register_arg_training_dataset_id(parser)
        MLOpsCliArgParser._register_arg_holdout_dataset_id(parser)
        MLOpsCliArgParser._register_timestamp_format(parser)

        # for model replacement only
        MLOpsCliArgParser._register_arg_reason(parser)

    @staticmethod
    def get_arg_parser():
        parser = argparse.ArgumentParser(
            formatter_class=RawTextHelpFormatter,
            description="""
        A command line tool for interacting with DataRobot MLOps app.
        All commands require --mlops-service-url and --mlops-api-token or that
        MLOPS_SERVICE_URL and MLOPS_API_TOKEN are set as environment variables.

        Usage is <subject> <action> followed by options. For example:

          # create a prediction environment
          prediction-environment create --json-config <>

          # get information about a prediction environment
          prediction-environment get --prediction-environment-id <>

          # delete a prediction environment (must not have any deployments)
          prediction-environment delete --prediction-environment-id <>

          # upload a dataset into the AI catalog
          dataset upload --input <>

          # delete a dataset from the AI catalog
          dataset delete --dataset-id <>

          # create an external model package
          model create --json-config <> --training-dataset-id <> --holdout-dataset-id <>

          # get model package metadata
          model get --model-package-id <>

          # deploy a model package
          model deploy --model-package-id <> --deployment-label <>

          # download the current model artifact from a deployment (for non-external models only)
          model download --deployment-id <>

          # delete a model package
          model delete --model-package-id <>

          # get metadata about a deployment
          deployment get --deployment-id <>

          # delete a deployment
          deployment delete --deployment-id <>

          # force-delete a deployment managed by the management agent
          deployment delete --deployment-id <> --force

          # upload a ScoringCode classification csv file
          predictions report --prediction-cols <col1> <col2> --input <> --class-names <c1> <c2>

          # upload a spool file
          predictions report --from-spool

          # upload a scoring file to a deployment
          predictions upload --input <> --target-col <> --class-names <>

          # count predictions processed for drift
          predictions count

          # upload an actuals file to a deployment
          actuals report --input <> --actual-value-col <> --assoc-id-col <>

          # measure performance
          perf run --input <> --target-col <> --class-names <> --deployment-id <> --model-id <>
        """,
        )
        MLOpsCliArgParser._register_arg_version(parser)
        MLOpsCliArgParser._register_arg_verbose(parser)
        MLOpsCliArgParser._register_arg_quiet(parser)
        MLOpsCliArgParser._register_arg_json(parser)
        MLOpsCliArgParser._register_arg_terse(parser)

        MLOpsCliArgParser._register_arg_mlops_service(parser)
        MLOpsCliArgParser._register_arg_mlops_api_token(parser)
        MLOpsCliArgParser._register_arg_no_verify_ssl(parser)
        MLOpsCliArgParser._register_datarobot_app_version(parser)

        MLOpsCliArgParser._register_arg_subject(parser)
        MLOpsCliArgParser._register_arg_action(parser)

        MLOpsCliArgParser._parsers = parser

        # multi-use parameters
        MLOpsCliArgParser._register_arg_deployment_id(parser)
        MLOpsCliArgParser._register_arg_pe_id(parser)
        MLOpsCliArgParser._register_arg_monitoring_job_id(parser)
        MLOpsCliArgParser._register_arg_model_id(parser)
        MLOpsCliArgParser._register_arg_model_package_id(parser)
        MLOpsCliArgParser._register_target_col(parser)
        MLOpsCliArgParser._register_prediction_cols(parser)
        MLOpsCliArgParser._register_class_names(parser)
        MLOpsCliArgParser._register_dry_run(parser)
        MLOpsCliArgParser._register_status_file(parser)
        MLOpsCliArgParser._register_assoc_id_col(parser)
        MLOpsCliArgParser._register_arg_json_conf(parser)
        MLOpsCliArgParser._register_arg_dataset_id(parser)
        MLOpsCliArgParser._register_arg_timeout(parser)
        MLOpsCliArgParser._register_arg_search(parser)
        MLOpsCliArgParser._register_arg_limit(parser)
        MLOpsCliArgParser._register_arg_force(parser)
        MLOpsCliArgParser._register_timestamp_col(parser)
        MLOpsCliArgParser._register_value_col(parser)
        MLOpsCliArgParser._register_arg_enable_batch_monitoring(parser)
        MLOpsCliArgParser._register_arg_batch_id(parser)
        MLOpsCliArgParser._register_arg_service_stats(parser)
        MLOpsCliArgParser._register_arg_data_drift(parser)
        MLOpsCliArgParser._register_arg_metric_id(parser)
        MLOpsCliArgParser._register_arg_sampling_percentage(parser)

        MLOpsCliArgParser._add_perf_subcommand(parser)
        MLOpsCliArgParser._add_predictions_subcommand(parser)
        MLOpsCliArgParser._add_actuals_subcommand(parser)
        MLOpsCliArgParser._add_model_subcommand(parser)
        return parser


class MLOpsCSVSplitter:
    def __init__(self, filename, chunk_size, skip_rows=0):
        self.filename = filename
        self.chunk_size = chunk_size
        self.skip_rows = skip_rows
        # Because we want to skip 'n' rows, but still want to keep the header (as it contains the
        # column names), we skip rows from range 1 to that offset)
        self.headers = pd.read_csv(filename, nrows=1).columns.tolist()
        logger.info(f"Reading input data after skipping '{self.skip_rows}' rows")
        self.reader = pd.read_csv(
            filename, skiprows=range(1, self.skip_rows), chunksize=self.chunk_size
        )
        self._next_chunk = None
        self._current_row = self.skip_rows

    def get_columns(self):
        return self.headers

    def get_data_chunks(self):
        # Using generator pattern, especially because we are dealing with several GBs of files
        # This will limit the memory usage.
        for chunk in self.reader:
            self._current_row += self.chunk_size
            yield chunk

    def get_current_row(self):
        return self._current_row

    def get_chunk_size(self):
        return self.chunk_size

    def _get_next_chunk(self):
        self._next_chunk = next(self.reader, None)
        if self._next_chunk is not None:
            self._current_row += self.chunk_size

    def is_all_data_reported(self):
        if self._next_chunk is not None:
            return False
        self._get_next_chunk()
        return self._next_chunk is None

    def get_next_chunk_to_report(self):
        if self._next_chunk is None:
            self._get_next_chunk()
        if self._next_chunk is not None:
            chunk = self._next_chunk
            self._get_next_chunk()
            return chunk
        else:
            return None


class MLOpsCSVBatchSplitter(MLOpsCSVSplitter):
    # Batch Splitter can chop big, 100K
    BATCH_CHUNK_SIZE = 100 * 1000

    def __init__(self, filename, skip_rows=0):
        super().__init__(filename, self.BATCH_CHUNK_SIZE, skip_rows)


class MLOpsCSVJSONSplitter(MLOpsCSVSplitter):
    # JSON Post is 10k at a time
    JSON_CHUNK_SIZE = 10000

    def __init__(self, filename, skip_rows=0):
        super().__init__(filename, self.JSON_CHUNK_SIZE, skip_rows)


class MLOpsCli:
    def __init__(self, options):
        self.options = options
        # self.logger = CMRunner._config_logger(runtime.options)
        self.run_mode = RunMode(options.subject)
        self.raw_arguments = sys.argv
        self.csv_splitter = None
        self.status_tracker = None
        self.mclient = None

    def create_mclient(self):
        try:
            self.mclient = MLOpsClient(
                service_url=self.options.mlops_service_url,
                api_key=self.options.mlops_api_token,
                verify=self.options.verify_ssl,
                dry_run=self.options.dry_run,
                datarobot_app_version=self.options.datarobot_app_version,
            )
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)

    def delete_mclient(self):
        if self.mclient is not None:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.mclient.shutdown())

    async def _check_deployment_stats_perf(self):
        logger.info("\n\ndeployment stats performance:")
        start_time = time.time()
        request_num = self.options.count
        for _ in range(0, request_num):
            request_start_time = time.time()
            res = await self.mclient.report_deployment_stats(
                self.options.deployment_id,
                self.options.model_id,
                1,
                10,
                batch_id=self.options.batch_id,
            )
            request_end_time = time.time()
            request_elapsed_ms = (request_end_time - request_start_time) * 1000
            logger.info(f"request: {res} time {request_elapsed_ms:.1f}ms")

        end_time = time.time()
        elapsed_time = end_time - start_time
        per_request_ms = (elapsed_time * 1000.0) / request_num

        logger.info(
            "report deployment stats: total: {:.3f}sec sec, per request {:.2f}ms".format(
                elapsed_time, per_request_ms
            )
        )

    async def _check_prediction_data_perf(self):
        logger.info("prediction data performance:")
        start_time = time.time()
        request_num = self.options.count

        input_df = pd.read_csv(self.options.input)
        if self.options.rows > 0:
            input_df = input_df.head(self.options.rows)

        for _ in range(0, request_num):
            request_start_time = time.time()
            res, payload_size = await self.mclient.report_prediction_data(
                self.options.deployment_id,
                self.options.model_id,
                input_df,
                assoc_id_col=None,
                target_col=self.options.target_col,
                class_names=self.options.class_names,
                batch_id=self.options.batch_id,
            )
            request_end_time = time.time()
            request_elapsed_ms = (request_end_time - request_start_time) * 1000
            logger.info(
                "request: {} payload_size: {} time {:.1f}ms".format(
                    res, payload_size, request_elapsed_ms
                )
            )

        end_time = time.time()
        elapsed_time = end_time - start_time
        per_request_ms = (elapsed_time * 1000.0) / request_num

        logger.info(
            "prediction data: total: {:.3f}sec sec, per request {:.2f}ms".format(
                elapsed_time, per_request_ms
            )
        )

    async def _perf_run_async(self):
        await self._check_deployment_stats_perf()
        await self._check_prediction_data_perf()

    def perf_run(self):
        check_required_parameter(self.options.input, "INPUT", ArgumentsOptions.INPUT)
        check_required_parameter(
            self.options.deployment_id, EV.MLOPS_DEPLOYMENT_ID, ArgumentsOptions.DEPLOYMENT_ID
        )
        check_required_parameter(
            self.options.model_id, EV.MLOPS_MODEL_ID, ArgumentsOptions.MODEL_ID
        )
        check_required_parameter(self.options.target_col, None, ArgumentsOptions.TARGET_COL)
        check_required_parameter(self.options.class_names, None, ArgumentsOptions.CLASS_NAMES)

        self.create_mclient()
        logger.info("Running performance test:")
        logger.info(f"MLOps service: {self.options.mlops_service_url}")
        logger.info(f"Deployment ID: {self.options.deployment_id}")
        logger.info(f"Model ID:      {self.options.model_id}")
        logger.info(f"Target:        {self.options.target_col}")
        logger.info(f"Classes:       {self.options.class_names}")
        logger.info(f"Input:         {self.options.input}")
        logger.info(f"Count:         {self.options.count}")
        logger.info(f"Rows:          {self.options.rows}")
        logger.info(f"Batch ID:    {self.options.batch_id}")

        self.event_loop.run_until_complete(self._perf_run_async())
        self.delete_mclient()

    def _log_report_status(self, input_df, row_offset):
        logger.info("Reporting predictions:")
        logger.debug(f"MLOps service: {self.options.mlops_service_url}")
        logger.debug(f"Input:         {self.options.input}")
        logger.info(f"Input rows:     {len(input_df)}")
        logger.info(f"Input cols:     {len(input_df.columns)}")
        logger.info(f"Row Offset:     {row_offset}")
        logger.debug(f"Dry run:       {self.options.dry_run}")
        logger.debug(f"Status File:   {self.status_tracker.get_status_file()}")

    async def _report_predictions_connected_lib(self, input_df, row_offset):
        self._log_report_status(input_df, row_offset)

        request_start_time = time.time()
        res, payload_size = await self.mclient.report_prediction_data(
            self.options.deployment_id,
            self.options.model_id,
            input_df,
            assoc_id_col=self.options.assoc_id_col,
            target_col=self.options.target_col,
            prediction_cols=self.options.prediction_cols,
            class_names=self.options.class_names,
            batch_id=self.options.batch_id,
            dry_run=self.options.dry_run,
        )
        request_end_time = time.time()
        request_elapsed_ms = (request_end_time - request_start_time) * 1000

        await self.mclient.report_deployment_stats(
            self.options.deployment_id,
            self.options.model_id,
            len(input_df),
            self.options.prediction_time,
            dry_run=self.options.dry_run,
            batch_id=self.options.batch_id,
        )
        logger.debug(
            "Row offset: {} payload_size: {} time {:.1f}ms".format(
                row_offset, payload_size, request_elapsed_ms
            )
        )

    def _get_association_ids(self, input_df):
        # TODO: method never called...delete? otherwise, change print -> logger
        if self.options.assoc_id_col is None:
            print("No association ID column set")
            return None

        if self.options.assoc_id_col not in input_df.columns:
            raise Exception(
                "Association ID feature '{}' is not present in the input data".format(
                    self.options.assoc_id_col
                )
            )

        return input_df[self.options.assoc_id_col].tolist()

    def _report_predictions_async(self):
        self.event_loop.run_until_complete(self._data_dispatcher())

    async def _data_dispatcher(self):
        num_rows, iteration = self.status_tracker.get_status()
        tasks = list()
        for input_df_chunk in self.csv_splitter.get_data_chunks():
            tasks.append(
                asyncio.create_task(
                    self._report_predictions_connected_lib(input_df_chunk, num_rows)
                )
            )
            num_rows = self.csv_splitter.get_current_row()
            if len(tasks) == self.options.num_concurrent_requests:
                break

        while not self.csv_splitter.is_all_data_reported():
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                tasks.remove(task)
                # num_rows += task.result()
                # iteration += 1
                # self.status_tracker.update_status(num_rows, iteration)
                input_df_chunk = self.csv_splitter.get_next_chunk_to_report()
                if input_df_chunk is None:
                    continue
                num_rows = self.csv_splitter.get_current_row()
                new_task = asyncio.create_task(
                    self._report_predictions_connected_lib(input_df_chunk, num_rows)
                )
                tasks.append(new_task)
                logger.debug(
                    "Added new task to report rows from {} to {}".format(
                        num_rows, num_rows + self.csv_splitter.get_chunk_size()
                    )
                )

        # No more data to report, all tasks submitted, but let's wait for their completion
        logger.info("Done with submitting all tasks; waiting for them to finish now.")
        await asyncio.wait(tasks)
        logger.info("Done reporting all data.")

    async def _report_predictions_from_spooler(self, record, spooler):
        # the name of this method does not capture the fact that it supports reporting more than
        # just predictions; refactor/cleanup in AGENT-3322 will make this more clear
        data_type = record.get_data_type()
        payload = record.get_payload()
        request_start_time = time.time()
        if data_type == DataType.DEPLOYMENT_STATS:
            await self.mclient.report_deployment_stats(
                record.get_deployment_id(),
                payload[common_fields_keys.MODEL_ID_FIELD_NAME],
                payload[deployment_stats_keys.NUM_PREDICTIONS_FIELD_NAME],
                payload[deployment_stats_keys.EXECUTION_TIME_FIELD_NAME],
                payload[common_fields_keys.TIMESTAMP_FIELD_NAME],
                dry_run=self.options.dry_run,
                batch_id=payload.get(common_fields_keys.BATCH_ID_FIELD_NAME),
            )
        elif data_type == DataType.CUSTOM_METRIC:
            await self.mclient.report_custom_metrics(
                record.get_deployment_id(),
                payload.get(common_fields_keys.MODEL_ID_FIELD_NAME),
                payload[custom_metric_keys.METRIC_ID_FIELD_NAME],
                payload[custom_metric_keys.BUCKETS_FIELD_NAME],
            )
        elif data_type == DataType.PREDICTIONS_DATA:
            df, assoc_id, predictions, class_names = [None] * 4
            if predictions_data_keys.FEATURES_FIELD_NAME in payload:
                df = pd.DataFrame.from_dict(payload[predictions_data_keys.FEATURES_FIELD_NAME])
            if predictions_data_keys.ASSOCIATION_IDS_FIELD_NAME in payload:
                assoc_id = payload[predictions_data_keys.ASSOCIATION_IDS_FIELD_NAME]
            if predictions_data_keys.PREDICTIONS_FIELD_NAME in payload:
                predictions = payload[predictions_data_keys.PREDICTIONS_FIELD_NAME]
            if predictions_data_keys.CLASS_NAMES_FIELD_NAME in payload:
                class_names = payload[predictions_data_keys.CLASS_NAMES_FIELD_NAME]
            await self.mclient.report_prediction_data(
                record.get_deployment_id(),
                payload[common_fields_keys.MODEL_ID_FIELD_NAME],
                df,
                association_ids=assoc_id,
                predictions=predictions,
                class_names=class_names,
                timestamp=payload[common_fields_keys.TIMESTAMP_FIELD_NAME],
                skip_drift_tracking=payload.get(
                    predictions_data_keys.SKIP_DRIFT_TRACKING_FIELD_NAME, False
                ),
                skip_accuracy_tracking=payload.get(
                    predictions_data_keys.SKIP_ACCURACY_TRACKING_FIELD_NAME, False
                ),
                batch_id=payload.get(common_fields_keys.BATCH_ID_FIELD_NAME, None),
                dry_run=self.options.dry_run,
            )

            row_count = df.shape[0] if df is not None else len(predictions)
        elif data_type == DataType.ACTUALS_DATA:
            await self.mclient.report_actuals_data(
                record.get_deployment_id(),
                payload[Constants.ACTUALS_LIST_KEY],
                dry_run=self.options.dry_run,
            )
        elif data_type == DataType.PREDICTION_STATS:
            await self.mclient.report_aggregated_prediction_data(
                record.get_deployment_id(),
                payload[common_fields_keys.MODEL_ID_FIELD_NAME],
                payload=payload,
                batch_id=payload.get(common_fields_keys.BATCH_ID_FIELD_NAME, None),
                dry_run=self.options.dry_run,
            )
        elif data_type == DataType.PING_MSG:
            # ping message are used by agent to check spooler enqueue/dequeue ability
            logger.debug("Read ping message ignoring..")
        else:
            logger.warn(f"Connected client does not handle data type: '{data_type.name}'")

        if spooler.enable_dequeue_ack_record:
            spooler.ack_records([record.get_id()])

        request_end_time = time.time()
        request_elapsed_ms = (request_end_time - request_start_time) * 1000
        if data_type == DataType.DEPLOYMENT_STATS:
            logger.debug(
                "Reporting stats predictions: {} execution time: {}".format(
                    payload[deployment_stats_keys.NUM_PREDICTIONS_FIELD_NAME],
                    payload[deployment_stats_keys.EXECUTION_TIME_FIELD_NAME],
                )
            )
        elif data_type == DataType.PREDICTIONS_DATA:
            logger.debug(f"Reporting feature data, row count: {row_count}")
        logger.debug(f"Reporting latency: {request_elapsed_ms:.1f}ms")

    def report_predictions_from_spool(self):
        self.create_mclient()
        try:
            spooler_type = config.get_config_default(
                config.ConfigConstants.SPOOLER_TYPE, SpoolerType.FILESYSTEM.name
            )
            # Set max number of request per dequeue call, to number of concurrent request
            config.set_config(
                config.ConfigConstants.SPOOLER_DEQUEUE_MAX_RECORDS_PER_CALL,
                self.options.num_concurrent_requests,
            )
            spooler = RecordSpoolerFactory().create(SpoolerType[spooler_type])
            spooler.set_config()
            spooler.open(action=MLOpsSpoolAction.DEQUEUE)

            # Some exceptions (like KeyboardInterrupt) don't work as expected inside the
            # event-loop so setup the spooler here and make sure it gets closed.
            with closing(spooler):
                self.event_loop.run_until_complete(self._spool_data_dispatcher(spooler))
        finally:
            self.delete_mclient()

    async def _spool_data_dispatcher(self, spooler):
        tasks = list()
        total_records = 0
        failed_records = 0
        log_interval_sec = 180
        start_time = time.time()
        next_log_time = start_time + log_interval_sec

        while not spooler.empty():
            record_list = spooler.dequeue()
            total_records += len(record_list)
            for record in record_list:
                tasks.append(
                    asyncio.create_task(self._report_predictions_from_spooler(record, spooler))
                )
            if len(tasks) == self.options.num_concurrent_requests:
                break

        while not spooler.empty() and tasks:
            done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                if task.exception():
                    failed_records += 1
                    logger.error(f"Failed to process task: {task.exception()}")
                tasks.remove(task)
                record_list = spooler.dequeue()
                total_records += len(record_list)
                for record in record_list:
                    new_task = asyncio.create_task(
                        self._report_predictions_from_spooler(record, spooler)
                    )
                    tasks.append(new_task)
            if time.time() >= next_log_time:  # log updated metrics every couple of minutes
                elapsed = time.time() - start_time
                logger.info("Records processed so far: %s", total_records)
                logger.info("Current Throughput: %.02f (records/s)", total_records / elapsed)
                next_log_time = time.time() + log_interval_sec

        runtime = time.time() - start_time
        logger.info("Runtime: %.02f minutes", runtime / 60)
        logger.info("Total failed records: %s", failed_records)
        logger.info("Total records processed: %s", total_records)
        logger.info("Overall Throughput: %.02f (records/s)", total_records / runtime)
        # No more data to report, all tasks submitted, but let's wait for their completion
        logger.info("Done with submitting all tasks; waiting for them to finish now.")

        if tasks:
            await asyncio.wait(tasks)
        logger.info("Done reporting all data.")

    def _check_columns(self, columns):
        if self.options.prediction_cols is not None:
            for prediction_col in self.options.prediction_cols:
                if prediction_col not in columns:
                    raise DRCommonException(
                        f"Prediction column {prediction_col} not found in input file."
                    )
            if self.options.class_names is not None:
                if len(self.options.class_names) != len(self.options.prediction_cols):
                    raise DRCommonException(
                        "The number of class names and prediction columns must match."
                    )
        if self.options.target_col is not None:
            if self.options.target_col not in columns:
                raise DRCommonException(
                    f"Target column {self.options.target_col} not found in input file."
                )
        if self.options.assoc_id_col is not None:
            if self.options.assoc_id_col not in columns:
                raise DRCommonException(
                    "Association ID column {} not found in input file.".format(
                        self.options.assoc_id_col
                    )
                )

    def report_predictions(self):
        check_required_parameter(self.options.input, None, ArgumentsOptions.INPUT)
        check_required_parameter(
            self.options.deployment_id, EV.MLOPS_DEPLOYMENT_ID, ArgumentsOptions.DEPLOYMENT_ID
        )
        check_required_parameter(
            self.options.model_id, EV.MLOPS_MODEL_ID, ArgumentsOptions.MODEL_ID
        )

        logger.debug("Reporting predictions:")
        logger.debug(f"MLOps service:         {self.options.mlops_service_url}")
        logger.debug(f"Input:                 {self.options.input}")
        logger.debug(f"Target column:         {self.options.target_col}")
        logger.debug(f"Prediction column(s):  {self.options.prediction_cols}")
        logger.debug(f"Classes:               {self.options.class_names}")
        logger.debug(f"Assoc Id column:       {self.options.assoc_id_col}")
        logger.debug(f"Dry run:               {self.options.dry_run}")

        if self.options.status_file:
            self.status_tracker = MLOpsUploadTracker(self.options.status_file)
        else:
            self.status_tracker = MLOpsUploadTracker()
        skip_rows, _ = self.status_tracker.get_status()
        try:
            self.csv_splitter = MLOpsCSVJSONSplitter(self.options.input, skip_rows=skip_rows)
            self._check_columns(self.csv_splitter.get_columns())
        except (pd.errors.EmptyDataError, DRCommonException) as e:
            self._log_error_and_exit(e, ExitCode.DEFAULT.value)

        try:
            self.create_mclient()
            self._report_predictions_async()
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def get_prediction_stats(self):
        """
        Uses the predictionsOverTime API to get statistics broken out by
        prediction value, time bucket, and more.
        This API requires the Experimental API flag.
        For that reason, "mlops-cli predictions get" is deprecated.
        To count recent predictions, use "mlops-cli predictions count".
        """
        check_required_parameter(
            self.options.deployment_id, EV.MLOPS_DEPLOYMENT_ID, ArgumentsOptions.DEPLOYMENT_ID
        )
        self.create_mclient()
        self._log_get_action("deployment", self.options.deployment_id, "prediction stats")
        try:
            stats = self.mclient.get_prediction_stats(
                self.options.deployment_id, self.options.model_id
            )
            self._print_resource_received(self.options.deployment_id, stats)
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def count_predictions(self):
        """
        Uses the targetDrift API to get the number of predictions processed in past 7 days.
        (The predictionsOverTime API requires Experimental API access, while targetDrift does not.)
        """
        check_required_parameter(
            self.options.deployment_id, EV.MLOPS_DEPLOYMENT_ID, ArgumentsOptions.DEPLOYMENT_ID
        )
        self.create_mclient()
        self._log_get_action("deployment", self.options.deployment_id, "target drift")
        try:
            drift = self.mclient.get_target_drift(self.options.deployment_id, self.options.model_id)
            stats = {"predictionsCount": drift.get("sampleSize", None)}
            self._print_resource_received(self.options.deployment_id, stats)
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def get_service_stats(self):
        check_required_parameter(
            self.options.deployment_id, EV.MLOPS_DEPLOYMENT_ID, ArgumentsOptions.DEPLOYMENT_ID
        )
        self.create_mclient()
        if self.options.model_id is None:
            self._log_get_action("deployment", self.options.deployment_id, "service stats")
        else:
            self._log_get_action(
                "deployment",
                self.options.deployment_id,
                f"service stats for model ID {self.options.model_id}",
            )
        try:
            stats = self.mclient.get_service_stats(
                self.options.deployment_id, self.options.model_id
            )
            self._print_resource_received(self.options.deployment_id, stats)
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    async def _report_actuals_connected_lib(self, input_df, row_offset):
        self._log_report_status(input_df, row_offset)

        reporting_df = input_df
        if self.options.sampling_percentage > 0.0:
            reporting_df = sample_dataframe(
                input_df, self.options.assoc_id_col, self.options.sampling_percentage
            )
            if reporting_df.empty:
                logger.debug(f"No rows sampled at offset {row_offset}")
                return

        request_start_time = time.time()
        res, payload_size = await self.mclient.submit_actuals_from_dataframe(
            self.options.deployment_id,
            reporting_df,
            assoc_id_col=self.options.assoc_id_col,
            actual_value_col=self.options.actual_value_col,
            was_act_on_col=self.options.acted_on_col,
            timestamp_col=self.options.timestamp_col,
            dry_run=self.options.dry_run,
        )
        request_end_time = time.time()
        request_elapsed_ms = (request_end_time - request_start_time) * 1000

        logger.debug(
            "Row offset: {} payload_size: {} time {:.1f}ms".format(
                row_offset, payload_size, request_elapsed_ms
            )
        )

    def _check_actuals_columns(self, actuals_columns):
        if self.options.actual_value_col not in actuals_columns:
            raise DRCommonException(
                f"Actuals value column {self.options.actual_value_col} missing in the dataframe"
            )

        if self.options.assoc_id_col not in actuals_columns:
            raise DRCommonException(
                f"Association ID column {self.options.assoc_id_col} missing in the dataframe"
            )

    def _report_actuals_async(self):
        self.event_loop.run_until_complete(self._actuals_dispatcher())

    async def _actuals_dispatcher(self):
        num_rows, iteration = self.status_tracker.get_status()
        tasks = list()
        for input_df_chunk in self.csv_splitter.get_data_chunks():
            tasks.append(
                asyncio.create_task(self._report_actuals_connected_lib(input_df_chunk, num_rows))
            )
            num_rows = self.csv_splitter.get_current_row()
            if len(tasks) == self.options.num_concurrent_requests:
                break

        while not self.csv_splitter.is_all_data_reported():
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                tasks.remove(task)
                input_df_chunk = self.csv_splitter.get_next_chunk_to_report()
                if input_df_chunk is None:
                    continue
                num_rows = self.csv_splitter.get_current_row()
                new_task = asyncio.create_task(
                    self._report_actuals_connected_lib(input_df_chunk, num_rows)
                )
                tasks.append(new_task)
                logger.debug(
                    "Added new task to report actuals from {} to {}".format(
                        num_rows, num_rows + self.csv_splitter.get_chunk_size()
                    )
                )

        # No more data to report, all tasks submitted, but let's wait for their completion
        logger.info("Done with submitting all tasks; waiting for them to finish now.")
        await asyncio.wait(tasks)
        logger.info("Done reporting all actuals.")

    def _validate_sampling_percentage(self):
        if not isinstance(self.options.sampling_percentage, numbers.Number):
            raise Exception(
                f"Auto sampling percentage {self.options.sampling_percentage} is not float or int"
            )
        self.options.sampling_percentage = float(self.options.sampling_percentage)
        if not 0.0 <= self.options.sampling_percentage <= 100.0:
            raise Exception(
                f"Invalid value for auto sampling percentage {self.options.sampling_percentage}."
                "  Value should be between 0 to 100"
            )

    def report_actuals(self):
        check_required_parameter(self.options.deployment_id, None, ArgumentsOptions.DEPLOYMENT_ID)
        check_required_parameter(self.options.input, None, ArgumentsOptions.INPUT)
        check_required_parameter(
            self.options.actual_value_col, None, ArgumentsOptions.ACTUAL_VALUE_COL
        )
        check_required_parameter(
            self.options.assoc_id_col,
            EV.MLOPS_ASSOCIATION_ID_COLUMN_NAME,
            ArgumentsOptions.ASSOC_ID,
        )
        self._validate_sampling_percentage()

        logger.info("Reporting actuals:")
        logger.info(f"MLOps service:         {self.options.mlops_service_url}")
        logger.info(f"Deployment ID:         {self.options.deployment_id}")
        logger.info(f"Input:                 {self.options.input}")
        logger.info(f"Actual value column:   {self.options.actual_value_col}")
        logger.info(f"Assoc ID column:       {self.options.assoc_id_col}")
        logger.info(f"Was-acted-on column:   {self.options.acted_on_col}")
        logger.info(f"Timestamp column:      {self.options.timestamp_col}")
        logger.info(f"Sampling Percentage:   {self.options.sampling_percentage}")

        if self.options.status_file:
            self.status_tracker = MLOpsUploadTracker(self.options.status_file)
        else:
            self.status_tracker = MLOpsUploadTracker()
        skip_rows, _ = self.status_tracker.get_status()
        try:
            self.csv_splitter = MLOpsCSVJSONSplitter(self.options.input, skip_rows=skip_rows)
            self._check_actuals_columns(self.csv_splitter.get_columns())
        except (pd.errors.EmptyDataError, DRCommonException) as e:
            self._log_error_and_exit(e, ExitCode.DEFAULT.value)

        try:
            self.create_mclient()
            self._report_actuals_async()
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def count_actuals(self):
        check_required_parameter(
            self.options.deployment_id, EV.MLOPS_DEPLOYMENT_ID, ArgumentsOptions.DEPLOYMENT_ID
        )
        self.create_mclient()
        self._log_get_action("deployment", self.options.deployment_id, "accuracy")
        try:
            accuracy = self.mclient.get_predictions_and_actuals_stats(
                self.options.deployment_id, self.options.model_id
            )
            stats = {"actuals": accuracy["summary"]["rowCountWithActual"]}
            self._print_resource_received(self.options.deployment_id, stats)
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def _generate_temp_csv_filename(self, iteration):
        prefix = "/tmp/" + os.path.basename(self.options.input).replace(".csv", "")
        return prefix + str(iteration) + ".csv"

    async def _upload_scoring_dataset_batch(self, input_df, row_offset, iteration):
        """Upload a scoring dataset and associate it with a deployment."""
        # This is just the filename generated and issued for display in "AI Catalog"; there is no
        # actual file written to disk.  Dataframe is streamed to the MLOps in CSV format.
        csv_file_name = self._generate_temp_csv_filename(iteration)
        logger.info("Set scoring dataset:")
        logger.debug(f"MLOps service: {self.options.mlops_service_url}")
        logger.info(f"Deployment ID:  {self.options.deployment_id}")
        logger.info(f"Model ID:       {self.options.model_id}")
        logger.info(f"Target:         {self.options.target_col}")
        logger.info(f"Prediction column(s):  {self.options.prediction_cols}")
        logger.info(f"Classes:        {self.options.class_names}")
        logger.debug(f"Input:         {self.options.input}")
        logger.info(f"Input rows:     {len(input_df)}")
        logger.info(f"Input cols:     {len(input_df.columns)}")
        logger.info(f"Row Offset:     {row_offset}")
        logger.debug(f"Dry run:       {self.options.dry_run}")
        logger.debug(f"Status File:   {self.status_tracker.get_status_file()}")
        logger.debug(f"CSV FileName:  {csv_file_name}")

        if len(input_df) < 1:
            logger.debug("All rows already uploaded.")
            return

        request_start_time = time.time()
        dataset_id = self.mclient.upload_dataframe(
            input_df, csv_file_name, dry_run=self.options.dry_run
        )
        request_end_time = time.time()
        request_elapsed_ms = (request_end_time - request_start_time) * 1000
        logger.debug(f"Upload done: time {request_elapsed_ms:.1f}ms")

        request_start_time = time.time()
        self.mclient.associate_deployment_dataset(
            self.options.deployment_id,
            dataset_id,
            DatasetSourceType.SCORING,
            dry_run=self.options.dry_run,
        )
        request_end_time = time.time()
        request_elapsed_ms = (request_end_time - request_start_time) * 1000
        logger.debug(f"Association done: time {request_elapsed_ms:.1f}ms")

        # Remove the dataset after association is done
        self.mclient.soft_delete_dataset(dataset_id)

        request_start_time = time.time()
        res, payload_size = await self.mclient.report_prediction_data(
            self.options.deployment_id,
            self.options.model_id,
            input_df,
            target_col=self.options.target_col,
            prediction_cols=self.options.prediction_cols,
            class_names=self.options.class_names,
            batch_id=self.options.batch_id,
            dry_run=self.options.dry_run,
        )
        request_end_time = time.time()
        request_elapsed_ms = (request_end_time - request_start_time) * 1000
        logger.debug(
            "request: {} payload_size: {} time {:.1f}ms".format(
                res, payload_size, request_elapsed_ms
            )
        )

    async def _upload_scoring_dataset_async(self):
        if self.options.status_file:
            self.status_tracker = MLOpsUploadTracker(self.options.status_file)
        else:
            self.status_tracker = MLOpsUploadTracker()
        skip_rows, iteration = self.status_tracker.get_status()
        csv_splitter = MLOpsCSVBatchSplitter(self.options.input, skip_rows=skip_rows)
        num_rows = skip_rows
        for input_df_chunk in csv_splitter.get_data_chunks():
            await self._upload_scoring_dataset_batch(input_df_chunk, num_rows, iteration)
            num_rows += input_df_chunk.shape[0]
            self.status_tracker.update_status(num_rows, iteration)
            iteration += 1

    def upload_scoring_dataset(self):
        check_required_parameter(
            self.options.deployment_id, EV.MLOPS_DEPLOYMENT_ID, ArgumentsOptions.DEPLOYMENT_ID
        )
        check_required_parameter(
            self.options.model_id, EV.MLOPS_MODEL_ID, ArgumentsOptions.MODEL_ID
        )
        check_required_parameter(self.options.input, "INPUT", ArgumentsOptions.INPUT)
        self.create_mclient()
        try:
            self.event_loop.run_until_complete(self._upload_scoring_dataset_async())
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def upload_dataset(self):
        check_required_parameter(self.options.input, None, ArgumentsOptions.INPUT)
        self.create_mclient()
        dataset = self.options.input
        logger.info(f"Uploading dataset - {dataset}. This may take some time...")
        try:
            if self.options.timeout:
                dataset_id = self.mclient.upload_dataset(dataset, timeout=self.options.timeout)
            else:
                dataset_id = self.mclient.upload_dataset(dataset)
            self._print_resource_generic_action(dataset_id)
            logger.info(f"Dataset uploaded. Dataset ID {dataset_id}.")
        except Exception as e:
            feature_drift_error_message = (
                "Dataset upload failed. You won't see Feature Drift reports in UI."
            )
            logger.error(feature_drift_error_message)
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED)
        finally:
            self.delete_mclient()

    def get_dataset(self):
        check_required_parameter(
            self.options.dataset_id, EV.MLOPS_DATASET_ID, ArgumentsOptions.DATASET_ID
        )
        self.create_mclient()
        self._log_get_action("dataset", self.options.dataset_id)
        try:
            info = self.mclient.get_dataset(self.options.dataset_id)
            self._print_resource_received(self.options.dataset_id, info)
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def list_datasets(self):
        self.create_mclient()
        self._log_list_action("dataset")
        params = None
        # TODO: using any limit seems to return 0 results
        if self.options.limit:
            params = {"limit": self.options.limit}

        try:
            all_results = self.mclient.list_datasets(params)
            # datasets don't have a name filter, so do that here
            if self.options.search:
                filtered_results = []
                for result in all_results:
                    if self.options.search in result.get("name"):
                        filtered_results.append(result)
            else:
                filtered_results = all_results
            self._print_resources_listed(filtered_results, "datasetId")
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def delete_dataset(self):
        check_required_parameter(self.options.dataset_id, None, ArgumentsOptions.DATASET_ID)
        self.create_mclient()
        self._log_delete_action("dataset", self.options.dataset_id)
        try:
            self.mclient.soft_delete_dataset(self.options.dataset_id)
            self._print_resource_generic_action(self.options.dataset_id)
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def download_model_package(self):
        check_required_parameter(
            self.options.deployment_id, "MLOPS_DEPLOYMENT_ID", ArgumentsOptions.DEPLOYMENT_ID
        )

        self.create_mclient()
        logger.debug("Downloading current model package:")
        logger.debug(f"MLOps service:          {self.options.mlops_service_url}")
        logger.debug(f"Deployment ID:          {self.options.deployment_id}")
        logger.debug(f"Output directory:       {self.options.output_dir}")

        mlpkg_path = self.mclient.download_dr_current_model_package(
            self.options.deployment_id,
            self.options.output_dir,
            download_scoring_code=self.options.download_scoring_code,
        )

        logger.debug(f"Model Package path     {mlpkg_path}")

        self.delete_mclient()

    def download_model_package_from_registry(self):
        check_required_parameter(
            self.options.model_package_id,
            EV.MLOPS_MODEL_PACKAGE_ID,
            ArgumentsOptions.MODEL_PACKAGE_ID,
        )
        logger.debug("Downloading model package from registry:")
        logger.debug(f"MLOps service:          {self.options.mlops_service_url}")
        logger.debug(f"Model package ID:          {self.options.model_package_id}")
        logger.debug(f"Output directory:       {self.options.output_dir}")

        self.create_mclient()
        self._log_get_action("model package", self.options.model_package_id)
        scoring_code_path = self.mclient.download_model_package_from_registry(
            self.options.model_package_id,
            self.options.output_dir,
            download_scoring_code=self.options.download_scoring_code,
        )
        logger.debug(f"Model package path:     {scoring_code_path}")

    def get_features_from_model_package(self):
        check_required_parameter(
            self.options.model_package_id,
            EV.MLOPS_MODEL_PACKAGE_ID,
            ArgumentsOptions.MODEL_PACKAGE_ID,
        )
        self.create_mclient()
        self._log_get_action("model package", self.options.model_package_id)
        try:
            info = self.mclient.get_features_from_model_package(
                self.options.model_package_id, params={"offset": 0, "limit": 0}
            )
            feature_types = [AggregationHelper.convert_feature_format(f) for f in info]

            if self.options.output_file:
                with open(self.options.output_file, "w") as f:
                    json.dump(feature_types, f)

            self._print_resource_received(self.options.model_package_id, feature_types)
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def get_model_package(self):
        check_required_parameter(
            self.options.model_package_id,
            EV.MLOPS_MODEL_PACKAGE_ID,
            ArgumentsOptions.MODEL_PACKAGE_ID,
        )
        self.create_mclient()
        self._log_get_action("model package", self.options.model_package_id)
        try:
            info = self.mclient.get_model_package(self.options.model_package_id)
            self._print_resource_received(self.options.model_package_id, info)
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def list_model_packages(self):
        self.create_mclient()
        self._log_list_action("model package")
        try:
            info = self.mclient.list_model_packages(self.get_list_params())
            self._print_resources_listed(info)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def delete_model_package(self):
        check_required_parameter(
            self.options.model_package_id,
            EV.MLOPS_MODEL_PACKAGE_ID,
            ArgumentsOptions.MODEL_PACKAGE_ID,
        )
        self.create_mclient()
        self._log_delete_action("model package", self.options.model_package_id)
        try:
            # until we support a real delete, we just archive.
            self.mclient.archive_model_package(self.options.model_package_id)
            self._print_resource_generic_action(self.options.model_package_id)
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def _read_json_config(self, config_file):
        config_path = os.path.abspath(config_file)
        try:
            with open(config_path) as f:
                info = json.loads(f.read())
        except FileNotFoundError as e:
            # Effectively, remove the '[Errno 2]' portion of the default FileNotFoundError message
            # so as to not confuse the user, since we exit with a custom error number from ExitCode
            raise FileNotFoundError(f"No such file or directory: {e.filename}")
        return info

    def create_model_package(self):
        check_required_parameter(self.options.json_config, None, ArgumentsOptions.JSON_CONF)
        self.create_mclient()
        logger.info("Creating model package:")
        logger.debug(f"MLOps service:         {self.options.mlops_service_url}")
        logger.info(f"Model config:           {self.options.json_config}")

        try:
            model_info = self._read_json_config(self.options.json_config)
        except FileNotFoundError as e:
            self._log_error_and_exit(e, ExitCode.FILE_NOT_FOUND.value)
        if self.options.model_id is not None:
            model_info["modelId"] = self.options.model_id
            logger.debug(f"Model ID:              {self.options.model_id}")

        # if specified, add training_data to model configuration
        if (
            self.options.training_dataset_id is not None
            or self.options.holdout_dataset_id is not None
        ):
            datasets = {}
            if self.options.training_dataset_id is not None:
                datasets["trainingDataCatalogId"] = self.options.training_dataset_id
                logger.debug(f"Training dataset ID:   {self.options.training_dataset_id}")
            if self.options.holdout_dataset_id is not None:
                datasets["holdoutDataCatalogId"] = self.options.holdout_dataset_id
                logger.debug(f"Holdout dataset ID:    {self.options.holdout_dataset_id}")
            model_info["datasets"] = datasets
        try:
            model_pkg_id = self.mclient.create_model_package(model_info)
            self._print_resource_generic_action(model_pkg_id)
            logger.info(f"Created model package ID {model_pkg_id}.")
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def deploy_model_package(self):
        check_required_parameter(
            self.options.model_package_id,
            EV.MLOPS_MODEL_PACKAGE_ID,
            ArgumentsOptions.MODEL_PACKAGE_ID,
        )
        self.create_mclient()
        logger.info("Deploying model package to prediction environment. This may take some time...")
        logger.debug(f"MLOps service:            {self.options.mlops_service_url}")
        logger.info(f"Model package ID:          {self.options.model_package_id}")
        logger.info(f"Deployment label:          {self.options.deployment_label}")
        logger.info(f"Prediction Environment ID: {self.options.prediction_environment_id}")
        logger.info(f"Timestamp column name:     {self.options.timestamp_col}")
        logger.info(f"Timestamp format:          {self.options.timestamp_format}")
        logger.info(f"Enable Batch Monitoring:   {self.options.enable_batch_monitoring}")
        if self.options.segment_attributes:
            logger.info(f"Segment attributes:        {self.options.segment_attributes}")

        try:
            deployment_id = self.mclient.deploy_model_package(
                self.options.model_package_id,
                self.options.deployment_label,
                prediction_environment_id=self.options.prediction_environment_id,
            )
            self._print_resource_generic_action(deployment_id)
            logger.info(f"Model package deployed. Deployment ID {deployment_id}.")

            logger.info(f"Updating deployment settings for deployment ID {deployment_id}.")
            self.mclient.update_deployment_settings(
                deployment_id,
                target_drift=True,
                feature_drift=True,
                segment_attributes=self.options.segment_attributes,
                timeout=600,
                timestamp_col_name=self.options.timestamp_col,
                timestamp_format=self.options.timestamp_format,
                batch_monitoring=self.options.enable_batch_monitoring,
            )
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def replace_model_package(self):
        check_required_parameter(
            self.options.deployment_id, EV.MLOPS_DEPLOYMENT_ID, ArgumentsOptions.DEPLOYMENT_ID
        )
        check_required_parameter(
            self.options.model_package_id,
            EV.MLOPS_MODEL_PACKAGE_ID,
            ArgumentsOptions.MODEL_PACKAGE_ID,
        )
        self.create_mclient()
        logger.info("Replacing model package in a deployment:")
        logger.debug(f"MLOps service:        {self.options.mlops_service_url}")
        logger.info(f"Model package ID:      {self.options.model_package_id}")
        logger.info(f"Deployment ID:         {self.options.deployment_id}")
        logger.info(f"Reason:                {self.options.reason}")
        try:
            self.mclient.replace_model_package(
                self.options.deployment_id, self.options.model_package_id, self.options.reason
            )
            logger.debug(f"Model package replaced on deployment {self.options.deployment_id}")
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def delete_deployment(self):
        check_required_parameter(
            self.options.deployment_id, EV.MLOPS_DEPLOYMENT_ID, ArgumentsOptions.DEPLOYMENT_ID
        )
        self.create_mclient()
        if self.options.force:
            logger.info("Force-deleting resource (ignoring management agent):")
        self._log_delete_action("deployment", self.options.deployment_id)
        try:
            self.mclient.delete_deployment(
                self.options.deployment_id, self.options.wait, self.options.force
            )
            self._print_resource_generic_action(self.options.deployment_id)
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def get_deployment(self):
        check_required_parameter(
            self.options.deployment_id, EV.MLOPS_DEPLOYMENT_ID, ArgumentsOptions.DEPLOYMENT_ID
        )
        self.create_mclient()
        self._log_get_action("deployment", self.options.deployment_id)
        try:
            info = self.mclient.get_deployment(self.options.deployment_id)
            if self.options.action == Actions.GET_MODEL:
                model_id = info["model"]["id"]
                self._print_resource_received(model_id, info)
            else:
                self._print_resource_received(self.options.deployment_id, info)
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def list_deployments(self):
        self.create_mclient()
        self._log_list_action("deployment")
        try:
            info = self.mclient.list_deployments(self.get_list_params())
            self._print_resources_listed(info)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def create_prediction_environment(self):
        check_required_parameter(self.options.json_config, None, ArgumentsOptions.JSON_CONF)
        try:
            info = self._read_json_config(self.options.json_config)
        except FileNotFoundError as e:
            self._log_error_and_exit(e, ExitCode.FILE_NOT_FOUND.value)
        self.create_mclient()
        try:
            pe_id = self.mclient.create_prediction_environment(info)
            self._print_resource_generic_action(pe_id)
            logger.info(f"Created prediction environment ID {pe_id}.")
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def get_prediction_environment(self):
        check_required_parameter(
            self.options.prediction_environment_id,
            EV.MLOPS_PREDICTION_ENVIRONMENT_ID,
            ArgumentsOptions.PREDICTION_ENVIRONMENT_ID,
        )
        self.create_mclient()
        self._log_get_action("prediction environment", self.options.prediction_environment_id)
        try:
            info = self.mclient.get_prediction_environment(self.options.prediction_environment_id)
            self._print_resource_received(self.options.prediction_environment_id, info)
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def list_prediction_environments(self):
        self.create_mclient()
        self._log_list_action("prediction environment")
        try:
            info = self.mclient.list_prediction_environments(self.get_list_params())
            self._print_resources_listed(info)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def delete_prediction_environment(self):
        check_required_parameter(
            self.options.prediction_environment_id,
            EV.MLOPS_PREDICTION_ENVIRONMENT_ID,
            ArgumentsOptions.PREDICTION_ENVIRONMENT_ID,
        )
        self.create_mclient()
        self._log_delete_action("prediction environment", self.options.prediction_environment_id)
        try:
            self.mclient.delete_prediction_environment(self.options.prediction_environment_id)
            self._print_resource_generic_action(self.options.prediction_environment_id)
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def restart_monitoring_agent(self):
        check_required_parameter(
            self.options.prediction_environment_id,
            EV.MLOPS_PREDICTION_ENVIRONMENT_ID,
            ArgumentsOptions.PREDICTION_ENVIRONMENT_ID,
        )
        self.create_mclient()
        try:
            self.mclient.restart_monitoring_agent(
                self.options.prediction_environment_id, self.options.wait, self.options.timeout
            )
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def restart_management_agent(self):
        check_required_parameter(
            self.options.prediction_environment_id,
            EV.MLOPS_PREDICTION_ENVIRONMENT_ID,
            ArgumentsOptions.PREDICTION_ENVIRONMENT_ID,
        )
        self.create_mclient()
        try:
            self.mclient.restart_management_agent(
                self.options.prediction_environment_id, self.options.wait, self.options.timeout
            )
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def create_monitoring_job(self):
        check_required_parameter(self.options.json_config, None, ArgumentsOptions.JSON_CONF)
        try:
            info = self._read_json_config(self.options.json_config)
            if self.options.deployment_id:
                # if deployment id is provided, use it to create the monitoring job
                info["deploymentId"] = self.options.deployment_id

            self.create_mclient()
            job_id = self.mclient.create_monitoring_job(info)
            self._print_resource_generic_action(job_id)
            logger.info(f"Created monitoring job ID {job_id}.")
        except FileNotFoundError as e:
            self._log_error_and_exit(e, ExitCode.FILE_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def get_monitoring_job(self):
        check_required_parameter(
            self.options.monitoring_job_id,
            EV.MLOPS_MONITORING_JOB_ID,
            ArgumentsOptions.MONITORING_JOB_ID,
        )
        self.create_mclient()
        self._log_get_action("monitoring job", self.options.monitoring_job_id)
        try:
            info = self.mclient.get_monitoring_job(self.options.monitoring_job_id)
            self._print_resource_received(self.options.monitoring_job_id, info)
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def abort_running_monitoring_job(self):
        check_required_parameter(
            self.options.monitoring_job_id,
            EV.MLOPS_MONITORING_JOB_ID,
            ArgumentsOptions.MONITORING_JOB_ID,
        )
        self.create_mclient()
        self._log_delete_action("monitoring job", self.options.monitoring_job_id)
        try:
            self.mclient.abort_running_monitoring_job(self.options.monitoring_job_id)
            self._print_resource_generic_action(self.options.monitoring_job_id)
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def upload_input_file_to_monitoring_job(self):
        check_required_parameter(
            self.options.monitoring_job_id,
            EV.MLOPS_MONITORING_JOB_ID,
            ArgumentsOptions.MONITORING_JOB_ID,
        )
        check_required_parameter(self.options.input, None, ArgumentsOptions.INPUT)

        self.create_mclient()
        logger.info(f"Uploading data - {self.options.input}.")
        try:
            self.mclient.upload_input_file_to_monitoring_job(
                self.options.monitoring_job_id, self.options.input
            )
            logger.info("Dataset uploaded.")
        except Exception as e:
            logger.error("Dataset upload failed.")
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED)
        finally:
            self.delete_mclient()

    @staticmethod
    def _print_supported_actions(subject):
        actions = SUPPORTED_ACTIONS[subject]
        if len(actions) == 1:
            print(f"Supported {subject} action is: {actions[0]}")
        else:
            print("Supported {} actions are: {}".format(subject, ", ".join(actions)))
        raise SystemExit(ExitCode.INVALID_CLI_INPUT.value)

    def handle_predictions(self):
        if self.options.action == Actions.GET:
            self.get_prediction_stats()
        elif self.options.action == Actions.COUNT:
            self.count_predictions()
        elif self.options.action == Actions.UPLOAD:
            self.upload_scoring_dataset()
        elif self.options.action == Actions.REPORT:
            if self.options.from_spool:
                self.report_predictions_from_spool()
            else:
                self.report_predictions()
        else:
            self._print_supported_actions(Subjects.PREDICTIONS)

    def handle_model(self):
        if self.options.action == Actions.CREATE:
            self.create_model_package()
        elif self.options.action == Actions.DEPLOY:
            self.deploy_model_package()
        elif self.options.action == Actions.REPLACE:
            self.replace_model_package()
        elif self.options.action == Actions.GET:
            self.get_model_package()
        elif self.options.action == Actions.FEATURES:
            self.get_features_from_model_package()
        elif self.options.action == Actions.LIST:
            self.list_model_packages()
        elif self.options.action == Actions.DOWNLOAD:
            if self.options.deployment_id:
                self.download_model_package()
            else:
                self.download_model_package_from_registry()
        elif self.options.action == Actions.DELETE:
            self.delete_model_package()
        else:
            self._print_supported_actions(Subjects.MODEL)

    def handle_deployment(self):
        if self.options.action == Actions.DELETE:
            self.delete_deployment()
        elif self.options.action == Actions.GET or self.options.action == Actions.GET_MODEL:
            self.get_deployment()
        elif self.options.action == Actions.LIST:
            self.list_deployments()
        else:
            self._print_supported_actions(Subjects.DEPLOYMENT)

    def handle_perf(self):
        if self.options.action == Actions.RUN:
            self.perf_run()
        else:
            self._print_supported_actions(Subjects.PERF_TEST)

    def handle_datasets(self):
        if self.options.action == Actions.UPLOAD:
            self.upload_dataset()
        elif self.options.action == Actions.DELETE:
            self.delete_dataset()
        elif self.options.action == Actions.GET:
            self.get_dataset()
        elif self.options.action == Actions.LIST:
            self.list_datasets()
        else:
            self._print_supported_actions(Subjects.DATASET)

    def handle_actuals(self):
        if self.options.action == Actions.REPORT:
            self.report_actuals()
        elif self.options.action == Actions.COUNT:
            self.count_actuals()
        else:
            self._print_supported_actions(Subjects.ACTUALS)

    def handle_prediction_environment(self):
        if self.options.action == Actions.DELETE:
            self.delete_prediction_environment()
        elif self.options.action == Actions.GET:
            self.get_prediction_environment()
        elif self.options.action == Actions.LIST:
            self.list_prediction_environments()
        elif self.options.action == Actions.CREATE:
            self.create_prediction_environment()
        elif self.options.action == Actions.RESTART_MONITORING_AGENT:
            self.restart_monitoring_agent()
        elif self.options.action == Actions.RESTART_MANAGEMENT_AGENT:
            self.restart_management_agent()
        else:
            self._print_supported_actions(Subjects.PREDICTION_ENVIRONMENT)

    def handle_monitoring_jobs(self):
        if self.options.action == Actions.CREATE:
            self.create_monitoring_job()
        elif self.options.action == Actions.GET:
            self.get_monitoring_job()
        elif self.options.action == Actions.CANCEL:
            self.abort_running_monitoring_job()
        elif self.options.action == Actions.UPLOAD:
            self.upload_input_file_to_monitoring_job()
        else:
            self._print_supported_actions(Subjects.MONITORING_JOB)

    def handle_service_stats(self):
        if self.options.action == Actions.GET:
            self.get_service_stats()
        else:
            self._print_supported_actions(Subjects.SERVICE_STATS)

    def create_custom_metric(self):
        check_required_parameter(
            self.options.deployment_id, EV.MLOPS_DEPLOYMENT_ID, ArgumentsOptions.DEPLOYMENT_ID
        )
        check_required_parameter(self.options.json_config, None, ArgumentsOptions.JSON_CONF)
        try:
            info = self._read_json_config(self.options.json_config)
        except FileNotFoundError as e:
            self._log_error_and_exit(e, ExitCode.FILE_NOT_FOUND.value)
        self.create_mclient()
        try:
            metric_id = self.mclient.create_custom_metric(self.options.deployment_id, info)
            self._print_resource_generic_action(metric_id)
            logger.info(f"Created Custom Metric ID {metric_id}.")
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def get_custom_metric(self):
        check_required_parameter(
            self.options.deployment_id, EV.MLOPS_DEPLOYMENT_ID, ArgumentsOptions.DEPLOYMENT_ID
        )
        check_required_parameter(
            self.options.metric_id, EV.MLOPS_METRIC_ID, ArgumentsOptions.METRIC_ID
        )
        check_required_parameter(
            self.options.model_id, EV.MLOPS_MODEL_ID, ArgumentsOptions.MODEL_ID
        )
        self.create_mclient()
        self._log_get_action("deployment", self.options.deployment_id, "custom metric")
        try:
            if self.options.metric_id:
                stats = self.mclient.get_custom_metric_summary(
                    self.options.deployment_id, self.options.metric_id, self.options.model_id
                )
            else:
                raise Exception(
                    'Please specify either "--metric-id ' "to query for the given custom metric"
                )
            self._print_resource_received(self.options.deployment_id, stats)
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def list_custom_metrics(self):
        check_required_parameter(
            self.options.deployment_id, EV.MLOPS_DEPLOYMENT_ID, ArgumentsOptions.DEPLOYMENT_ID
        )
        self._log_get_action("deployment", self.options.deployment_id, "list custom metrics")
        self.create_mclient()
        self._log_list_action("custom metrics")

        params = {"offset": 0, "limit": 20}
        if self.options.limit:
            params["limit"] = self.options.limit

        matched = []
        try:
            all_results = self.mclient.list_custom_metrics(
                self.options.deployment_id,
                params=params,
            )
            if self.options.search:
                # Custom Metrics list controller does not support "search" parameter, so
                # we will implement our own basic search
                for result in all_results:
                    if self.options.search in result["name"]:
                        matched.append(result)
            else:
                matched = all_results
            self._print_resources_listed(matched)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    async def _report_custom_metrics_connected_lib(self, input_df, row_offset):
        self._log_report_status(input_df, row_offset)

        request_start_time = time.time()
        res, payload_size = await self.mclient.submit_custom_metrics_from_dataframe(
            self.options.deployment_id,
            self.options.model_id,
            self.options.metric_id,
            input_df,
            timestamp_col=self.options.timestamp_col,
            value_col=self.options.value_col,
            timestamp_format=self.options.timestamp_format,
            dry_run=self.options.dry_run,
        )
        request_end_time = time.time()
        request_elapsed_ms = (request_end_time - request_start_time) * 1000

        logger.debug(
            "Row offset: {} payload_size: {} time {:.1f}ms".format(
                row_offset, payload_size, request_elapsed_ms
            )
        )

    def _check_custom_metrics_columns(self, custom_metrics_columns):
        if self.options.timestamp_col not in custom_metrics_columns:
            raise DRCommonException(
                f"Timestamp column {self.options.timestamp_col} missing in the dataframe"
            )

        if self.options.value_col not in custom_metrics_columns:
            raise DRCommonException(
                f"Custom Metrics Value column {self.options.value_col} missing in the dataframe"
            )

    def _report_custom_metrics_async(self):
        self.event_loop.run_until_complete(self._custom_metrics_dispatcher())

    async def _custom_metrics_dispatcher(self):
        num_rows, iteration = self.status_tracker.get_status()
        tasks = list()
        for input_df_chunk in self.csv_splitter.get_data_chunks():
            tasks.append(
                asyncio.create_task(
                    self._report_custom_metrics_connected_lib(input_df_chunk, num_rows)
                )
            )
            num_rows = self.csv_splitter.get_current_row()
            if len(tasks) == self.options.num_concurrent_requests:
                break

        while not self.csv_splitter.is_all_data_reported():
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                tasks.remove(task)
                input_df_chunk = self.csv_splitter.get_next_chunk_to_report()
                if input_df_chunk is None:
                    continue
                num_rows = self.csv_splitter.get_current_row()
                new_task = asyncio.create_task(
                    self._report_custom_metrics_connected_lib(input_df_chunk, num_rows)
                )
                tasks.append(new_task)
                logger.debug(
                    "Added new task to report custom metrics from {} to {}".format(
                        num_rows, num_rows + self.csv_splitter.get_chunk_size()
                    )
                )

        # No more data to report, all tasks submitted, but let's wait for their completion
        logger.info("Done with submitting all tasks; waiting for them to finish now.")
        await asyncio.wait(tasks)
        logger.info("Done reporting all custom metrics.")

    def report_custom_metrics(self):
        check_required_parameter(self.options.input, None, ArgumentsOptions.INPUT)
        check_required_parameter(
            self.options.deployment_id, EV.MLOPS_DEPLOYMENT_ID, ArgumentsOptions.DEPLOYMENT_ID
        )
        check_required_parameter(
            self.options.metric_id, EV.MLOPS_METRIC_ID, ArgumentsOptions.METRIC_ID
        )
        check_required_parameter(
            self.options.model_id, EV.MLOPS_MODEL_ID, ArgumentsOptions.MODEL_ID
        )
        check_required_parameter(self.options.timestamp_col, None, ArgumentsOptions.TIMESTAMP_COL)
        check_required_parameter(self.options.value_col, None, ArgumentsOptions.VALUE_COL)

        logger.debug("Reporting custom metrics:")
        logger.debug(f"MLOps service:         {self.options.mlops_service_url}")
        logger.debug(f"Input:                 {self.options.input}")
        logger.debug(f"Metric ID:             {self.options.metric_id}")
        logger.debug(f"Timestamp column:      {self.options.timestamp_col}")
        logger.debug(f"Value column:          {self.options.value_col}")
        logger.debug(f"Timestamp Format:      {self.options.timestamp_format}")
        logger.debug(f"Dry run:               {self.options.dry_run}")

        if self.options.status_file:
            self.status_tracker = MLOpsUploadTracker(self.options.status_file)
        else:
            self.status_tracker = MLOpsUploadTracker()
        skip_rows, _ = self.status_tracker.get_status()
        try:
            self.csv_splitter = MLOpsCSVJSONSplitter(self.options.input, skip_rows=skip_rows)
            self._check_custom_metrics_columns(self.csv_splitter.get_columns())
        except (pd.errors.EmptyDataError, DRCommonException) as e:
            self._log_error_and_exit(e, ExitCode.DEFAULT.value)

        try:
            self.create_mclient()
            self._report_custom_metrics_async()
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def handle_custom_metrics(self):
        if self.options.action == Actions.CREATE:
            self.create_custom_metric()
        elif self.options.action == Actions.GET:
            self.get_custom_metric()
        elif self.options.action == Actions.LIST:
            self.list_custom_metrics()
        elif self.options.action == Actions.REPORT:
            self.report_custom_metrics()
        else:
            self._print_supported_actions(Subjects.CUSTOM_METRICS)

    def create_monitoring_batch(self):
        check_required_parameter(
            self.options.deployment_id, EV.MLOPS_DEPLOYMENT_ID, ArgumentsOptions.DEPLOYMENT_ID
        )
        check_required_parameter(self.options.json_config, None, ArgumentsOptions.JSON_CONF)
        try:
            info = self._read_json_config(self.options.json_config)
        except FileNotFoundError as e:
            self._log_error_and_exit(e, ExitCode.FILE_NOT_FOUND.value)
        self.create_mclient()
        try:
            batch_id = self.mclient.create_monitoring_batch(self.options.deployment_id, info)
            self._print_resource_generic_action(batch_id)
            logger.info(f"Created Monitoring Batch ID {batch_id}.")
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def get_batch_statistics(self):
        check_required_parameter(
            self.options.deployment_id, EV.MLOPS_DEPLOYMENT_ID, ArgumentsOptions.DEPLOYMENT_ID
        )
        check_required_parameter(
            self.options.batch_id, EV.MLOPS_BATCH_ID, ArgumentsOptions.BATCH_ID
        )
        self.create_mclient()
        self._log_get_action("deployment", self.options.deployment_id, "batch stats")
        try:
            if self.options.batch_service_stats:
                stats = self.mclient.get_batch_service_statistics(
                    self.options.deployment_id, self.options.batch_id
                )
            elif self.options.batch_data_drift:
                stats = self.mclient.get_batch_data_drift(
                    self.options.deployment_id, self.options.batch_id
                )
            else:
                raise Exception(
                    'Please specify either "--service-stats" or "--data-drift" '
                    "to query for the given batch"
                )
            self._print_resource_received(self.options.deployment_id, stats)
        except DRNotFoundException as e:
            self._log_error_and_exit(e, ExitCode.DR_NOT_FOUND.value)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def list_batches(self):
        check_required_parameter(
            self.options.deployment_id, EV.MLOPS_DEPLOYMENT_ID, ArgumentsOptions.DEPLOYMENT_ID
        )
        self._log_get_action("deployment", self.options.deployment_id, "list batches")
        self.create_mclient()
        self._log_list_action("batches")

        try:
            all_results = self.mclient.list_batches(
                self.options.deployment_id, params=self.get_list_params()
            )
            self._print_resources_listed(all_results)
        except DRMLOpsConnectedException as e:
            self._log_error_and_exit(e, ExitCode.DR_CONNECTED.value)
        except Exception as e:
            self._log_error_and_exit(e, ExitCode.UNSPECIFIED.value)
        finally:
            self.delete_mclient()

    def handle_batch(self):
        if self.options.action == Actions.CREATE:
            self.create_monitoring_batch()
        elif self.options.action == Actions.GET:
            self.get_batch_statistics()
        elif self.options.action == Actions.LIST:
            self.list_batches()
        else:
            self._print_supported_actions(Subjects.BATCH)

    def get_list_params(self):
        params = None
        if self.options.search or self.options.limit:
            params = {}
            if self.options.search:
                params["search"] = self.options.search
            if self.options.limit:
                params["limit"] = self.options.limit
        return params

    def _log_list_action(self, resource):
        logger.debug(f"Listing {resource} metadata...")
        logger.debug(f"MLOps service:         {self.options.mlops_service_url}")

    def _print_resources_listed(self, info, key="id"):
        """Print information for resources listed, according to output format."""
        if self.options.terse:
            for id in [result.get(key) for result in info]:
                print(id)
        elif self.options.json:
            print(json.dumps(info, indent=1))
        else:
            raise ValueError("Something went wrong. Output format not recognized.")

    def _log_get_action(self, resource, id, retrieved="metadata"):
        logger.debug(f"Retrieving {retrieved} for {resource} ID {id}")
        logger.debug(f"MLOps service:          {self.options.mlops_service_url}")

    def _print_resource_received(self, id, info):
        # TODO: this could technically be the same method as _print_list_resources;
        #       maybe just get 'id' from info object, instead of passing 'id' separately
        if self.options.terse:
            print(id)
        elif self.options.json:
            print(json.dumps(info, indent=1))
        else:
            raise ValueError("Something went wrong. Output format not recognized.")

    def _log_delete_action(self, resource, id):
        logger.info(f"Deleting {resource} ID {id}...")
        logger.debug(f"MLOps service:         {self.options.mlops_service_url}")

    def _print_resource_generic_action(self, id):
        """Print information for a single resource, according to output format."""
        if self.options.terse:
            print(id)
        elif self.options.json:
            print(json.dumps({"id": id}, indent=1))
        else:
            raise ValueError("Something went wrong. Output format not recognized.")

    def _log_error_and_exit(self, error, exit_code):
        show_stack_trace = logger.isEnabledFor(logging.DEBUG)
        logger.critical("%s: %s", error.__class__.__name__, error, exc_info=show_stack_trace)
        raise SystemExit(exit_code) from None

    def run(self):
        self.event_loop = asyncio.get_event_loop()
        if self.run_mode == RunMode.PERF_TEST:
            self.handle_perf()
        elif self.run_mode == RunMode.PREDICTIONS:
            self.handle_predictions()
        elif self.run_mode == RunMode.ACTUALS:
            self.handle_actuals()
        elif self.run_mode == RunMode.DATASET:
            self.handle_datasets()
        elif self.run_mode == RunMode.MODEL:
            self.handle_model()
        elif self.run_mode == RunMode.DEPLOYMENT:
            self.handle_deployment()
        elif self.run_mode == RunMode.PREDICTION_ENVIRONMENT:
            self.handle_prediction_environment()
        elif self.run_mode == RunMode.SERVICE_STATS:
            self.handle_service_stats()
        elif self.run_mode == RunMode.BATCH:
            self.handle_batch()
        elif self.run_mode == RunMode.CUSTOM_METRICS:
            self.handle_custom_metrics()
        elif self.run_mode == RunMode.MONITORING_JOBS:
            self.handle_monitoring_jobs()
        else:
            print("No valid subject provided")
            raise SystemExit(ExitCode.INVALID_CLI_INPUT.value)


def check_required_parameter(option, env_name, parameter_name):
    if option is None:
        if env_name is None:
            print(f"Missing required parameter {parameter_name}.")
        else:
            print(
                "{} must be set via environment variable or via {} parameter.".format(
                    env_name, parameter_name
                )
            )
        raise SystemExit(ExitCode.INVALID_CLI_INPUT.value)


def determine_logging_level(options):
    if options.verbose and options.quiet:
        print(
            "Please specify only one logging level from: {} | {}".format(
                ArgumentsOptions.VERBOSE, ArgumentsOptions.QUIET
            )
        )
        raise SystemExit(ExitCode.INVALID_CLI_INPUT.value)
    if options.verbose:
        return logging.DEBUG
    if options.quiet:
        return logging.ERROR
    # By default, set logging level to INFO if no level specified
    return logging.INFO


def determine_output_format(options):
    if options.json and options.terse:
        print(
            "Please specify only one output type from: {} (default) | {}".format(
                ArgumentsOptions.JSON, ArgumentsOptions.TERSE
            )
        )
        raise SystemExit(ExitCode.INVALID_CLI_INPUT.value)
    # No changes needed if one or the other specified
    if options.json or options.terse:
        return
    # By default, set output format to JSON if no format specified
    options.json = True


def main():
    arg_parser = MLOpsCliArgParser.get_arg_parser()
    options = arg_parser.parse_args()

    check_required_parameter(
        options.mlops_service_url, EV.MLOPS_SERVICE_URL, ArgumentsOptions.MLOPS_SERVICE
    )
    check_required_parameter(
        options.mlops_api_token, EV.MLOPS_API_TOKEN, ArgumentsOptions.MLOPS_API_TOKEN
    )
    determine_output_format(options)
    logging_level = determine_logging_level(options)

    console_handler = logging.StreamHandler()
    simple_formatter = logging.Formatter("%(levelname)-8s  %(message)s")
    debug_formatter = logging.Formatter(
        "%(asctime)s,%(lineno)4d %(levelname)-8s %(name)s    %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    if logging_level == logging.DEBUG:
        console_handler.setFormatter(debug_formatter)
    else:
        console_handler.setFormatter(simple_formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging_level)

    # Setup signal handler so we can exit cleanly (i.e. delete lock files)
    def handle_term(*args):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, handle_term)

    mlops_cli = MLOpsCli(options)
    mlops_cli.run()
    exit(ExitCode.OK.value)


if __name__ == "__main__":
    main()
