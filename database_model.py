from sqlalchemy import (
    Column, 
    Integer, 
    String,
    DateTime, 
    Numeric
    )
from ev_charging_database import Base


class HrlyEVLoad(Base):

    __tablename__ = "hrly_ev_loads"

    index = Column(Integer, primary_key=True)
    date_from = Column(DateTime, nullable = False, index = True)
    date_to = Column(DateTime, nullable = False)
    user_id = Column(String)
    session_id = Column(Integer)
    synthetic_3_6_kwh = Column(Numeric(6,3))
    synthetic_7_2_kwh = Column(Numeric(6,3))
    flex_3_6_kwh = Column(Numeric(6,3))
    flex_7_2_kwh = Column(Numeric(6,3))