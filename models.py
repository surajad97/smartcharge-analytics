from pydantic import BaseModel
import pandas as pd
from datetime import datetime

class HrlyEVLoad(BaseModel):
    id: int
    date_from: datetime
    date_to: datetime
    user_id: str
    session_id: int
    synthetic_3_6_kwh: float
    synthetic_7_2_kwh: float
    flex_7_2_kwh: float