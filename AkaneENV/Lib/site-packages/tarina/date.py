import re
from datetime import datetime, timedelta, timezone
from typing import Union

MILLI_SECOND = 1
SECOND = MILLI_SECOND * 1000
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7

NUMERIC = r"\d+(?:\.\d+)?"
TIME_REGEXP = re.compile(
    "^"
    + "".join(
        map(
            lambda unit: f"({NUMERIC}{unit})?",
            [
                "w(?:eek(?:s)?)?",
                "d(?:ay(?:s)?)?",
                "h(?:our(?:s)?)?",
                "m(?:in(?:ute)?(?:s)?)?",
                "s(?:ec(?:ond)?(?:s)?)?",
            ],
        )
    )
)


class DateParser:
    timezone_offset = (
        datetime.now(timezone.utc).astimezone().utcoffset().total_seconds() / 60
    )

    @classmethod
    def set_timezone_offset(cls, offset: float):
        cls.timezone_offset = offset

    @classmethod
    def get_timezone_offset(cls):
        return cls.timezone_offset

    @classmethod
    def get_date_number(cls, date: Union[float, datetime, None] = None, offset: Union[float, None] = None):
        if date is None:
            date = datetime.now()
        if isinstance(date, float):
            date = datetime.fromtimestamp(date)
        if offset is None:
            offset = cls.timezone_offset
        return int((date.timestamp() / MINUTE - offset) / 1440)

    @classmethod
    def from_date_number(cls, value: float, offset: Union[float, None] = None):
        date = datetime.fromtimestamp(value * DAY)
        if offset is None:
            offset = cls.timezone_offset
        return datetime.fromtimestamp(date.timestamp() + offset * MINUTE)

    @classmethod
    def parse(cls, pattern: str):
        if capture := TIME_REGEXP.match(pattern):
            if stamp := (
                float(capture[1] or 0) * WEEK
                + float(capture[2] or 0) * DAY
                + float(capture[3] or 0) * HOUR
                + float(capture[4] or 0) * MINUTE
                + float(capture[5] or 0) * SECOND
            ):
                return datetime.now() + timedelta(milliseconds=stamp)
        if re.match(r"^\d{1,2}(:\d{1,2}){1,2}$", pattern):
            return datetime.fromisoformat(f"{datetime.now().strftime('%Y-%m-%d')}-{pattern}")
        if re.match(r"^\d{1,2}-\d{1,2}-\d{1,2}(:\d{1,2}){1,2}$", pattern):
            return datetime.fromisoformat(f"{datetime.now().year}-{pattern}")
        return datetime.fromisoformat(pattern)

    @classmethod
    def format(cls, ms: float):
        abs_ms = abs(ms)
        if abs_ms >= DAY - HOUR / 2:
            return f"{round(ms / DAY)}d"
        elif abs_ms >= HOUR - MINUTE / 2:
            return f"{round(ms / HOUR)}h"
        elif abs_ms >= MINUTE - SECOND / 2:
            return f"{round(ms / MINUTE)}m"
        elif abs_ms >= SECOND:
            return f"{round(ms / SECOND)}s"
        return f"{ms}ms"

    @classmethod
    def to_digits(cls, source: int, length: int = 2):
        return str(source).zfill(length)

    @classmethod
    def template(cls, template: str, time: Union[datetime, None] = None):
        if time is None:
            time = datetime.now()
        return (
            template.replace("yyyy", str(time.year))
            .replace("yy", str(time.year)[2:])
            .replace("MM", cls.to_digits(time.month))
            .replace("dd", cls.to_digits(time.day))
            .replace("hh", cls.to_digits(time.hour))
            .replace("mm", cls.to_digits(time.minute))
            .replace("ss", cls.to_digits(time.second))
            .replace("SSS", cls.to_digits(time.microsecond, 3))
        )
