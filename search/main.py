from fastapi import APIRouter, Depends
import requests
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy.orm.session import Session
from database.main import Alert, Day, Group, Schedule, SessionLocal, save_alerts_to_db, save_schedule_to_db
from ics_parser.main import parse_ics


app = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/search/name={group_name}')
async def get_group(group_name: str, db_session: Session = Depends(get_db)):
    search_response = requests.get(f'https://schedule-of.mirea.ru/schedule/api/search?limit=10&match={group_name}')
    print(search_response.status_code)
    if search_response.status_code != 200:
        return {"error": "Failed to fetch group data."}

    search_data = search_response.json()
    if not search_data["data"]:
        return {"error": "Group/teacher not found."}

    ical_link = search_data["data"][0].get("iCalLink")
    print(ical_link)
    if not ical_link:
        return {"error": "No iCal link found."}

    ical_response = requests.get(ical_link)
    print(ical_response.headers["Content-Length"])
    content_length = ical_response.headers["Content-Length"]
    if ical_response.status_code != 200:
        return {"error": "Failed to fetch schedule file."}

    group = db_session.query(Group).filter(Group.group_name == group_name).first()

    if group :
        if group.content_length == int(content_length):
            schedule_entries = (
                db_session.query(Schedule)
                .filter(Schedule.group_id == group.id)
                .all()
            )
            alerts = (
                db_session.query(Alert)
                .filter(Alert.group_id == group.id)
                .all()
            )

            schedule_data = {}
            for entry in schedule_entries:
                days = (
                    db_session.query(Day)
                    .filter(Day.schedule_id == entry.id)
                    .all()
                )
                week_type = entry.week_type

                if entry.day not in schedule_data:
                    schedule_data[entry.day] = {"odd": [], "even": []}

                for day in days:
                    schedule_data[entry.day][week_type].append({
                        "lesson": day.lesson_place,
                        "name": day.name,
                        "type": day.type,
                        "tutor": day.tutor,
                        "place": day.place
                    })

            alert_data = [
                {
                    "lesson": alert.lesson,
                    "name": alert.name,
                    "place": alert.place,
                    "next_name": alert.next_name,
                    "next_place": alert.next_place,
                    "alert_type": alert.alert_type,
                }
                for alert in alerts
            ]

            return {"alerts": alert_data, "schedule": schedule_data}
        if group.content_length != int(content_length):
            db_session.query(Group).filter(Group.id == group.id).delete()

    schedule = parse_ics(ical_response.text)
    alert = {"odd": [], "even": []}

    for day_info in schedule:
        day = day_info.get("day", "Unknown day")
        odd = day_info.get("odd", [])
        even = day_info.get("even", [])

        odd_flat = [lesson for sublist in odd if isinstance(sublist, list) for lesson in sublist]
        even_flat = [lesson for sublist in even if isinstance(sublist, list) for lesson in sublist]

        for week_type, lessons in [("odd", odd), ("even", even)]:
            for j in range(len(lessons) - 1):
                current_lesson = lessons[j][0] if lessons[j] else None
                next_lesson = None
                next_index = None

                for k in range(j + 1, len(lessons)):
                    if lessons[k]:
                        next_lesson = lessons[k][0]
                        next_index = k
                        break

                if current_lesson and next_lesson:
                    place = current_lesson.get("place", "")
                    next_place = next_lesson.get("place", "")
                    name = current_lesson.get("name", "Unknown")
                    next_name = next_lesson.get("name", "Unknown")

                    if next_index - j > 1:
                        alert[week_type].append({
                            "day": day,
                            "lesson": j+1,
                            "name": name,
                            "place": place,
                            "next_name": next_name,
                            "next_place": next_place,
                            "alert_type": "Большое окно"
                        })

                    elif place and next_place and place[0] != next_place[0] and j in [0, 2, 4, 5]:
                        alert[week_type].append({
                            "day": day,
                            "lesson": j+1,
                            "name": name,
                            "place": place,
                            "next_name": next_name,
                            "next_place": next_place,
                            "alert_type": "Маленький перерыв. Большое расстояние между кабинетами"
                        })
    print(schedule)
    print(alert)
    save_schedule_to_db(db_session=db_session, group_name=group_name, content_length=content_length, schedule_data=schedule)
    group = db_session.query(Group).filter(Group.group_name == group_name).first()
    if not group:
        return {"error": "Group not found in the database."}
    save_alerts_to_db(db_session=db_session, alerts=alert, group_id=group.id)

    return {"alerts": alert, "schedule": schedule}

