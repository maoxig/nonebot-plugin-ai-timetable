from nonebot_plugin_orm import Model
from sqlalchemy import (
    TEXT,
    ForeignKey,
    Integer,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship



class Course(Model):

    course_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    day: Mapped[int] = mapped_column(Integer)

    name: Mapped[str] = mapped_column(TEXT)
    position: Mapped[str] = mapped_column(TEXT)

    sections: Mapped[str] = mapped_column(TEXT)

    teacher: Mapped[str] = mapped_column(TEXT)

    weeks: Mapped[str] = mapped_column(TEXT)
    # 添加外键
    user_id: Mapped[str] = mapped_column(
        TEXT, ForeignKey("nonebot_plugin_ai_timetable_user.user_id")
    )
    user = relationship("User", back_populates="courses")


class User(Model):

    user_id: Mapped[str] = mapped_column(TEXT, primary_key=True)

    response_url: Mapped[str] = mapped_column(TEXT)
    base_url: Mapped[str] = mapped_column(TEXT)

    # 以下内容都是json文件中已有的
    current: Mapped[int] = mapped_column(Integer)

    name: Mapped[str] = mapped_column(TEXT)

    afternoonNum: Mapped[int] = mapped_column(Integer)

    createTime: Mapped[int] = mapped_column(Integer)

    isWeekend: Mapped[int] = mapped_column(Integer)
    morningNum: Mapped[int] = mapped_column(Integer)
    nightNum: Mapped[int] = mapped_column(Integer)
    presentWeek: Mapped[int] = mapped_column(Integer)

    sectionTimes: Mapped[str] = mapped_column(TEXT)
    speak: Mapped[int] = mapped_column(Integer)
    startSemester: Mapped[str] = mapped_column(TEXT)
    totalWeek: Mapped[int] = mapped_column(Integer)

    weekStart: Mapped[int] = mapped_column(Integer)
    # 建立一对多的表关系
    courses = relationship("Course", order_by="Course.course_id", back_populates="user")

