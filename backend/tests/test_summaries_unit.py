import pytest
from datetime import datetime, timezone
from app.api import crud, summaries

def test_create_summary(test_app, monkeypatch):
    test_request_payload = {"url": "https://www.example.com"}
    test_response_payload = {"id": 1, "url": "https://www.example.com/"}
    
    async def mock_post(payload):
        return 1
    monkeypatch.setattr(crud, "post", mock_post)
    
    response = test_app.post("api/summarize", json=test_request_payload)
    assert response.status_code == 201
    assert response.json() == test_response_payload
    
    

def test_create_summaries_invalid_json(test_app):
    response = test_app.post("api/summarize", json={})
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": {},
                "loc": ["body", "url"],
                "msg": "Field required",
                "type": "missing",
            }
        ]
    }
    
    response = test_app.post("api/summarize", json={"url": "invalid://url"})
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "URL scheme should be 'http' or 'https'"
    
def test_read_summary(test_app, monkeypatch):
    test_data = {
        "id": 1,
        "url": "https://www.example.com",
        "summary": "This is a summary.",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    async def mock_get(summary_id):
        return test_data if summary_id == 1 else None
    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("api/summarize/1")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == test_data["id"]
    assert response_data["url"] == test_data["url"]
    assert response_data["summary"] == test_data["summary"]
    assert response_data["created_at"]

def test_read_summary_incorrect_id(test_app, monkeypatch):
    async def mock_get(summary_id):
        return None
    monkeypatch.setattr(crud, "get", mock_get)
    
    response = test_app.get("api/summarize/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Summary not found"}

def test_read_all_summaries(test_app, monkeypatch):
    test_data = [
        {
            "id": 1,
            "url": "https://www.example.com",
            "summary": "This is a summary.",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "id": 2,
            "url": "https://www.example2.com",
            "summary": "This is another summary.",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    ]

    async def mock_get_all():
        return test_data
    monkeypatch.setattr(crud, "get_all", mock_get_all)

    response = test_app.get("api/summarize")
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == len(test_data)
    for i, item in enumerate(response_data):
        assert item["id"] == test_data[i]["id"]
        assert item["url"] == test_data[i]["url"]
        assert item["summary"] == test_data[i]["summary"]
        assert item["created_at"]

def test_remove_summary(test_app, monkeypatch):
    async def mock_delete(summary_id):
        return {"id": summary_id, "url": "https://www.example.com"} if summary_id == 1 else None
    monkeypatch.setattr(crud, "delete", mock_delete)
    
    
    response = test_app.delete("api/summarize/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "url": "https://www.example.com/"}

def test_remove_summary_incorrect_id(test_app, monkeypatch):
    async def mock_delete(summary_id):
        return None
    monkeypatch.setattr(crud, "delete", mock_delete)
    
    response = test_app.delete("api/summarize/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Summary not found"}

def test_update_summary(test_app, monkeypatch):
    test_request_payload = {"url": "https://www.foobar.com", "summary": "Updated summary"}
    test_response_payload = {
        "id": 1,
        "url": "https://www.foobar.com",
        "summary": "Updated summary",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    async def mock_put(summary_id, payload):
        return test_response_payload if summary_id == 1 else None
    monkeypatch.setattr(crud, "put", mock_put)

    response = test_app.put("api/summarize/1", json=test_request_payload)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == test_response_payload["id"]
    assert response_data["url"] == test_response_payload["url"]
    assert response_data["summary"] == test_response_payload["summary"]
    assert response_data["created_at"]

@pytest.mark.parametrize(
    "summary_id, payload, expected_status, expected_response",
    [
        (
            9999,
            {"url": "https://www.foobar.com", "summary": "Updated summary"},
            404,
            {"detail": "Summary not found"},
        ),
        (
            0,
            {"url": "https://www.foobar.com", "summary": "Updated summary"},
            422,
            {
                "detail": [
                    {
                        "type": "greater_than",
                        "loc": ["path", "summary_id"],
                        "msg": "Input should be greater than 0",
                        "input": "0",
                        "ctx": {"gt": 0},
                    }
                ]
            },
        ),
        (
            1,
            {},
            422,
            {
                "detail": [
                    {"input": {}, "loc": ["body", "url"], "msg": "Field required", "type": "missing"},
                    {"input": {}, "loc": ["body", "summary"], "msg": "Field required", "type": "missing"},
                ]
            },
        ),
        (
            1,
            {"url": "https://www.foobar.com"},
            422,
            {
                "detail": [
                    {
                        "input": {"url": "https://www.foobar.com"},
                        "loc": ["body", "summary"],
                        "msg": "Field required",
                        "type": "missing",
                    }
                ]
            },
        ),
    ],
)

def test_update_summary_invalid(test_app, monkeypatch, summary_id, payload, expected_status, expected_response):
    async def mock_put(summary_id, payload):
        return None

    monkeypatch.setattr(crud, "put", mock_put)
    response = test_app.put(f"api/summarize/{summary_id}", json=payload)
    assert response.status_code == expected_status
    assert response.json() == expected_response
