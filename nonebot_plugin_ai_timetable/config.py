from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    # 以图片发送
    timetable_pic: bool = True
    # 发送第二天课表的时间
    timetable_alock_someday: int = 22
    # 发送第二天早八的时间
    timetable_alock_8: int = 21
    # 提前发送下一节课的时间
    timetable_send_time: float = 0.5
