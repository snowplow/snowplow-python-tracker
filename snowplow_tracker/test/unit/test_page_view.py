import pytest

from snowplow_tracker.events.page_view import PageView


class TestPageView:
    def test_getters(self):
        pv = PageView("url", "title", "referrer")
        assert pv.page_url == "url"
        assert pv.page_title == "title"
        assert pv.referrer == "referrer"

    def test_setters(self):
        pv = PageView("url", "title", "referrer")
        pv.page_url = "new_url"
        pv.page_title = "new_title"
        pv.referrer = "new_referrer"
        assert pv.page_url == "new_url"
        assert pv.page_title == "new_title"
        assert pv.referrer == "new_referrer"

    def test_page_url_non_empty_string(self):
        pv = PageView("url")
        pv.page_url = "new_url"
        assert pv.page_url == "new_url"
        with pytest.raises(ValueError):
            pv.page_url = ""
