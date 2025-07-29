from __future__ import annotations

import base64
import dataclasses
import json
import logging
import random
from typing import Sequence, TYPE_CHECKING
from typing_extensions import reveal_type as reveal_type  # temp

import freezegun
import opentelemetry.trace
from google.protobuf.json_format import MessageToDict
from opentelemetry.exporter.otlp.proto.common._internal import trace_encoder
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import set_tracer_provider, get_tracer_provider

if TYPE_CHECKING:
    from google.protobuf.message import Message
    from opentelemetry.sdk.trace import ReadableSpan
    from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import (
        ExportTraceServiceRequest,
    )


tracer = opentelemetry.trace.get_tracer(__name__)
provider = TracerProvider()
exporter = InMemorySpanExporter()
provider.add_span_processor(SimpleSpanProcessor(exporter))
set_tracer_provider(provider)


@dataclasses.dataclass
class Config:
    start_time: str = "2020-01-01 00:00:00Z"
    random_seed: int = 42


time: freezegun.api.FrozenDateTimeFactory = None  # type: ignore


class LogsToEvents(logging.Handler):
    def emit(self, record):
        span = opentelemetry.trace.get_current_span()
        if span and span.is_recording():
            span.add_event(record.getMessage(), {"severity": record.levelname})


def sample_proto(config: Config | None = None) -> bytes:
    return _proto_to_bytes(_spans_to_proto_object(sample_spans(config)))


def sample_json(config: Config | None = None) -> bytes:
    return _proto_to_json(_spans_to_proto_object(sample_spans(config)))


def sample_spans(config: Config | None = None) -> Sequence[ReadableSpan]:
    """Creates and finishes two spans, then returns them as a list."""
    global time
    config = config or Config()
    logging.basicConfig(level="DEBUG")
    if not any(isinstance(h, LogsToEvents) for h in logging.root.handlers):
        logging.root.addHandler(LogsToEvents())
    resource = Resource.create(
        attributes={
            "service.namespace": "1234-1234",  # a unique id
            "service.name": "my-service",
            "service.instance.id": "123",
            "int": 42,
            "float": 3.14,
            "bool": False,
            "str": "sss",
            "ints": [42, 0],
            "floats": [3.14, 2.72],
            "strs": ["sss", "shh"],
        }
    )
    del exporter._finished_spans[:]
    get_tracer_provider()._resource = resource  # type: ignore

    random.seed(config.random_seed)

    with freezegun.freeze_time(config.start_time) as time:  # type: ignore
        workload()

    return exporter.get_finished_spans()


def _spans_to_proto_object(spans: Sequence[ReadableSpan]) -> ExportTraceServiceRequest:
    return trace_encoder.encode_spans(spans)


def _proto_to_bytes(data: Message) -> bytes:
    return data.SerializePartialToString()


# FIXME: there are probably 3 different enumerated types in the API
def _proto_to_json(data: Message) -> bytes:
    dic = MessageToDict(data)

    for rs in dic["resourceSpans"]:
        for ss in rs["scopeSpans"]:
            for sp in ss["spans"]:
                for k in "parentSpanId spanId traceId".split():
                    if k in sp:
                        sp[k] = base64.b64decode(sp[k]).hex()
                sp["kind"] = {
                    "SPAN_KIND_UNSPECIFIED": 0,
                    "SPAN_KIND_INTERNAL": 1,
                    "SPAN_KIND_SERVER": 2,
                    "SPAN_KIND_CLIENT": 3,
                    "SPAN_KIND_PRODUCER": 4,
                    "SPAN_KIND_CONSUMER": 5,
                }[sp["kind"]]
                if status := sp["status"]:
                    status["code"] = {
                        "STATUS_CODE_UNSET": 0,
                        "STATUS_CODE_OK": 1,
                        "STATUS_CODE_ERROR": 2,
                    }[status["code"]]

    return json.dumps(dic).encode("utf-8")


def workload():
    series_of_spans()
    nested_spans()
    attribute_types()
    repeated_attributes()
    events()
    instrumentation_scopes()
    with_exception()
    with_logs()
    # TODO: status that's not an OK status
    # TODO: captured logs
    # TODO: example exception traceback
    # TODO: instrumentation scope with a version
    # TODO: instrumentation scope with attributes


def series_of_spans():
    with tracer.start_as_current_span("span-one") as one:
        one.set_attribute("count", "one")
        time.tick()

    with tracer.start_as_current_span("span-two") as two:
        two.set_attribute("count", "two")
        time.tick()


def nested_spans():
    outer()


@tracer.start_as_current_span("outer")
def outer():
    time.tick()
    inner()
    time.tick()


@tracer.start_as_current_span("inner")
def inner() -> None:
    opentelemetry.trace.get_current_span().set_attribute("an-attribute", 42)
    time.tick()


@tracer.start_as_current_span("with-exc-outer")
def with_exception() -> None:
    try:
        with tracer.start_as_current_span("with-exc-inner"):
            1 / 0  # type: ignore
    except Exception:
        pass


@tracer.start_as_current_span("with-logs")
def with_logs() -> None:
    logging.warning("sss")
    time.tick()
    logging.warning("sss-sss")
    time.tick()
    logging.warning("sss-sss-sss")


def attribute_types():
    with tracer.start_as_current_span("attribute-types") as span:
        span.set_attributes(
            {"int": 42, "bool": False, "float": 3.14, "str": "cheese", "bytes": b"bb"}
        )
        span.set_attributes(
            {
                "ints": [1, 42],
                "bools": [True, False],
                "floats": [2.72, 3.14],
                "strs": ["cheese", "mozzarella"],
                "byteses": [b"aa", b"bb"],  # type: ignore
            }
        )


def instrumentation_scopes():
    tracer1 = opentelemetry.trace.get_tracer("one", "1.2.3")
    tracer2 = opentelemetry.trace.get_tracer("one", "2.7.18")
    tracer3 = opentelemetry.trace.get_tracer(
        "one",
        "3.14.0a5",
        attributes={
            "bool": True,
            "int": 42,
            "float": -12.34,
            "string": "cheese",
            "bytes": b"bb",
            "empty-list": [],
            # "empty-dict": {},  # not allowed for instrumentation scopes
        },
    )

    with tracer1.start_as_current_span("1.1"):
        time.tick()
    with tracer2.start_as_current_span("2.1"):
        time.tick()
    with tracer1.start_as_current_span("1.2"):
        time.tick()
    with tracer1.start_as_current_span("1.3"):
        time.tick()
    with tracer3.start_as_current_span("3.1"):
        time.tick()
    with tracer1.start_as_current_span("1.4"):
        time.tick()


def repeated_attributes():
    with tracer.start_as_current_span("attribute-types") as span:
        span.set_attribute("int", 42)
        span.set_attribute("int", 99)

    with tracer.start_as_current_span("attribute-types") as span:
        span.set_attributes({"int": 42})
        span.set_attributes({"int": 99})


def events():
    with tracer.start_as_current_span("attribute-types") as span:
        span.add_event("first event")
        time.tick()

        span.add_event("second event")
        time.tick()

        span.add_event(
            "event with attributes",
            attributes={
                "int": 42,
                "bool": False,
                "float": 3.14,
                "str": "string-cheese",
                "ints": [1, 42],
                "bools": [True, False],
                "floats": [2.72, 3.14],
                "strs": ["string-cheese", "strung-cheese"],
            },
        )
        time.tick()
