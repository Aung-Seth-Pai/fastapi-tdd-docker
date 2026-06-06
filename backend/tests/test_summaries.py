
async def test_create_summary(test_app_with_db):
    response = await test_app_with_db.post("api/summarize", json={"url": "https://www.example.com"})
    assert response.status_code == 201
    response_data = response.json()
    assert isinstance(response_data["id"], int)
    assert response_data["url"] == "https://www.example.com/"


async def test_create_summary_invalid_json(test_app_with_db):
    response = await test_app_with_db.post("api/summarize", json={"invalid_field": "abcd"})
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": {"invalid_field": "abcd"},
                "loc": ["body", "url"],
                "msg": "Field required",
                "type": "missing",
            }
        ]
    }


async def test_create_summary_invalid_url(test_app_with_db):
    response = await test_app_with_db.post("api/summarize", json={"url": "invalid_url"})
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": "invalid_url",
                "loc": ["body", "url"],
                "msg": "Input should be a valid URL, relative URL without a base",
                "type": "url_parsing",
                "ctx": {"error": "relative URL without a base"},
            }
        ]
    }


async def test_read_summary(test_app_with_db):
    response = await test_app_with_db.post("/api/summarize", json={"url": "https://www.example.com"})
    summary_id = response.json()["id"]

    response = await test_app_with_db.get(f"/api/summarize/{summary_id}")
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["id"] == summary_id
    assert response_data["url"] == "https://www.example.com/"
    assert response_data["summary"]
    assert response_data["created_at"]


async def test_read_summary_incorrect_id(test_app_with_db):
    response = await test_app_with_db.get("/api/summarize/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Summary not found"}


async def test_read_all_summaries(test_app_with_db):
    response = await test_app_with_db.post("/api/summarize", json={"url": "https://www.example.com"})
    summary_id = response.json()["id"]

    response = await test_app_with_db.get("/api/summarize")
    assert response.status_code == 200

    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(list(filter(lambda d: d["id"] == summary_id, response_data))) == 1
