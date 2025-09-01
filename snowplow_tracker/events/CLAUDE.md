# Snowplow Event Types - CLAUDE.md

## Directory Overview

The `events/` directory contains all event type implementations for the Snowplow Python Tracker. Each event class represents a specific type of analytics event that can be sent to Snowplow collectors. All events inherit from the base `Event` class and follow a consistent pattern for construction, validation, and payload generation.

## Event Class Hierarchy

```
Event (base class)
├── PageView         # Web page view tracking
├── PagePing         # Page engagement/heartbeat
├── ScreenView       # Mobile/app screen views  
├── StructuredEvent  # Generic 5-parameter events
└── SelfDescribing   # Custom schema events
```

## Core Event Patterns

### Event Construction Pattern
```python
# ✅ Use keyword arguments for clarity
event = PageView(
    page_url="https://example.com",
    page_title="Homepage",
    referrer="https://google.com"
)

# ❌ Don't use positional arguments
event = PageView("https://example.com", "Homepage")
```

### Event Context Pattern
```python
# ✅ Add contexts as SelfDescribingJson list
geo_context = SelfDescribingJson(
    "iglu:com.acme/geolocation/jsonschema/1-0-0",
    {"latitude": 40.0, "longitude": -73.0}
)
event = PageView(page_url="...", context=[geo_context])

# ❌ Don't use raw dictionaries for context
event.context = [{"latitude": 40.0}]  # Missing schema!
```

### Event Subject Override Pattern
```python
# ✅ Override tracker subject for specific event
special_subject = Subject()
special_subject.set_user_id("anonymous_user")
event = StructuredEvent(
    category="shop",
    action="view",
    event_subject=special_subject
)

# ❌ Don't modify shared subject
tracker.subject.set_user_id("temp")  # Affects all events
```

### True Timestamp Pattern
```python
# ✅ Use milliseconds for true_timestamp
import time
timestamp_ms = time.time() * 1000
event = PageView(
    page_url="...",
    true_timestamp=timestamp_ms
)

# ❌ Don't use seconds
event = PageView(true_timestamp=time.time())
```

## Event-Specific Patterns

### PageView Events
```python
# ✅ Complete PageView with all fields
page_view = PageView(
    page_url="https://example.com/products",
    page_title="Products",
    referrer="https://example.com/home"
)

# ❌ Missing required page_url
page_view = PageView(page_title="Products")
```

### StructuredEvent Pattern
```python
# ✅ Use descriptive category/action pairs
event = StructuredEvent(
    category="ecommerce",
    action="add-to-cart",
    label="SKU-123",
    property_="size:XL",
    value=29.99
)

# ❌ Generic naming loses meaning
event = StructuredEvent("event", "click")
```

### SelfDescribing Events
```python
# ✅ Custom events with Iglu schemas
purchase_event = SelfDescribing(
    SelfDescribingJson(
        "iglu:com.acme/purchase/jsonschema/2-0-0",
        {
            "orderId": "ORD-123",
            "total": 99.99,
            "currency": "USD"
        }
    )
)

# ❌ Missing schema version
event = SelfDescribing(
    SelfDescribingJson("iglu:com.acme/purchase", {...})
)
```

### ScreenView Pattern (Mobile)
```python
# ✅ Mobile screen tracking with ID
screen = ScreenView(
    name="ProductDetailScreen",
    id_="screen-456",
    previous_name="ProductListScreen"
)

# ❌ Using PageView for mobile apps
page = PageView(page_url="app://product-detail")
```

## Event Validation Rules

### Required Fields by Event Type
- **PageView**: `page_url` (required), `page_title`, `referrer`
- **StructuredEvent**: `category`, `action` (required), `label`, `property_`, `value`
- **SelfDescribing**: `event_json` (SelfDescribingJson required)
- **ScreenView**: `name` or `id_` (at least one required)
- **PagePing**: `page_url` (required)

### Schema Validation Pattern
```python
# ✅ Validate schema format
SCHEMA_PATTERN = r"^iglu:[a-zA-Z0-9-_.]+/[a-zA-Z0-9-_]+/"
SCHEMA_PATTERN += r"[a-zA-Z0-9-_]+/[0-9]+-[0-9]+-[0-9]+$"

# ❌ Invalid schema formats
"iglu:com.acme/event"  # Missing version
"com.acme/event/1-0-0"  # Missing iglu: prefix
```

## Payload Building Pattern

### Internal Payload Construction
```python
# ✅ Event classes handle payload internally
def build_payload(self, encode_base64, json_encoder, subject):
    # Add event-specific fields
    self.payload.add("e", "pv")  # Page view type
    self.payload.add("url", self.page_url)
    
    # Let base class handle common fields
    return super().build_payload(encode_base64, json_encoder, subject)

# ❌ Don't expose payload building to users
event.payload = Payload()
event.payload.add("custom", "field")
```

## Testing Event Classes

### Unit Test Pattern
```python
# ✅ Test event construction and validation
def test_page_view_required_fields():
    with self.assertRaises(TypeError):
        PageView()  # Missing required page_url
    
    event = PageView(page_url="https://test.com")
    assert event.page_url == "https://test.com"

# ✅ Test payload generation
def test_event_payload():
    event = PageView(page_url="https://test.com")
    payload = event.build_payload(False, None, None)
    assert payload.get()["url"] == "https://test.com"
```

### Context Testing Pattern
```python
# ✅ Test context attachment
def test_event_context():
    context = SelfDescribingJson(schema, data)
    event = PageView(page_url="...", context=[context])
    
    payload = event.build_payload(True, None, None)
    assert "cx" in payload.get()  # Base64 context
```

## Common Event Pitfalls

### Timestamp Confusion
```python
# ❌ Mixing timestamp types
event.true_timestamp = "2024-01-01"  # String not allowed
event.true_timestamp = datetime.now()  # Use milliseconds

# ✅ Consistent millisecond timestamps
event.true_timestamp = int(time.time() * 1000)
```

### Context Array Management
```python
# ❌ Modifying context after creation
event.context.append(new_context)  # Unexpected behavior

# ✅ Set complete context at creation
all_contexts = [context1, context2]
event = PageView(page_url="...", context=all_contexts)
```

### Schema Version Control
```python
# ❌ Hardcoding schema versions
schema = "iglu:com.acme/event/jsonschema/1-0-0"

# ✅ Centralize schema definitions
PURCHASE_SCHEMA = "iglu:com.acme/purchase/jsonschema/2-1-0"
event = SelfDescribing(SelfDescribingJson(PURCHASE_SCHEMA, data))
```

## Event Migration Guide

### Upgrading Event Schemas
```python
# From version 1-0-0 to 2-0-0
# ✅ Handle backward compatibility
def create_purchase_event(data):
    if "items" in data:  # New schema
        schema = "iglu:.../purchase/jsonschema/2-0-0"
    else:  # Old schema
        schema = "iglu:.../purchase/jsonschema/1-0-0"
    
    return SelfDescribing(SelfDescribingJson(schema, data))
```

## Quick Reference

### Event Type Selection
- **PageView**: Traditional web page tracking
- **ScreenView**: Mobile app screen tracking
- **StructuredEvent**: Generic business events
- **SelfDescribing**: Complex custom events
- **PagePing**: Engagement/time-on-page tracking

### Event Field Checklist
- [ ] Required fields provided
- [ ] Timestamps in milliseconds
- [ ] Contexts as SelfDescribingJson array
- [ ] Valid Iglu schema format
- [ ] Event-specific subject if needed

### Common Event Methods
- `build_payload()`: Internal payload generation
- `event_subject`: Per-event user context
- `context`: Custom context array
- `true_timestamp`: User-defined timestamp

## Contributing to events/CLAUDE.md

When modifying event implementations or adding new event types:

1. **Follow the Event base class pattern** - All events must inherit from Event
2. **Implement required abstract methods** - Ensure payload building works correctly
3. **Document required fields** - Update this file with new event requirements
4. **Add comprehensive tests** - Test construction, validation, and payload generation
5. **Maintain backward compatibility** - Don't break existing event APIs
6. **Update schema constants** - Add new schemas to constants.py if needed