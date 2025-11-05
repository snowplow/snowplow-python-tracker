# Snowplow Python Tracker - CLAUDE.md

## Project Overview

The Snowplow Python Tracker is a public Python library for sending analytics events to Snowplow collectors. It enables developers to integrate Snowplow analytics into Python applications, games, and web servers. The library provides a robust event tracking system with support for various event types, custom contexts, and reliable event delivery through configurable emitters.

**Key Technologies:**
- Python 3.8+ (supported versions: 3.8-3.13)
- requests library for HTTP communication
- typing_extensions for enhanced type hints
- Event-driven architecture with schema validation
- Asynchronous and synchronous event emission

## Development Commands

```bash
# Install dependencies
pip install -r requirements-test.txt

# Run tests
./run-tests.sh

# Run specific test module
python -m pytest snowplow_tracker/test/unit/test_tracker.py

# Run integration tests
python -m pytest snowplow_tracker/test/integration/

# Install package in development mode
pip install -e .

# Build Docker image for testing
docker build -t snowplow-python-tracker .
docker run snowplow-python-tracker
```

## Architecture

The tracker follows a layered architecture with clear separation of concerns:

```
snowplow_tracker/
├── Core Components
│   ├── tracker.py          # Main Tracker class orchestrating events
│   ├── snowplow.py         # High-level API for tracker management
│   └── subject.py          # User/device context management
├── Event Layer (events/)
│   ├── event.py            # Base Event class
│   ├── page_view.py        # PageView event
│   ├── structured_event.py # Structured events
│   └── self_describing.py  # Custom schema events
├── Emission Layer
│   ├── emitters.py         # Sync/Async event transmission
│   ├── event_store.py      # Event buffering and persistence
│   └── payload.py          # Event payload construction
├── Configuration
│   ├── tracker_configuration.py
│   └── emitter_configuration.py
└── Validation
    ├── contracts.py        # Runtime validation
    └── typing.py           # Type definitions
```

## Core Architectural Principles

1. **Schema-First Design**: All events conform to Iglu schemas for consistency
2. **Separation of Concerns**: Event creation, validation, and emission are separate
3. **Configuration Objects**: Use dedicated configuration classes, not raw dictionaries
4. **Type Safety**: Extensive use of type hints and Protocol classes
5. **Fail-Safe Delivery**: Events are buffered and retried on failure
6. **Immutability**: Event objects are largely immutable after creation

## Layer Organization & Responsibilities

### Application Layer (snowplow.py)
- Singleton pattern for global tracker management
- Factory methods for tracker creation
- Namespace-based tracker registry

### Domain Layer (tracker.py, events/)
- Event creation and validation
- Subject (user/device) context management
- Event enrichment with standard fields

### Infrastructure Layer (emitters.py, event_store.py)
- HTTP communication with collectors
- Event buffering and retry logic
- Async/sync emission strategies

### Cross-Cutting (contracts.py, typing.py)
- Runtime validation with togglable contracts
- Shared type definitions and protocols

## Critical Import Patterns

```python
# ✅ Import from package root for public API
from snowplow_tracker import Snowplow, Tracker, Subject
from snowplow_tracker import EmitterConfiguration, TrackerConfiguration

# ✅ Import specific event classes
from snowplow_tracker.events import PageView, StructuredEvent

# ❌ Don't import from internal modules
from snowplow_tracker.emitters import Requester  # Internal class

# ✅ Use typing module for type hints
from snowplow_tracker.typing import PayloadDict, Method
```

## Essential Library Patterns

### Tracker Initialization Pattern
```python
# ✅ Use Snowplow factory with configuration objects
tracker = Snowplow.create_tracker(
    namespace="my_app",
    endpoint="https://collector.example.com",
    tracker_config=TrackerConfiguration(encode_base64=True),
    emitter_config=EmitterConfiguration(batch_size=10)
)

# ❌ Don't instantiate Tracker directly without Snowplow
tracker = Tracker("namespace", emitter)  # Missing registration
```

### Event Creation Pattern
```python
# ✅ Use event classes with named parameters
page_view = PageView(
    page_url="https://example.com",
    page_title="Homepage"
)

# ✅ Add contexts to events
event.context = [SelfDescribingJson(schema, data)]

# ❌ Don't modify event payload directly
event.payload.add("custom", "value")  # Breaks schema validation
```

### Subject Management Pattern
```python
# ✅ Set subject at tracker or event level
subject = Subject()
subject.set_user_id("user123")
tracker = Snowplow.create_tracker(..., subject=subject)

# ✅ Override subject per event
event = PageView(..., event_subject=Subject())

# ❌ Don't modify subject after tracker creation
tracker.subject.set_user_id("new_id")  # Not thread-safe
```

### Emitter Configuration Pattern
```python
# ✅ Configure retry and buffering behavior
config = EmitterConfiguration(
    batch_size=50,
    buffer_capacity=10000,
    custom_retry_codes={429: True, 500: True}
)

# ❌ Don't use magic numbers
emitter = Emitter(endpoint, 443, "post", 100)  # Use config object
```

## Model Organization Pattern

### Event Hierarchy
```python
Event (base class)
├── PageView         # Web page views
├── PagePing         # Page engagement tracking
├── ScreenView       # Mobile screen views
├── StructuredEvent  # Category/action/label/property/value events
└── SelfDescribing   # Custom schema events
```

### Data Structures
```python
# SelfDescribingJson for custom contexts
context = SelfDescribingJson(
    "iglu:com.example/context/jsonschema/1-0-0",
    {"key": "value"}
)

# Payload for event data assembly
payload = Payload()
payload.add("e", "pv")  # Event type
payload.add_dict({"aid": "app_id"})
```

## Common Pitfalls & Solutions

### Contract Validation
```python
# ❌ Passing invalid parameters silently fails in production
tracker.track_page_view("")  # Empty URL

# ✅ Enable contracts during development
from snowplow_tracker import enable_contracts
enable_contracts()
```

### Event Buffering
```python
# ❌ Not flushing events before shutdown
tracker.track(event)
sys.exit()  # Events lost!

# ✅ Always flush before exit
tracker.track(event)
tracker.flush()
```

### Thread Safety
```python
# ❌ Sharing emitter across threads
emitter = Emitter(endpoint)
# Multiple threads using same emitter

# ✅ Use AsyncEmitter for concurrent scenarios
emitter = AsyncEmitter(endpoint, thread_count=2)
```

### Schema Validation
```python
# ❌ Hardcoding schema strings
schema = "iglu:com.snowplow/event/1-0-0"

# ✅ Use constants for schemas
from snowplow_tracker.constants import CONTEXT_SCHEMA
```

## File Structure Template

```
project/
├── tracker_app.py           # Application entry point
├── config/
│   └── tracker_config.py    # Tracker configuration
├── events/
│   ├── __init__.py
│   └── custom_events.py     # Custom event definitions
├── contexts/
│   └── custom_contexts.py   # Custom context schemas
└── tests/
    ├── unit/
    │   └── test_events.py
    └── integration/
        └── test_emission.py
```

## Testing Patterns

### Unit Testing
```python
# ✅ Mock emitters for unit tests
@mock.patch('snowplow_tracker.emitters.Emitter')
def test_track_event(mock_emitter):
    tracker = Tracker("test", mock_emitter)
    tracker.track(PageView(...))
    mock_emitter.input.assert_called_once()
```

### Contract Testing
```python
# ✅ Use ContractsDisabled context manager
with ContractsDisabled():
    # Test invalid inputs without raising
    tracker.track_page_view(None)
```

### Integration Testing
```python
# ✅ Test against mock collector
def test_event_delivery():
    with requests_mock.Mocker() as m:
        m.post("https://collector.test/com.snowplow/tp2")
        # Track and verify delivery
```

## Configuration Best Practices

### Environment-Based Configuration
```python
# ✅ Use environment variables
import os
endpoint = os.getenv("SNOWPLOW_COLLECTOR_URL")
namespace = os.getenv("SNOWPLOW_NAMESPACE", "default")
```

### Retry Configuration
```python
# ✅ Configure intelligent retry behavior
EmitterConfiguration(
    max_retry_delay_seconds=120,
    custom_retry_codes={
        429: True,  # Retry rate limits
        500: True,  # Retry server errors
        400: False  # Don't retry bad requests
    }
)
```

## Quick Reference

### Import Checklist
- [ ] Import from `snowplow_tracker` package root
- [ ] Use `EmitterConfiguration` and `TrackerConfiguration`
- [ ] Import specific event classes from `snowplow_tracker.events`
- [ ] Use type hints from `snowplow_tracker.typing`

### Event Tracking Checklist
- [ ] Create tracker with `Snowplow.create_tracker()`
- [ ] Configure emitter with appropriate batch size
- [ ] Set subject context if tracking users
- [ ] Use appropriate event class for the use case
- [ ] Add custom contexts as `SelfDescribingJson`
- [ ] Call `flush()` before application shutdown
- [ ] Handle failures with callbacks

### Common Event Types
- `PageView`: Web page views
- `ScreenView`: Mobile app screens
- `StructuredEvent`: Generic events with 5 parameters
- `SelfDescribing`: Custom schema events
- `PagePing`: Engagement tracking

## Contributing to CLAUDE.md

When adding or updating content in this document, please follow these guidelines:

### File Size Limit
- **CLAUDE.md must not exceed 40KB** (currently ~19KB)
- Check file size after updates: `wc -c CLAUDE.md`
- Remove outdated content if approaching the limit

### Code Examples
- Keep all code examples **4 lines or fewer**
- Focus on the essential pattern, not complete implementations
- Use `// ❌` and `// ✅` to clearly show wrong vs right approaches

### Content Organization
- Add new patterns to existing sections when possible
- Create new sections sparingly to maintain structure
- Update the architectural principles section for major changes
- Ensure examples follow current codebase conventions

### Quality Standards
- Test any new patterns in actual code before documenting
- Verify imports and syntax are correct for the codebase
- Keep language concise and actionable
- Focus on "what" and "how", minimize "why" explanations

### Multiple CLAUDE.md Files
- **Directory-specific CLAUDE.md files** can be created for specialized modules
- Follow the same structure and guidelines as this root CLAUDE.md
- Keep them focused on directory-specific patterns and conventions
- Maximum 20KB per directory-specific CLAUDE.md file

### Instructions for LLMs
When editing files in this repository, **always check for CLAUDE.md guidance**:

1. **Look for CLAUDE.md in the same directory** as the file being edited
2. **If not found, check parent directories** recursively up to project root
3. **Follow the patterns and conventions** described in the applicable CLAUDE.md
4. **Prioritize directory-specific guidance** over root-level guidance when conflicts exist