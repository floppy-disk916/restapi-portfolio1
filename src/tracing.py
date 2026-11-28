
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

def setup_tracing(app, engine=None):
    # 1. Create a resource to identify your service
    resource = Resource.create(attributes={"service.name": "restapi-portfolio1"})

    # 2. Set up the TracerProvider
    provider = TracerProvider(resource=resource)

    # 3. Configure the exporter (point this to your Jaeger endpoint)
    # Use "http://localhost:4317" if running Jaeger locally via Docker
    # Use "http://jaeger:4317" if your app is also in Docker Compose
    otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    # 4. Set the global tracer provider
    trace.set_tracer_provider(provider)

    # 5. Instrument FastAPI and SQLAlchemy
    FastAPIInstrumentor.instrument_app(app)
    if engine:
        SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
