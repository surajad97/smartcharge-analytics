# create hourly EV load table and ingest it to postresql database
import pandas as pd
import database_model
import ev_charging_database
from preprocessing import preprocessing_hrly_ev_load

database_model.Base.metadata.create_all(ev_charging_database.engine)

hrly_ev_load_df = pd.read_csv('/home/surajad97/power_grid_project/ev_charging_data/Dataset 2_Hourly EV loads - Per user.csv',
                              sep=';')

hrly_ev_load_df = preprocessing_hrly_ev_load(hrly_ev_load_df)

print(hrly_ev_load_df)

hrly_ev_load_df.to_sql(
    name = "hrly_ev_loads",
    con = ev_charging_database.engine,
    if_exists='replace',
    index=True,
)