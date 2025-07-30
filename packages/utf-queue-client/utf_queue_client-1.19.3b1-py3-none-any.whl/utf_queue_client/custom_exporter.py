from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as HTTPSpanExporter,
)
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult


class CustomSpansExporter(SpanExporter):
    def __init__(self, options):
        self.exporter = HTTPSpanExporter()

    def export(self, spans):
        return SpanExportResult.SUCCESS

    def shutdown(self):
        return self.exporter.shutdown()

    def force_flush(self, timeout_millis: int = 60000):
        return self.exporter.force_flush(timeout_millis)
