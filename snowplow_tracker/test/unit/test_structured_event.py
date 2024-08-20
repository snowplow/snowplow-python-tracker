from snowplow_tracker.events.structured_event import StructuredEvent


class TestStructuredEvent:
    def test_getters(self):
        se = StructuredEvent("category", "action", "label", "property", 1)
        assert se.category == "category"
        assert se.action == "action"
        assert se.label == "label"
        assert se.property_ == "property"
        assert se.value == 1

    def test_setters(self):
        se = StructuredEvent("category", "action")
        se.category = "new_category"
        se.action = "new_action"
        se.label = "new_label"
        se.property_ = "new_property"
        se.value = 2
        assert se.category == "new_category"
        assert se.action == "new_action"
        assert se.label == "new_label"
        assert se.property_ == "new_property"
        assert se.value == 2
