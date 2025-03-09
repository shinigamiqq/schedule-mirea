from ics import Calendar
from datetime import timezone, datetime


def clean_ics(ics_data):
    filtered_lines = []
    for line in ics_data.split("\n"):
        if not line.startswith("X-"):
            filtered_lines.append(line)
    return "\n".join(filtered_lines)

def get_weekday(dt):
    days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
    return days[dt.weekday()]

def is_odd_week(dt):
    start_date = datetime(2025, 2, 10, tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc)

    week_num = (dt - start_date).days // 7 + 1
    return week_num % 2 == 1

def parse_ics(ics_data):
    ics_data = clean_ics(ics_data)
    calendar = Calendar(ics_data)
    schedule = {}

    for event in calendar.events:
        dt_start = event.begin.datetime
        dt_end = event.end.datetime
        day = get_weekday(dt_start)

        lesson_info = {
            "weeks": None,
            "name": event.name,
            "type": event.categories.pop() if event.categories else "Неизвестно",
            "tutor": event.description.split("\n")[0].replace("Преподаватель: ", "") if event.description else "Неизвестно",
            "place": event.location if event.location else "Неизвестно",
            "link": None
        }

        week_type = "odd" if is_odd_week(dt_start) else "even"

        if day not in schedule:
            schedule[day] = {"day": day, "odd": [[] for _ in range(7)], "even": [[] for _ in range(7)]}

        lesson_times = ["09:00", "10:40", "12:40", "14:20", "16:20", "18:00", "19:40"]
        start_time = dt_start.strftime("%H:%M")

        if start_time in lesson_times:
            index = lesson_times.index(start_time)
            schedule[day][week_type][index].append(lesson_info)

    return list(schedule.values())

