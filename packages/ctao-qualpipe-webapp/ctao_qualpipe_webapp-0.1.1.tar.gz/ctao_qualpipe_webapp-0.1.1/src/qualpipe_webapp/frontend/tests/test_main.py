import re

import pytest
from fastapi.testclient import TestClient

from qualpipe_webapp.frontend.main import app

client = TestClient(app)


def assert_html_utf8(response):
    """Check if 'html' and 'utf-8' is in response."""
    assert "text/html" in response.headers["content-type"]
    assert "charset=utf-8" in response.headers["content-type"]


def test_read_home():
    """Test the home page endpoint."""
    response = client.get("/home")
    assert response.status_code == 200
    assert_html_utf8(response)
    assert "home" in response.text or "<html" in response.text
    assert '<nav class="first-nav' in response.text
    assert '<nav class="second-nav' not in response.text


scopes = ["LSTs", "MSTs", "SSTs"]
pages = [
    ("", "{scope}"),
    ("/pointings", "Pointings"),
    ("/event_rates", "Event rates"),
    ("/trigger_tags", "Trigger tags"),
    ("/interleaved_pedestals", "Interleaved pedestals"),
    ("/interleaved_flat_field_charge", "Interleaved flat field charge"),
    ("/interleaved_flat_field_time", "Interleaved flat field time"),
    ("/cosmics", "Cosmics"),
    ("/pixel_problems", "Pixel problems"),
    ("/muons", "Muons"),
    ("/interleaved_pedestals_averages", "Interleaved pedestals averages"),
    ("/interleaved_FF_averages", "Interleaved FF averages"),
    ("/cosmics_averages", "Cosmics averages"),
]


@pytest.mark.parametrize("scope", scopes)
@pytest.mark.parametrize(("page", "keyword"), pages)
def test_read_scopes(scope, page, keyword):
    """Test the scope and page endpoints."""
    endpoint = f"/{scope}{page}"
    expected_keyword = keyword.format(scope=scope)
    response = client.get(endpoint)
    assert response.status_code == 200
    assert_html_utf8(response)
    assert expected_keyword in response.text or "<!DOCTYPE html>" in response.text
    assert '<nav class="first-nav' in response.text
    assert re.search(r"<nav\s+class=\"second-nav", response.text)
    expected_keyword = expected_keyword.replace(" ", "[\\s]*")
    pattern = (
        rf'href="{re.escape(endpoint)}"[\w\s\n=:;<>\".\-]*>{expected_keyword}</a[\s]*>'
    )
    assert re.search(pattern, response.text)


def test_not_found():
    """Test the 404 page."""
    response = client.get("/nonexistent-page")
    assert response.status_code == 404
    assert_html_utf8(response)
    assert "404" in response.text or "not found" in response.text.lower()
