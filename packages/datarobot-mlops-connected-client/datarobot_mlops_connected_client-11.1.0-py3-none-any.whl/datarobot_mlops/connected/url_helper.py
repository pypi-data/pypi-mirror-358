#  Copyright (c) 2021 DataRobot, Inc. and its affiliates. All rights reserved.
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

from urllib.parse import urlencode


def build_url(host_base_url, *res, **params):
    """
    Function to build url. Examples:
    build_url('http://localhost:8080', 'deployments') => http://localhost:8080/deployments/
    build_url('https://localhost:8080', 'deployments', name="test_deployment") =>
    https://localhost:8080/deployments/?name=test_deployment
    The DataRobot API will redirect the client if the path does not end in '/'.
    :param host_base_url: REST service url base.
    :param res: path components
    :param params: REST request parameters.
    """

    url = host_base_url.rstrip("/")
    for r in res:
        if r is not None:
            url = f"{url}/{r}"
    if not url.endswith("/"):
        url += "/"
    if params:
        url = f"{url}?{urlencode(params)}"

    return url


class MMMEndpointPrefix:
    DEPLOYMENT = "api/v2/deployments"
    DATASET = "api/v2/datasets"
    MODEL_PACKAGE = "api/v2/modelPackages"
    PREDICTION_ENV = "api/v2/predictionEnvironments"
    MLOPS_PREDICTION_ENV = "api/v2/mlops/predictionEnvironments"
    BATCH_MONITORING = "api/v2/batchMonitoring"
    BATCH_JOBS = "api/v2/batchJobs"


class MMMEndpoint:
    ARCHIVE = "archive"
    FEATURES = "features"
    FROM_FILE = "fromFile"
    PREDICTION_DATASET = "predictionInputs/fromDataset/"
    API_VERSION = "api/v2/version/"
    FROM_JSON = "fromJSON"
    FROM_MODEL_PACKAGE = "fromModelPackage"
    MODEL_PACKAGE_BUILDS = "modelPackageFileBuilds"
    MODEL_PACKAGE_DOWNLOAD = "modelPackageFile"
    MODEL = "model"
    SETTINGS = "settings"
    SCORING_CODE_BUILD = "scoringCodeBuilds"
    SCORING_CODE_DOWNLOAD = "scoringCode"
    SERVICE_STATS = "serviceStats"
    PREDICTION_STATS = "predictionsOverTime"
    TARGET_DRIFT = "targetDrift"
    PREDICTIONS_ACTUALS_STATS = "predictionsVsActualsOverTime"
    MONITORING_BATCHES = "monitoringBatches"
    PREDICTIONS_OVER_BATCH = "predictionsOverBatch"
    CUSTOM_METRICS = "customMetrics"
    SUMMARY = "summary"
    CSV_UPLOAD = "csvUpload"
    MONITORING_AGENTS = "monitoringAgents"
    MANAGEMENT_AGENTS = "managementAgents"


class URLBuilder:
    def __init__(self, service_url):
        self._service_url = service_url

    def deployment(self, deployment_id, force_delete=False):
        extra_args = {"ignoreManagementAgent": "true"} if force_delete else {}
        return build_url(
            self._service_url, MMMEndpointPrefix.DEPLOYMENT, deployment_id, **extra_args
        )

    def list_deployments(self):
        return build_url(self._service_url, MMMEndpointPrefix.DEPLOYMENT)

    def deploy_model_package(self):
        return build_url(
            self._service_url, MMMEndpointPrefix.DEPLOYMENT, MMMEndpoint.FROM_MODEL_PACKAGE
        )

    def upload_dataset(self):
        return build_url(self._service_url, MMMEndpointPrefix.DATASET, MMMEndpoint.FROM_FILE)

    def deployment_settings(self, deployment_id):
        return build_url(
            self._service_url, MMMEndpointPrefix.DEPLOYMENT, deployment_id, MMMEndpoint.SETTINGS
        )

    def associate_deployment_dataset(self, deployment_id):
        return build_url(
            self._service_url,
            MMMEndpointPrefix.DEPLOYMENT,
            deployment_id,
            MMMEndpoint.PREDICTION_DATASET,
        )

    def create_model_package(self):
        return build_url(self._service_url, MMMEndpointPrefix.MODEL_PACKAGE, MMMEndpoint.FROM_JSON)

    def replace_model_package(self, deployment_id):
        return build_url(
            self._service_url, MMMEndpointPrefix.DEPLOYMENT, deployment_id, MMMEndpoint.MODEL
        )

    def get_model_package(self, model_package_id):
        return build_url(self._service_url, MMMEndpointPrefix.MODEL_PACKAGE, model_package_id)

    def list_model_packages(self):
        return build_url(self._service_url, MMMEndpointPrefix.MODEL_PACKAGE)

    def archive_model_package(self, model_package_id):
        return build_url(
            self._service_url,
            MMMEndpointPrefix.MODEL_PACKAGE,
            model_package_id,
            MMMEndpoint.ARCHIVE,
        )

    def features_model_package(self, model_package_id):
        return build_url(
            self._service_url,
            MMMEndpointPrefix.MODEL_PACKAGE,
            model_package_id,
            MMMEndpoint.FEATURES,
        )

    def model_package_build_from_registry(self, model_package_id):
        return build_url(
            self._service_url,
            MMMEndpointPrefix.MODEL_PACKAGE,
            model_package_id,
            MMMEndpoint.MODEL_PACKAGE_BUILDS,
        )

    def model_package_download_from_registry(self, model_package_id):
        return build_url(
            self._service_url,
            MMMEndpointPrefix.MODEL_PACKAGE,
            model_package_id,
            MMMEndpoint.MODEL_PACKAGE_DOWNLOAD,
        )

    def scoring_code_build_from_registry(self, model_package_id):
        return build_url(
            self._service_url,
            MMMEndpointPrefix.MODEL_PACKAGE,
            model_package_id,
            MMMEndpoint.SCORING_CODE_BUILD,
        )

    def scoring_code_download_from_registry(self, model_package_id):
        return build_url(
            self._service_url,
            MMMEndpointPrefix.MODEL_PACKAGE,
            model_package_id,
            MMMEndpoint.SCORING_CODE_DOWNLOAD,
        )

    def model_package_build(self, deployment_id):
        return build_url(
            self._service_url,
            MMMEndpointPrefix.DEPLOYMENT,
            deployment_id,
            MMMEndpoint.MODEL_PACKAGE_BUILDS,
        )

    def model_package_download(self, deployment_id):
        return build_url(
            self._service_url,
            MMMEndpointPrefix.DEPLOYMENT,
            deployment_id,
            MMMEndpoint.MODEL_PACKAGE_DOWNLOAD,
        )

    def scoring_code_build(self, deployment_id):
        return build_url(
            self._service_url,
            MMMEndpointPrefix.DEPLOYMENT,
            deployment_id,
            MMMEndpoint.SCORING_CODE_BUILD,
        )

    def scoring_code_download(self, deployment_id):
        return build_url(
            self._service_url,
            MMMEndpointPrefix.DEPLOYMENT,
            deployment_id,
            MMMEndpoint.SCORING_CODE_DOWNLOAD,
        )

    def get_model_id(self, deployment_id):
        return build_url(self._service_url, MMMEndpointPrefix.DEPLOYMENT, deployment_id)

    def get_dataset(self, dataset_id):
        return build_url(self._service_url, MMMEndpointPrefix.DATASET, dataset_id)

    def list_datasets(self):
        return build_url(self._service_url, MMMEndpointPrefix.DATASET)

    def soft_delete_dataset(self, dataset_id):
        return build_url(self._service_url, MMMEndpointPrefix.DATASET, dataset_id)

    def create_prediction_environment(self):
        return build_url(self._service_url, MMMEndpointPrefix.PREDICTION_ENV, None)

    def get_prediction_environment(self, pe_id):
        return build_url(self._service_url, MMMEndpointPrefix.PREDICTION_ENV, pe_id)

    def restart_monitoring_agent(self, pe_id):
        return build_url(
            self._service_url,
            MMMEndpointPrefix.MLOPS_PREDICTION_ENV,
            pe_id,
            MMMEndpoint.MONITORING_AGENTS,
        )

    def restart_management_agent(self, pe_id):
        return build_url(
            self._service_url,
            MMMEndpointPrefix.MLOPS_PREDICTION_ENV,
            pe_id,
            MMMEndpoint.MANAGEMENT_AGENTS,
        )

    def list_prediction_environments(self):
        return build_url(self._service_url, MMMEndpointPrefix.PREDICTION_ENV)

    def create_monitoring_job(self):
        return build_url(self._service_url, MMMEndpointPrefix.BATCH_MONITORING, None)

    def get_monitoring_job(self, job_id):
        return build_url(self._service_url, MMMEndpointPrefix.BATCH_JOBS, job_id)

    def upload_file_to_monitoring_job(self, job_id):
        return build_url(
            self._service_url, MMMEndpointPrefix.BATCH_JOBS, job_id, MMMEndpoint.CSV_UPLOAD
        )

    def get_service_stats(self, deployment_id):
        return build_url(
            self._service_url,
            MMMEndpointPrefix.DEPLOYMENT,
            deployment_id,
            MMMEndpoint.SERVICE_STATS,
        )

    def get_prediction_stats(self, deployment_id):
        return build_url(
            self._service_url,
            MMMEndpointPrefix.DEPLOYMENT,
            deployment_id,
            MMMEndpoint.PREDICTION_STATS,
        )

    def get_target_drift(self, deployment_id):
        return build_url(
            self._service_url, MMMEndpointPrefix.DEPLOYMENT, deployment_id, MMMEndpoint.TARGET_DRIFT
        )

    def get_predictions_and_actuals_stats_url(self, deployment_id):
        return build_url(
            self._service_url,
            MMMEndpointPrefix.DEPLOYMENT,
            deployment_id,
            MMMEndpoint.PREDICTIONS_ACTUALS_STATS,
        )

    def create_monitoring_batch(self, deployment_id):
        return build_url(
            self._service_url,
            MMMEndpointPrefix.DEPLOYMENT,
            deployment_id,
            MMMEndpoint.MONITORING_BATCHES,
        )

    def list_batches(self, deployment_id):
        return build_url(
            self._service_url,
            MMMEndpointPrefix.DEPLOYMENT,
            deployment_id,
            MMMEndpoint.MONITORING_BATCHES,
        )

    def get_batch_service_statistics(self, deployment_id, batch_id):
        url = build_url(
            self._service_url,
            MMMEndpointPrefix.DEPLOYMENT,
            deployment_id,
            MMMEndpoint.MONITORING_BATCHES,
        )
        return f"{url}{batch_id}/"

    def get_batch_data_drift(self, deployment_id, batch_id):
        return build_url(
            self._service_url,
            MMMEndpointPrefix.DEPLOYMENT,
            deployment_id,
            MMMEndpoint.PREDICTIONS_OVER_BATCH,
            batchId=batch_id,
        )

    def create_custom_metric(self, deployment_id):
        return build_url(
            self._service_url,
            MMMEndpointPrefix.DEPLOYMENT,
            deployment_id,
            MMMEndpoint.CUSTOM_METRICS,
        )

    def get_custom_metric_summary(self, deployment_id, metric_id):
        return build_url(
            self._service_url,
            MMMEndpointPrefix.DEPLOYMENT,
            deployment_id,
            MMMEndpoint.CUSTOM_METRICS,
            metric_id,
            MMMEndpoint.SUMMARY,
        )

    def list_custom_metrics(self, deployment_id):
        return build_url(
            self._service_url,
            MMMEndpointPrefix.DEPLOYMENT,
            deployment_id,
            MMMEndpoint.CUSTOM_METRICS,
        )
