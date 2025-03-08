import pytest
from fastapi.testclient import TestClient
from ..main_router import router


client = TestClient(app=router)


with open("tests/ics_data.ics", "r", encoding="utf-8") as f:
    ics_data = f.read()

@pytest.fixture
def mock_response_api(requests_mock):
    requests_mock.get(
        "https://schedule-of.mirea.ru/schedule/api/search?limit=10&match=%D0%98%D0%9A%D0%91%D0%9E-17-22",
      json = {"data":[{"id":517,"targetTitle":"ИКБО-17-22","fullTitle":"ИКБО-17-22","scheduleTarget":1,"iCalLink":"https://schedule-of.mirea.ru/schedule/api/ical/1/517","scheduleImageLink":"https://schedule-of.mirea.ru/schedule/genericschedule?type=1&id=517&asImage=True","scheduleUpdateImageLink":"https://schedule-of.mirea.ru/schedule/genericupdate?type=1&id=517&asImage=True","scheduleUIAddToCalendarLink":"https://schedule-of.mirea.ru/?s=1_517&addToCal=1_517"}],"nextPageToken":None}
)
@pytest.fixture
def mock_response_api2(requests_mock):
    requests_mock.get(
        "https://schedule-of.mirea.ru/schedule/api/ical/1/517",
        headers={"Content-Length": "31305"},
        text = ics_data
    )
@pytest.mark.parametrize(
    "expected_data",
    [
        {
        "alerts": {
    "odd": [
      {
        "day": "пятница",
        "lesson": 3,
        "name": "ПР Основы сетевых технологий",
        "place": "Б-211 (В-78)",
        "next_name": "ПР Системы управления производством",
        "next_place": "Г-101 (В-78)",
        "alert_type": "Маленький перерыв. Большое расстояние между кабинетами"
      },
      {
        "day": "понедельник",
        "lesson": 3,
        "name": "ПР Моделирование сред и разработка приложений виртуальной и дополненной реальности",
        "place": "И-205-б (В-78)",
        "next_name": "ПР Исследование операций",
        "next_place": "А-150 (В-78)",
        "alert_type": "Маленький перерыв. Большое расстояние между кабинетами"
      },
      {
        "day": "суббота",
        "lesson": 3,
        "name": "ПР Моделирование сред и разработка приложений виртуальной и дополненной реальности",
        "place": "И-205-б (В-78)",
        "next_name": "ПР Исследование операций",
        "next_place": "А-150 (В-78)",
        "alert_type": "Маленький перерыв. Большое расстояние между кабинетами"
      },
      {
        "day": "вторник",
        "lesson": 5,
        "name": "ЛК Системное администрирование",
        "place": "А-18 (В-78)",
        "next_name": "ПР Системное администрирование",
        "next_place": "И-202-б (В-78)",
        "alert_type": "Маленький перерыв. Большое расстояние между кабинетами"
      },
      {
        "day": "четверг",
        "lesson": 1,
        "name": "ЛК Основы сетевых технологий",
        "place": "А-9 (В-78)",
        "next_name": "ПР Проектирование информационных систем",
        "next_place": "ИВЦ-109 (В-78)",
        "alert_type": "Маленький перерыв. Большое расстояние между кабинетами"
      }
    ],
    "even": [
      {
        "day": "пятница",
        "lesson": 3,
        "name": "ПР Основы сетевых технологий",
        "place": "Б-211 (В-78)",
        "next_name": "ПР Системы управления производством",
        "next_place": "Г-101 (В-78)",
        "alert_type": "Маленький перерыв. Большое расстояние между кабинетами"
      },
      {
        "day": "понедельник",
        "lesson": 4,
        "name": "ПР Безопасность жизнедеятельности",
        "place": "ВУЦ (У-7/1)",
        "next_name": "ЛК Безопасность жизнедеятельности",
        "next_place": "Дистанционно (СДО)",
        "alert_type": "Большое окно"
      },
      {
        "day": "суббота",
        "lesson": 3,
        "name": "ПР Моделирование сред и разработка приложений виртуальной и дополненной реальности",
        "place": "И-205-б (В-78)",
        "next_name": "ПР Исследование операций",
        "next_place": "А-150 (В-78)",
        "alert_type": "Маленький перерыв. Большое расстояние между кабинетами"
      },
      {
        "day": "вторник",
        "lesson": 5,
        "name": "ЛК Системное администрирование",
        "place": "А-18 (В-78)",
        "next_name": "ПР Системное администрирование",
        "next_place": "И-202-б (В-78)",
        "alert_type": "Маленький перерыв. Большое расстояние между кабинетами"
      },
      {
        "day": "четверг",
        "lesson": 1,
        "name": "ЛК Системы управления производством",
        "place": "А-9 (В-78)",
        "next_name": "ПР Проектирование информационных систем",
        "next_place": "ИВЦ-109 (В-78)",
        "alert_type": "Маленький перерыв. Большое расстояние между кабинетами"
      }
    ]
  }
        }
    ]
)
def test_api(mock_response_api, mock_response_api2, expected_data):
    response = client.get(f"search/name=ИКБО-17-22")
    print(response.json())
    print("Ответ ICS:", response.text)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["alerts"] == expected_data["alerts"]
