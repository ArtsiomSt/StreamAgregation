import json

from httpx import AsyncClient

with open("tests/test_auth/requests_auth.json", "r") as json_requests_file:
    json_requests = json.loads(json_requests_file.read())


async def get_auth_headers(client: AsyncClient) -> dict:
    valid_login_request: dict = json_requests["login"]["request"]
    response = await client.post("/auth/token", json=valid_login_request)
    response_json: dict = response.json()
    assert response.status_code == 200
    return {"Authorization": "Bearer " + response_json["access_token"]}
