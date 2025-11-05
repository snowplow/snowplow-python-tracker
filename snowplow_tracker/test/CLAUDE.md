# Snowplow Python Tracker Tests - CLAUDE.md

## Directory Overview

The `test/` directory contains comprehensive test suites for the Snowplow Python Tracker. Tests are organized into unit tests (isolated component testing) and integration tests (end-to-end collector communication). The test suite uses pytest and unittest.mock for mocking, with freezegun for time-based testing.

## Test Organization

```
test/
├── unit/                    # Isolated component tests
│   ├── test_tracker.py      # Tracker class tests
│   ├── test_emitters.py     # Emitter functionality
│   ├── test_event.py        # Base event class
│   ├── test_payload.py      # Payload construction
│   ├── test_contracts.py    # Validation logic
│   └── test_*.py            # Other component tests
└── integration/             # End-to-end tests
    └── test_integration.py  # Collector communication
```

## Core Testing Patterns

### Mock Pattern for Emitters
```python
# ✅ Mock emitter for isolated tracker testing
@mock.patch('snowplow_tracker.emitters.Emitter')
def test_tracker_tracks_event(mock_emitter):
    tracker = Tracker("test", mock_emitter)
    tracker.track(PageView(page_url="test.com"))
    mock_emitter.input.assert_called_once()

# ❌ Don't test with real network calls in unit tests
def test_tracker():
    emitter = Emitter("https://real-collector.com")
```

### Contract Testing Pattern
```python
# ✅ Use ContractsDisabled context manager
class ContractsDisabled:
    def __enter__(self):
        disable_contracts()
    def __exit__(self, type, value, traceback):
        enable_contracts()

with ContractsDisabled():
    # Test invalid inputs without raising
    tracker.track_page_view(None)

# ❌ Don't disable contracts globally
disable_contracts()
# ... rest of test file
```

### Time-Based Testing Pattern
```python
# ✅ Use freezegun for deterministic timestamps
from freezegun import freeze_time

@freeze_time("2024-01-01 12:00:00")
def test_event_timestamp():
    event = PageView(page_url="test.com")
    # Timestamp will be consistent

# ❌ Don't use actual system time
import time
timestamp = time.time()  # Non-deterministic
```

### UUID Mocking Pattern
```python
# ✅ Mock UUID generation for predictable IDs
@mock.patch('snowplow_tracker.tracker.Tracker.get_uuid')
def test_event_id(mock_uuid):
    mock_uuid.return_value = "test-uuid-123"
    tracker.track(event)
    assert payload["eid"] == "test-uuid-123"

# ❌ Don't rely on random UUIDs
event_id = tracker.get_uuid()  # Different each run
```

## Unit Test Patterns

### Payload Testing
```python
# ✅ Test payload field presence and values
def test_payload_construction():
    payload = Payload()
    payload.add("e", "pv")
    payload.add("url", "https://test.com")
    
    result = payload.get()
    assert result["e"] == "pv"
    assert result["url"] == "https://test.com"

# ✅ Test JSON encoding
def test_payload_json_encoding():
    payload.add_json({"key": "value"}, True, "cx", "co")
    assert "cx" in payload.get()  # Base64 encoded
```

### Event Testing
```python
# ✅ Test event construction with all parameters
def test_page_view_complete():
    context = SelfDescribingJson(schema, data)
    subject = Subject()
    
    event = PageView(
        page_url="https://test.com",
        page_title="Test",
        context=[context],
        event_subject=subject,
        true_timestamp=1234567890
    )
    
    assert event.page_url == "https://test.com"
    assert len(event.context) == 1

# ❌ Don't test internal implementation details
def test_private_methods():
    event._internal_method()  # Testing private methods
```

### Emitter Testing
```python
# ✅ Mock HTTP requests for emitter tests
@mock.patch('requests.post')
def test_emitter_sends_events(mock_post):
    mock_post.return_value.status_code = 200
    
    emitter = Emitter("https://collector.test")
    emitter.input({"e": "pv"})
    emitter.flush()
    
    mock_post.assert_called_once()

# ✅ Test retry logic
def test_emitter_retry_on_failure(mock_post):
    mock_post.return_value.status_code = 500
    emitter.custom_retry_codes = {500: True}
    # Verify retry behavior
```

### Contract Validation Testing
```python
# ✅ Test validation rules
def test_non_empty_string_validation():
    with self.assertRaises(ValueError):
        non_empty_string("")
    
    non_empty_string("valid")  # Should not raise

# ✅ Test form element validation
def test_form_element_contract():
    valid_element = {
        "name": "field1",
        "value": "test",
        "nodeName": "INPUT",
        "type": "text"
    }
    form_element(valid_element)  # Should not raise
```

## Integration Test Patterns

### Mock Collector Pattern
```python
# ✅ Use micro mock collector for integration tests
from http.server import HTTPServer, BaseHTTPRequestHandler

class MockCollector(BaseHTTPRequestHandler):
    def do_POST(self):
        # Capture and validate payload
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        # Store for assertions
        self.send_response(200)

# Start mock collector in test
server = HTTPServer(('localhost', 9090), MockCollector)
```

### End-to-End Testing
```python
# ✅ Test complete tracking flow
def test_end_to_end_tracking():
    tracker = Snowplow.create_tracker(
        namespace="test",
        endpoint="http://localhost:9090"
    )
    
    # Track multiple events
    tracker.track(PageView(page_url="test1.com"))
    tracker.track(StructuredEvent("cat", "act"))
    tracker.flush()
    
    # Verify collector received both events
    assert len(received_events) == 2
```

## Testing Best Practices

### Test Isolation
```python
# ✅ Clean up after each test
def setUp(self):
    Snowplow.reset()  # Clear all trackers

def tearDown(self):
    # Clean up any test artifacts
    if hasattr(self, 'server'):
        self.server.shutdown()

# ❌ Don't leave state between tests
class TestSuite:
    shared_tracker = Tracker(...)  # Shared state!
```

### Assertion Patterns
```python
# ✅ Use specific assertions
assert event.page_url == "https://expected.com"
assert "e" in payload.get()
mock_func.assert_called_with(expected_arg)

# ❌ Avoid generic assertions
assert event  # Too vague
assert payload.get()  # What are we checking?
```

### Mock Management
```python
# ✅ Use patch decorators or context managers
@mock.patch('snowplow_tracker.tracker.uuid.uuid4')
def test_with_mock(mock_uuid):
    mock_uuid.return_value = "test-id"

# ✅ Clean up patches
def create_patch(self, name):
    patcher = mock.patch(name)
    thing = patcher.start()
    self.addCleanup(patcher.stop)
    return thing
```

## Common Test Scenarios

### Testing Event Contexts
```python
# ✅ Test context encoding and attachment
def test_event_with_multiple_contexts():
    contexts = [
        SelfDescribingJson(schema1, data1),
        SelfDescribingJson(schema2, data2)
    ]
    event = PageView(page_url="test", context=contexts)
    
    payload = event.build_payload(True, None, None)
    cx_data = json.loads(base64.b64decode(payload.get()["cx"]))
    assert len(cx_data["data"]) == 2
```

### Testing Failure Scenarios
```python
# ✅ Test failure callbacks
def test_emitter_failure_callback():
    failed_events = []
    
    def on_failure(count, events):
        failed_events.extend(events)
    
    emitter = Emitter(
        "https://invalid.collector",
        on_failure=on_failure
    )
    # Trigger failure and verify callback
```

### Testing Async Behavior
```python
# ✅ Test async emitter threading
def test_async_emitter():
    emitter = AsyncEmitter("https://collector.test")
    
    # Track events
    for i in range(100):
        emitter.input({"e": "pv", "url": f"test{i}.com"})
    
    # Wait for flush
    emitter.flush()
    time.sleep(1)  # Allow async processing
    
    # Verify all events sent
```

## Test Utilities

### Helper Functions
```python
# ✅ Create reusable test helpers
def create_test_tracker(namespace="test"):
    emitter = mock.MagicMock()
    return Tracker(namespace, emitter)

def create_test_event():
    return PageView(page_url="https://test.com")

# ❌ Don't duplicate test setup
def test_one():
    emitter = mock.MagicMock()
    tracker = Tracker("test", emitter)
    # ... repeated in every test
```

## Performance Testing

### Load Testing Pattern
```python
# ✅ Test tracker under load
def test_high_volume_tracking():
    tracker = create_test_tracker()
    
    start = time.time()
    for i in range(10000):
        tracker.track(PageView(page_url=f"test{i}.com"))
    
    duration = time.time() - start
    assert duration < 5.0  # Performance threshold
```

## Quick Reference

### Test File Naming
- Unit tests: `test_<component>.py`
- Integration tests: `test_integration_<feature>.py`
- Test classes: `Test<Component>`
- Test methods: `test_<scenario>`

### Essential Test Imports
```python
import unittest
import unittest.mock as mock
from freezegun import freeze_time
from snowplow_tracker.contracts import ContractsDisabled
```

### Common Mock Targets
- `snowplow_tracker.tracker.Tracker.get_uuid`
- `requests.post` / `requests.get`
- `time.time`
- `snowplow_tracker.emitters.Emitter.sync_flush`

## Contributing to test/CLAUDE.md

When adding or modifying tests:

1. **Maintain test isolation** - Each test should be independent
2. **Mock external dependencies** - No real network calls in unit tests
3. **Use descriptive test names** - Clear what is being tested
4. **Test both success and failure paths** - Include edge cases
5. **Keep tests fast** - Mock time-consuming operations
6. **Document complex test scenarios** - Add comments for clarity