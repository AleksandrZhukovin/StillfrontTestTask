from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from datetime import datetime

from .database import Base, SessionLocal


class Rate(Base):
    __tablename__ = "rates"
    id = Column(Integer, primary_key=True)
    series_id = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, series_id, value, date):
        if isinstance(date, str):
            from app.api import SweaRatesAPI

            date = datetime.strptime(date, SweaRatesAPI.RATE_DATE_FORMAT)
        session = SessionLocal()
        rate = cls(series_id=series_id, value=value, date=date)
        session.add(rate)
        session.commit()

    @classmethod
    def query_all(cls):
        session = SessionLocal()
        return session.query(cls).all()
