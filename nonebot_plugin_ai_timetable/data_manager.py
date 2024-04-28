from sqlalchemy import (
    select,
)
from nonebot import logger, require
from sqlalchemy.orm import selectinload

require("nonebot_plugin_orm")
from nonebot_plugin_orm import get_session
from typing import List
from .model import User,Course
import time

async def add_user(user_id: str, base_url: str, response_url: str, user_data: dict):
    """在数据库中添加新用户,user_data是返回数据中的data部分"""
    async with get_session() as session:
        user_data.update(user_data["setting"])
        del user_data["setting"]
        user_orm = User()
        user_orm.user_id = user_id
        user_orm.base_url = base_url
        user_orm.response_url = response_url
        # 设置类的属性
        for key, value in user_data.items():
            if hasattr(User, key) and key != "courses":
                setattr(user_orm, key, value)
        user_data["courses"].sort(key=lambda x: int(x["sections"].split(",")[0]))
        for course in user_data["courses"]:
            course_orm = Course()
            for key, value in course.items():
                if hasattr(Course, key):
                    setattr(course_orm, key, value)
            user_orm.courses.append(course_orm)  # 添加表关系
            session.add(course_orm)
        session.add(user_orm)
        await session.commit()


async def update_user(user_id: str, base_url: str, response_url: str, user_data: dict):
    """从数据库中重新更新用户信息"""
    async with get_session() as session:
        # 查询现有的用户
        query = (
            select(User)
            .options(selectinload(User.courses))
            .where(User.user_id == user_id)
        )
        result = await session.execute(query)
        user_orm = result.scalar_one_or_none()

        if user_orm:
            # 更新用户的基本信息
            user_orm.base_url = base_url
            user_orm.response_url = response_url
            user_orm.name = user_data["name"]
            # 其他需要更新的用户属性
            user_orm.courses.clear()
            user_data["courses"].sort(key=lambda x: int(x["sections"].split(",")[0]))
            for course in user_data["courses"]:
                course_orm = Course()
                for key, value in course.items():
                    if hasattr(Course, key):
                        setattr(course_orm, key, value)
                user_orm.courses.append(course_orm)

            # 提交更改
            session.commit()


async def remove_user(user_id: str):
    """从数据库中删除用户信息"""
    async with get_session() as session:
        # 查询现有的用户
        query = (
            select(User)
            .options(selectinload(User.courses))
            .where(User.user_id == user_id)
        )
        result = await session.execute(query)
        user_orm = result.scalar_one_or_none()
        if user_orm:
            # 删除用户的所有课程
            user_orm.courses.clear()
            # 删除用户对象
            session.delete(user_orm)
            # 提交更改
            await session.commit()


async def query_user_by_uid(user_id: str) -> User:
    """从数据库获取某个用户信息，只含信息，不含课表"""
    async with get_session() as session:
        query = select(User).filter(User.user_id == user_id)
        result = await session.execute(query)
        result = result.scalar()
    return result


async def query_course_by_day(user_id: str, day: int) -> List[Course]:
    """根据用户ID和日期查询课程"""
    async with get_session() as session:
        # 查询用户
        query = (
            select(User)
            .options(selectinload(User.courses))
            .where(User.user_id == user_id)
        )
        result = await session.execute(query)
        user_orm = result.scalar_one_or_none()
        if user_orm:
            # 过滤课程
            courses = [course for course in user_orm.courses if course.day == day]
            return courses
        else:
            return []


async def query_course_by_name(user_id: str, name: str) -> List[Course]:
    """根据用户ID和课程名查询课程"""
    async with get_session() as session:
        # 查询用户
        query = (
            select(User)
            .options(selectinload(User.courses))
            .where(User.user_id == user_id)
        )
        result = await session.execute(query)
        user_orm = result.scalar_one_or_none()
        if user_orm:
            # 过滤课程
            courses = [course for course in user_orm.courses if name in course.name]
            return courses
        else:
            return []


async def get_current_week(user_id: str, day: int):
    # 查询用户
    async with get_session() as session:
        query = (
            select(User)
            .options(selectinload(User.courses))
            .where(User.user_id == user_id)
        )
        result = await session.execute(query)
        user_orm = result.scalar_one_or_none()
    if user_orm:
        presentweek = int((time.time() - int(user_orm.startSemester[0:10])) // 604800)
        +1
        return presentweek
    else:
        return 7


async def check_user_in_table(user_id: str) -> bool:
    """
    检查当前uid是否在数据库中
    """
    async with get_session() as session:
        query = select(User).where(User.user_id == user_id)
        # 执行查询
        result = await session.execute(query)
        row = result.fetchone()
    if row is None:
        logger.debug("不存在该用户")
    return row is not None
