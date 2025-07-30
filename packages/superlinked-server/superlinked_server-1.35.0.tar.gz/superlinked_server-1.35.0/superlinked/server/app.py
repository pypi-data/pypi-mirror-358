# Copyright 2024 Superlinked, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from json import JSONDecodeError

import sentry_sdk
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from opentelemetry.exporter.cloud_monitoring import CloudMonitoringMetricsExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from superlinked.framework.common.metrics.metric_registry import (
    MetricRegistry,
    MetricType,
)
from superlinked.framework.common.parser.exception import MissingIdException
from superlinked.framework.online.dag.exception import ValueNotProvidedException
from superlinked.server.configuration.app_config import AppConfig
from superlinked.server.dependency_register import register_dependencies
from superlinked.server.exception.exception_handler import (
    handle_bad_request,
    handle_generic_exception,
)
from superlinked.server.logger import ServerLoggerConfigurator
from superlinked.server.middleware.lifespan_event import lifespan
from superlinked.server.middleware.timing_middleware import add_timing_middleware
from superlinked.server.router.management_router import router as management_router
from superlinked.server.util.superlinked_app_downloader_util import download_from_gcs
from superlinked.server.util.version_resolver import VersionResolver


class ServerApp:
    def __init__(self) -> None:
        self.app = self._create_app()

    def _setup_executor_handlers(self, app: FastAPI) -> None:
        app.add_exception_handler(ValueNotProvidedException, handle_bad_request)
        app.add_exception_handler(MissingIdException, handle_bad_request)
        app.add_exception_handler(JSONDecodeError, handle_bad_request)
        app.add_exception_handler(ValueError, handle_bad_request)
        app.add_exception_handler(Exception, handle_generic_exception)

    def _create_app(self) -> FastAPI:
        app_config = AppConfig()
        ServerLoggerConfigurator.setup_logger(app_config)
        if app_config.IS_DOCKERIZED:
            if not app_config.BUCKET_NAME or not app_config.BUCKET_PREFIX:
                raise ValueError(
                    "Environment variables BUCKET_NAME and BUCKET_PREFIX must be defined when IS_DOCKERIZED is enabled"
                )
            download_from_gcs(
                app_config.BUCKET_NAME, app_config.BUCKET_PREFIX, app_config.APP_MODULE_PATH, app_config.PROJECT_ID
            )
        self._init_sentry(app_config)
        app = FastAPI(lifespan=lifespan)
        self._init_opentelemetry(app_config)
        self._setup_executor_handlers(app)
        app.include_router(management_router)

        add_timing_middleware(app)
        app.add_middleware(
            GZipMiddleware,
            minimum_size=app_config.GZIP_MINIMUM_SIZE,
            compresslevel=app_config.GZIP_COMPRESSLEVEL,
        )
        app.add_middleware(CorrelationIdMiddleware)  # This must be the last middleware

        register_dependencies()

        return app

    def _init_sentry(self, app_config: AppConfig) -> None:
        if app_config.SENTRY_ENABLE:
            sentry_sdk.init(
                dsn=app_config.SENTRY_URL,
                send_default_pii=app_config.SENTRY_SEND_DEFAULT_PII,
                traces_sample_rate=app_config.SENTRY_TRACES_SAMPLE_RATE,
                profiles_sample_rate=app_config.SENTRY_PROFILES_SAMPLE_RATE,
            )

    def _init_opentelemetry(self, app_config: AppConfig) -> None:
        if not app_config.OPENTELEMETRY_ENABLE:
            return

        if not app_config.OPENTELEMETRY_PROJECT_ID:
            raise ValueError("OPENTELEMETRY_PROJECT_ID must be set in the environment variables")

        metric_registry = MetricRegistry()
        framework_version = VersionResolver.get_version_for_package("superlinked") or "unknown"
        server_version = VersionResolver.get_version_for_package("superlinked-server") or "unknown"
        labels = {
            "service": "superlinked-server",
            "framework-version": framework_version,
            "version": server_version,
            "environment": "DEV",
        }
        metric_registry.add_labels(labels)

        metric_registry.create_metric(MetricType.COUNTER, "http_requests_total", "Count of HTTP requests", "1")
        metric_registry.create_metric(
            MetricType.HISTOGRAM, "http_request_duration_ms", "HTTP request duration in milliseconds", "ms"
        )
        metric_registry.create_metric(
            MetricType.COUNTER,
            "ingested_items_with_data_loader_total",
            "Count of ingested items with data loader",
            "item",
        )

        metric_exporter = CloudMonitoringMetricsExporter(
            app_config.OPENTELEMETRY_PROJECT_ID, add_unique_identifier=True
        )
        metric_reader = PeriodicExportingMetricReader(
            exporter=metric_exporter, export_interval_millis=app_config.OPENTELEMETRY_EXPORT_INTERVAL_IN_MS
        )

        metric_registry.initialize(
            MeterProvider(metric_readers=[metric_reader]), meter_name=app_config.OPENTELEMETRY_METER_NAME
        )
