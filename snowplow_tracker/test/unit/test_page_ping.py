import pytest

from snowplow_tracker.events.page_ping import PagePing


class TestPagePing:
    def test_getters(self):
        pp = PagePing("url", "title", "referrer", 1, 2, 3, 4)
        assert pp.page_url == "url"
        assert pp.page_title == "title"
        assert pp.referrer == "referrer"
        assert pp.min_x == 1
        assert pp.max_x == 2
        assert pp.min_y == 3
        assert pp.max_y == 4

    def test_setters(self):
        pp = PagePing("url")
        pp.page_title = "title"
        pp.referrer = "referrer"
        pp.min_x = 1
        pp.max_x = 2
        pp.min_y = 3
        pp.max_y = 4
        assert pp.page_title == "title"
        assert pp.referrer == "referrer"
        assert pp.min_x == 1
        assert pp.max_x == 2
        assert pp.min_y == 3
        assert pp.max_y == 4
        assert pp.page_url == "url"

    def test_page_url_non_empty_string(self):
        pp = PagePing("url")
        pp.page_url = "new_url"
        assert pp.page_url == "new_url"
        with pytest.raises(ValueError):
            pp.page_url = ""
