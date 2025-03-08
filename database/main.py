from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Time, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import Session
import psycopg2

DATABASE_URL = "postgresql://postgres:postgres@192.168.0.120:5432/schedule"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Group(Base):
    __tablename__ = "mirea_group"

    id = Column(Integer, primary_key=True, index=True)
    group_name = Column(String, index=True)
    content_length =Column(Integer)

    schedule = relationship("Schedule", back_populates="group")
    alerts = relationship("Alert", back_populates="group")
class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("mirea_group.id"))
    day = Column(String)
    week_type = Column(String)

    group = relationship("Group", back_populates="schedule")

class Day(Base):
    __tablename__ = "day"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedule.id"))
    name = Column(String)
    type = Column(String)
    tutor = Column(String)
    place = Column(String)
    lesson_place = Column(Integer)

class Alert(Base):
    __tablename__ = "alert"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("mirea_group.id"))
    lesson = Column(String)
    name = Column(String)
    place = Column(String)
    next_name = Column(String)
    next_place = Column(String)
    alert_type = Column(String)

    group = relationship("Group", back_populates="alerts")

def init_db():
    Base.metadata.create_all(bind=engine)

def save_schedule_to_db(db_session: Session, group_name: str, content_length: str, schedule_data: list):
    group = db_session.query(Group).filter_by(group_name=group_name).first()
    if not group:
        group = Group(group_name=group_name, content_length=int(content_length))
        db_session.add(group)
        db_session.commit()

    for day_info in schedule_data:
        day = day_info.get("day", "Unknown day")
        for week_type in ["odd", "even"]:
            schedule = Schedule(
                group_id=group.id,
                day=day,
                week_type=week_type
            )
            db_session.add(schedule)
            db_session.commit()

            for index, lesson_info in enumerate(day_info.get(week_type, [])):
                for lesson in lesson_info:
                    day_entry = Day(
                        schedule_id=schedule.id,
                        name=lesson.get("name"),
                        type=lesson.get("type", "Неизвестно"),
                        tutor=lesson.get("tutor", "Неизвестно"),
                        place=lesson.get("place", "Неизвестно"),
                        lesson_place=index+1
                    )
                    db_session.add(day_entry)
            db_session.commit()

def save_alerts_to_db(db_session: Session, alerts: dict, group_id: int):
    for week_type, week_alerts in alerts.items():
        for alert in week_alerts:
            alert_record = Alert(
                group_id=group_id,
                lesson=str(alert["lesson"]),
                name=alert["name"],
                place=alert["place"],
                next_name=alert["next_name"],
                next_place=alert["next_place"],
                alert_type=alert["alert_type"]
            )
            db_session.add(alert_record)
        db_session.commit()

