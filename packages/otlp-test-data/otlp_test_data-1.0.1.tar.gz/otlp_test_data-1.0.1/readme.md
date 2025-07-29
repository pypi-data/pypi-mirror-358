# otlp-test-data

Produces OTLP data using OTEL instrumentation.

### Features

- Fixed, configurable timestamps
- aims to cover as much of OTEL API as possible
- Cover all valid data types
- Events

### Limitations

- currently only tracing data is generated, PRs are welcome to add metrics and logs data
- data is generated in process, remote (forwarded) spans are not supported

### TODO

- Links
- Baggage
- Schemata, when https://github.com/open-telemetry/opentelemetry-python/pull/4359 lands
- Attribute value type coercion, e.g. `class Str(str): ...` and objects with `__str__(self)`.
- Exceptions
