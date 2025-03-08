from fastapi import responses
import pytest
from fastapi.testclient import TestClient
from ..main_router import router


client = TestClient(app=router)


@pytest.mark.parametrize(
    "group_name",
    [
        "ИКБО-17-22",
        "ИКБО-17-21",
        "Дзержинский Роман Игоревич",
        "ИКБО-15-21",
        "ИКБО-04-21"
    ]
)
def test_groups(group_name):
    response = client.get(f"/search/name={group_name}")
    assert response.status_code == 200
    assert response.json() != None

