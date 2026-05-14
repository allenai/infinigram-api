import os

from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import (
    DEPLOYMENT_ENVIRONMENT,
    SERVICE_INSTANCE_ID,
    SERVICE_NAME,
    Resource,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import set_tracer_provider


def set_up_tracing(
    *,
    is_otel_enabled: bool = True,
    is_prod_environment: bool = True,
    otel_service_name: str = "infinigram-api",
    env: str = "prod",
) -> None:
    if is_otel_enabled or is_prod_environment:
        resource = Resource.create(
            attributes={
                SERVICE_NAME: otel_service_name,
                SERVICE_INSTANCE_ID: f"worker-{os.getpid()}",
                DEPLOYMENT_ENVIRONMENT: env,
            }
        )

        tracer_provider = TracerProvider(resource=resource)

        metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
        meter_provider = MeterProvider(
            metric_readers=[metric_reader], resource=resource
        )

        tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))

        set_tracer_provider(tracer_provider)
        set_meter_provider(meter_provider)
