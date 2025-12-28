from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from ev_charging_database import SessionLocal, engine
import database_model
from sqlalchemy.orm import Session
from sqlalchemy import distinct, func, case
from datetime import datetime, timedelta
from typing import Annotated

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "localhost:3000",
        "127.0.0.1:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

database_model.Base.metadata.create_all(bind = engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/")
def main():
    return "Welcome to from EV Charging Project!"

@app.get("/hourly_loads")
def get_all_hourly_data(db: db_dependency):
    
    db_hrly_ev_loads = (
        db.query(database_model.HrlyEVLoad).limit(20).all()
    )

    return db_hrly_ev_loads

@app.get("/users")
def get_unique_users(db: db_dependency):
    users = (
        db.query(distinct(database_model.HrlyEVLoad.user_id))
        .all()
    )
    return [u[0] for u in users]

@app.get("/load/{user_id}/hourly")
def get_hourly_data_for_user(
    db: db_dependency,
    user_id: str, 
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    ):
    
    query = (
        db.query(database_model.HrlyEVLoad).
        filter(database_model.HrlyEVLoad.user_id == user_id)
    )

    if not query:
        raise HTTPException(
            status_code=404,
            detail="No data found for given user"
        )
    
    if start_date is not None and end_date is not None:
        if start_date > end_date:
            raise HTTPException(
                status_code=400,
                detail="start_date must be before end_date"
            )

    if start_date:
        query = query.filter(database_model.HrlyEVLoad.date_from >= start_date)

    if end_date:
        query = query.filter(database_model.HrlyEVLoad.date_to <= end_date)
    
    if not query:
        raise HTTPException(
            status_code=404,
            detail="No data found between given datetime range"
        )
        
    return query.order_by(database_model.HrlyEVLoad.date_from).all()

@app.get("/load/daily")
def get_daily_load(
    db: db_dependency,
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    ):
    query = db.query(
        func.date(database_model.HrlyEVLoad.date_from).label("day"),
        func.sum(
            func.coalesce(database_model.HrlyEVLoad.synthetic_3_6_kwh, 0)
        ).label("daily_energy_kwh"),
        )
    
    if start_date:
        query = query.filter(database_model.HrlyEVLoad.date_from >= start_date)

    if end_date:
        query = query.filter(database_model.HrlyEVLoad.date_from <= end_date)

    
    results = (
        query
        .group_by("day")
        .order_by("day")
        .all()
    )

    return [
        {
            "day": row.day.isoformat(), 
            "daily_energy_kwh": float(row.daily_energy_kwh),
        }
        for row in results
    ]

@app.get("/kpi/total-energy")
def get_total_demand(
    db: db_dependency,
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    ):

    query = db.query(
        func.sum(func.coalesce(database_model.HrlyEVLoad.synthetic_3_6_kwh, 0)
                 ).label("total_energy_kwh")
    )

    if start_date:
        query = query.filter(database_model.HrlyEVLoad.date_from >= start_date)

    if end_date:
        query = query.filter(database_model.HrlyEVLoad.date_from <= end_date)

    total_energy = query.scalar() or 0

    return {
        "total_energy_kwh": round(float(total_energy), 2)
        }

@app.get("/kpi/daily-average")
def get_daily_avg_energy(
    db: db_dependency,
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None)               
    ):

    # Step 1: subquery -> daily totals
    daily_subquery = db.query(
        func.date(database_model.HrlyEVLoad.date_from).label("day"),
        func.sum(
            func.coalesce(database_model.HrlyEVLoad.synthetic_3_6_kwh, 0)
        ).label("daily_energy_kwh")
    )

    if start_date:
        daily_subquery = daily_subquery.filter(
            database_model.HrlyEVLoad.date_from >= start_date
            )

    if end_date:
        daily_subquery = daily_subquery.filter(
            database_model.HrlyEVLoad.date_from <= end_date
            )
        
    daily_subquery = daily_subquery.group_by("day").subquery()

    # Step 2: average over daily totals
    avg_daily_energy = (
        db.query(func.avg(daily_subquery.c.daily_energy_kwh))
        .scalar()
    ) or 0

    return {
        "avg_daily_energy_kwh": round(float(avg_daily_energy), 2)
    }

@app.get("/kpi/daily-average-last-7-days")
def get_last_7_days_avg_energy(db: db_dependency):

    # Step 0: get latest date from data
    latest_date = (
        db.query(func.max(database_model.HrlyEVLoad.date_from))
        .scalar()
    )

    if not latest_date:
        return {"avg_daily_energy_kwh": 0}
    
    start_date = latest_date - timedelta(days=7)

    # Step 1: subquery -> daily totals
    daily_subquery = db.query(
        func.date(database_model.HrlyEVLoad.date_from).label("day"),
        func.sum(
            func.coalesce(database_model.HrlyEVLoad.synthetic_3_6_kwh, 0)
        ).label("daily_energy_kwh")
    )

    daily_subquery = daily_subquery.filter(
            database_model.HrlyEVLoad.date_from >= start_date
            )

    daily_subquery = daily_subquery.filter(
            database_model.HrlyEVLoad.date_from <= latest_date
            )
        
    daily_subquery = daily_subquery.group_by("day").subquery()

    # Step 2: average over daily totals
    avg_daily_energy = (
        db.query(func.avg(daily_subquery.c.daily_energy_kwh))
        .scalar()
    ) or 0

    return {
        "avg_daily_energy_kwh": round(float(avg_daily_energy), 2),
        "period": "last_7_days",
        "from": start_date.date(),
        "to": latest_date.date()
    }

@app.get("/kpi/peak-daily")
def get_daily_peak_energy(
    db: db_dependency,
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None)               
    ):

    # Step 1: daily aggregation subquery
    daily_subquery = db.query(
        func.date(database_model.HrlyEVLoad.date_from).label("day"),
        func.sum(
            func.coalesce(database_model.HrlyEVLoad.synthetic_3_6_kwh, 0)
        ).label("daily_energy_kwh")
    )

    if start_date:
        daily_subquery = daily_subquery.filter(
            database_model.HrlyEVLoad.date_from >= start_date
            )

    if end_date:
        daily_subquery = daily_subquery.filter(
            database_model.HrlyEVLoad.date_from <= end_date
            )
        
    daily_subquery = daily_subquery.group_by("day").subquery()

    # Step 2: peak daily energy
    peak_daily_energy = (
        db.query(func.max(daily_subquery.c.daily_energy_kwh))
        .scalar()
    ) or 0

    return {
        "peak_daily_energy_kwh": round(float(peak_daily_energy), 2)
    }


@app.get("/kpi/peak-hourly")
def get_hourly_peak_energy(
    db: db_dependency,
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None)               
    ):

    # Step 1: aggregate per hour across all users
    hourly_subquery = db.query(
        database_model.HrlyEVLoad.date_from.label("hour"), 
        func.sum(func.coalesce(
            database_model.HrlyEVLoad.synthetic_3_6_kwh, 0)
            ).label("total_hourly_energy_kwh"))
    
    if start_date:
        hourly_subquery = hourly_subquery.filter(
            database_model.HrlyEVLoad.date_from >= start_date
            )

    if end_date:
        hourly_subquery = hourly_subquery.filter(
            database_model.HrlyEVLoad.date_from <= end_date
            )

    hourly_subquery = hourly_subquery.group_by("hour").subquery()

    # Step 2: peak across hours
    peak_hourly_load = (
        db.query(func.max(hourly_subquery.c.total_hourly_energy_kwh))
        .scalar()
    ) or 0

    return {
        "peak_hourly_load_kwh": round(float(peak_hourly_load), 2)
    }

@app.get("/kpi/daily_utilization")
def get_daily_utilization(db: db_dependency,
                          start_date: datetime | None = Query(None),
                          end_date: datetime | None = Query(None)
                          ):
    hourly_energy_sum = func.sum(
        func.coalesce(database_model.HrlyEVLoad.synthetic_3_6_kwh, 0)
    )
    
    # Step 1: aggregate per hour across all users
    hourly_query = db.query(
        database_model.HrlyEVLoad.date_from.label("hour"),
        func.date(database_model.HrlyEVLoad.date_from).label("day"),
        hourly_energy_sum.label("total_hourly_energy_kwh"), 
        case(
            (hourly_energy_sum > 0, 1),
            else_ = 0
        ).label("active")
        )

    if start_date:
        hourly_query = hourly_query.filter(
            database_model.HrlyEVLoad.date_from >= start_date
            )

    if end_date:
        hourly_query = hourly_query.filter(
            database_model.HrlyEVLoad.date_from <= end_date
            )
    
    hourly_subquery = (hourly_query
    .group_by(database_model.HrlyEVLoad.date_from).subquery())
    
    results = (
        db.query(
            hourly_subquery.c.day,
            func.sum(hourly_subquery.c.active).label("active_hours")
        )
        .group_by(hourly_subquery.c.day)
        .order_by(hourly_subquery.c.day)
        .all()
    )

    return [
        {
            "day": row.day.isoformat(),
            "active_hours": int(row.active_hours),
        }
        for row in results
    ]

@app.get("/kpi/avg-active-hours-per-day")
def get_avg_active_hours_per_day(
    db: db_dependency,
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
):
    # ----- Step 1: hourly aggregation + active flag -----
    hourly_energy_sum = func.sum(
        func.coalesce(
            database_model.HrlyEVLoad.synthetic_3_6_kwh, 0
        )
    )

    hourly_query = (
        db.query(
            func.date(database_model.HrlyEVLoad.date_from).label("day"),
            database_model.HrlyEVLoad.date_from.label("hour"),
            case(
                (hourly_energy_sum > 0, 1),
                else_=0
            ).label("active")
        )
    )
    if start_date:
        hourly_query = hourly_query.filter(
            database_model.HrlyEVLoad.date_from >= start_date
        )

    if end_date:
        hourly_query = hourly_query.filter(
            database_model.HrlyEVLoad.date_from <= end_date
        )

    hourly_subquery = (
        hourly_query
        .group_by(database_model.HrlyEVLoad.date_from)
        .subquery()
    )

    # ----- Step 2: daily active hours -----
    daily_subquery = (
        db.query(
            hourly_subquery.c.day,
            func.sum(hourly_subquery.c.active).label("active_hours")
        )
        .group_by(hourly_subquery.c.day)
        .subquery()
    )

    # ----- Step 3: average across days -----
    avg_active_hours = (
        db.query(func.avg(daily_subquery.c.active_hours))
        .scalar()
    ) or 0

    return {
        "avg_active_charging_hours_per_day": round(float(avg_active_hours), 2)
    }