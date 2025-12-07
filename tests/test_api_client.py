import requests_mock
from api_client import search_exercises

def test_search_exercises_handles_missing_gifurl(requests_mock):
    """API returns exercises even if gifUrl is missing."""
    payload = [{"name": "curl", "target": "biceps"}]  # no gifUrl
    requests_mock.get("https://example.api/exercises?query=biceps", json=payload)
    results = search_exercises("biceps")
    assert len(results) == 1
    assert "gifUrl" in results[0]
