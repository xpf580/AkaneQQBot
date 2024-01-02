import asyncio
import sys
from typing import List, Optional, Union

from nonebot.log import logger
from nonebot_plugin_orm import Model, get_session
from nonebot_plugin_session import Session, SessionIdType, SessionLevel
from sqlalchemy import Integer, String, UniqueConstraint, exc, select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import ColumnElement


class SessionModel(Model):
    __table_args__ = (
        UniqueConstraint(
            "bot_id",
            "bot_type",
            "platform",
            "level",
            "id1",
            "id2",
            "id3",
            name="unique_session",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    bot_id: Mapped[str] = mapped_column(String(64))
    bot_type: Mapped[str] = mapped_column(String(32))
    platform: Mapped[str] = mapped_column(String(32))
    level: Mapped[int] = mapped_column(Integer)
    id1: Mapped[str] = mapped_column(String(64))
    id2: Mapped[str] = mapped_column(String(64))
    id3: Mapped[str] = mapped_column(String(64))

    @property
    def session(self) -> Session:
        return Session(
            bot_id=self.bot_id,
            bot_type=self.bot_type,
            platform=self.platform,
            level=SessionLevel(self.level),
            id1=self.id1 or None,
            id2=self.id2 or None,
            id3=self.id3 or None,
        )

    @staticmethod
    def filter_statement(
        session: Session,
        id_type: Union[int, SessionIdType],
        *,
        include_platform: bool = True,
        include_bot_type: bool = True,
        include_bot_id: bool = True,
    ) -> List[ColumnElement[bool]]:
        id_type = min(max(id_type, 0), SessionIdType.GROUP_USER)

        if session.level == SessionLevel.LEVEL0:
            id_type = 0
        elif session.level == SessionLevel.LEVEL1:
            id_type = int(bool(id_type))
        elif session.level == SessionLevel.LEVEL2:
            id_type = (id_type & 1) | (int(bool(id_type >> 1)) << 1)
        elif session.level == SessionLevel.LEVEL3:
            pass

        include_id1 = bool(id_type & 1)
        include_id2 = bool((id_type >> 1) & 1)
        include_id3 = bool((id_type >> 2) & 1)

        whereclause: List[ColumnElement[bool]] = []
        if include_bot_id:
            whereclause.append(SessionModel.bot_id == session.bot_id)
        if include_bot_type:
            whereclause.append(SessionModel.bot_type == session.bot_type)
        if include_platform:
            whereclause.append(SessionModel.platform == session.platform)
        if include_id1:
            whereclause.append(SessionModel.id1 == (session.id1 or ""))
        if include_id2:
            whereclause.append(SessionModel.id2 == (session.id2 or ""))
        if include_id3:
            whereclause.append(SessionModel.id3 == (session.id3 or ""))
        return whereclause


_insert_mutex: Optional[asyncio.Lock] = None


def _get_insert_mutex():
    # py3.10以下，Lock必须在event_loop内创建
    global _insert_mutex

    if _insert_mutex is None:
        _insert_mutex = asyncio.Lock()
    elif sys.version_info < (3, 10):
        # 还需要判断loop是否与之前创建的一致
        # 单测中不同的test，loop也不一样
        # 但是nonebot里loop始终是一样的
        if getattr(_insert_mutex, "_loop") != asyncio.get_running_loop():
            _insert_mutex = asyncio.Lock()

    return _insert_mutex


async def get_session_persist_id(session: Session) -> int:
    statement = (
        select(SessionModel.id)
        .where(SessionModel.bot_id == session.bot_id)
        .where(SessionModel.bot_type == session.bot_type)
        .where(SessionModel.platform == session.platform)
        .where(SessionModel.level == session.level.value)
        .where(SessionModel.id1 == (session.id1 or ""))
        .where(SessionModel.id2 == (session.id2 or ""))
        .where(SessionModel.id3 == (session.id3 or ""))
    )

    async with get_session() as db_session:
        if persist_id := (await db_session.scalars(statement)).one_or_none():
            return persist_id

    session_model = SessionModel(
        bot_id=session.bot_id,
        bot_type=session.bot_type,
        platform=session.platform,
        level=session.level.value,
        id1=session.id1 or "",
        id2=session.id2 or "",
        id3=session.id3 or "",
    )

    async with _get_insert_mutex():
        try:
            async with get_session() as db_session:
                db_session.add(session_model)
                await db_session.commit()
                await db_session.refresh(session_model)
                return session_model.id
        except exc.IntegrityError:
            logger.debug(f"session ({session}) is already inserted")

            async with get_session() as db_session:
                return (await db_session.scalars(statement)).one()


async def get_session_by_persist_id(sid: int) -> Session:
    async with get_session() as db_session:
        session_model = (
            await db_session.scalars(select(SessionModel).where(SessionModel.id == sid))
        ).one()
        return session_model.session
