from opentelemetry import context as context_api
from opentelemetry.sdk.trace import ReadableSpan, Span, SpanProcessor


class ServiceNameSpanProcessor(SpanProcessor):
    # This class forces the service.name onto the span. For some reason OTLPSpanExporter will not send the process tags, so this is a way to force it.
    def on_start(
        self, span: Span, parent_context: context_api.Context | None = None
    ) -> None:
        span.set_attributes({
            "service.name": "infinigram-api",
        })

    def on_end(self, span: ReadableSpan) -> None:
        pass
