from nonebot_plugin_orm import Model
from sqlalchemy import String, TEXT, ForeignKey, Integer, select, update, delete

from sqlalchemy.orm import selectinload
from sqlalchemy.orm import Mapped, mapped_column, relationship
from nonebot_plugin_orm import get_session
from pydantic import parse_obj_as, BaseModel


class Course(Model):

    course_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    day: Mapped[int] = mapped_column(Integer)

    name: Mapped[str] = mapped_column(TEXT)
    position: Mapped[str] = mapped_column(TEXT)

    sections: Mapped[str] = mapped_column(TEXT)

    teacher: Mapped[str] = mapped_column(TEXT)

    weeks: Mapped[str] = mapped_column(TEXT)
    # 添加外键
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("nonebot_plugin_ai_timetable_user.user_id")
    )
    user = relationship("User", back_populates="courses")


class Job(Model):

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    @staticmethod
    async def add_job():
        """
        添加定时任务

        """

        pass

    @staticmethod
    async def remove_job():
        """
        删除定时任务

        """
        pass

    @staticmethod
    async def init_job():
        """
        从数据库加载定时任务
        """
        pass


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

    @staticmethod
    async def add_user(user_id: str, base_url: str, response_url: str, user_data: dict):
        """在数据库中添加新用户,user_data是返回数据中的data部分"""
        async with get_session() as session:
            user_data.update(user_data["setting"])
            user_orm = parse_obj_as(User, user_data)
            user_orm.user_id = user_id
            user_orm.base_url = base_url
            user_orm.response_url = response_url
            user_data["courses"].sort(key=lambda x: int(x["sections"].split(",")[0]))
            for course in user_data["courses"]:
                course_orm = parse_obj_as(Course, course)
                user_orm.courses.append(course_orm)  # 添加表关系
                session.add(course_orm)
            session.add(user_orm)
            await session.commit()

    @staticmethod
    async def update_user(
        user_id: str, base_url: str, response_url: str, user_data: dict
    ):
        """从数据库中重新更新用户信息"""
        async with get_session() as session:
            # 查询现有的用户
            query = select(User).where(User.user_id == user_id)
            result = await session.execute(query)
            user_orm = result.scalar_one_or_none()

            if user_orm:
                # 更新用户的基本信息
                user_orm.base_url = base_url
                user_orm.response_url = response_url
                user_orm.name = user_data["name"]
                # 其他需要更新的用户属性...

                # 删除现有的课程
                for course in user_orm.courses:
                    session.delete(course)
                user_data["courses"].sort(
                    key=lambda x: int(x["sections"].split(",")[0])
                )
                for course_data in user_data["courses"]:
                    course_orm = parse_obj_as(Course, course_data)
                    user_orm.courses.append(course_orm)

                # 提交更改
                session.commit()

    @staticmethod
    async def remove_user(user_id: str):
        """从数据库中删除用户信息"""
        pass

    @staticmethod
    async def check_user_in_table(user_id: str) -> bool:
        """
        检查当前uid是否在数据库中
        """
        async with get_session() as session:
            query = select(User).where(User.user_id == user_id)
            # 执行查询
            result = await session.execute(query)
            row = result.fetchone()
        return row is not None
