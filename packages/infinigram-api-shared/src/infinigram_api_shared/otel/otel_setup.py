import os

from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor

from .service_name_span_processor import ServiceNameSpanProcessor


def set_up_tracing(service_name: str = "infinigram-api") -> None:
    tracer_provider = TracerProvider()

    if os.getenv("ENV") == "development":
        tracer_provider.add_span_processor(
            span_processor=SimpleSpanProcessor(OTLPSpanExporter())
        )
    else:
        tracer_provider.add_span_processor(
            BatchSpanProcessor(CloudTraceSpanExporter(project_id="ai2-reviz"))  # type:ignore[no-untyped-call]
        )

    tracer_provider.add_span_processor(ServiceNameSpanProcessor(service_name))

    trace.set_tracer_provider(tracer_provider)
