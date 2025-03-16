from sqlalchemy import BigInteger, String, ForeignKey, JSON, DateTime, Integer, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.utils.datebase import Base


class UserTelegram(Base):
    __tablename__ = 'user_telegram'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String(100))
    first_name: Mapped[str] = mapped_column(String(100))
    middle_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20), unique=True)
    date_of_birth: Mapped[datetime] = mapped_column(DateTime)
    admin: Mapped[bool] = mapped_column(Boolean, default=False)

    questionnaires = relationship('Questionnaire', back_populates='user', lazy='joined', overlaps="questionnaire")


class JobOpenings(Base):
    __tablename__ = 'job_openings'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    time_created: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user_id_create: Mapped[int] = mapped_column(ForeignKey('user_telegram.user_id'))
    flag: Mapped[bool] = mapped_column(Boolean, default=True)

    questions = relationship('Question', back_populates='job_opening')


class Question(Base):
    __tablename__ = 'question'

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    job_opening_id: Mapped[int] = mapped_column(ForeignKey('job_openings.id'))

    job_opening = relationship('JobOpenings', back_populates='questions')


class Questionnaire(Base):
    __tablename__ = 'questionnaire'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user_telegram.user_id'))
    job_opening_id: Mapped[int] = mapped_column(ForeignKey('job_openings.id'))
    data: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship('UserTelegram', back_populates='questionnaires')
    job_opening = relationship('JobOpenings', backref='questionnaires', lazy='joined')
