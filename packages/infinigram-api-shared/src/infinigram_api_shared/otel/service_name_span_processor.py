from opentelemetry import context as context_api
from opentelemetry.sdk.trace import ReadableSpan, Span, SpanProcessor


class ServiceNameSpanProcessor(SpanProcessor):
    service_name: str

    def __init__(self, service_name: str):
        self.service_name = service_name

    # This class forces the service.name onto the span. For some reason OTLPSpanExporter will not send the process tags, so this is a way to force it.
    def on_start(
        self, span: Span, parent_context: context_api.Context | None = None
    ) -> None:
        span.set_attributes({
            "service.name": self.service_name,
        })

    def on_end(self, span: ReadableSpan) -> None:
        pass
