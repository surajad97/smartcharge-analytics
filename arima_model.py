import pandas as pd
from preprocessing import preprocessing_hrly_ev_load
from scipy.stats import boxcox
from scipy.special import inv_boxcox
from statsmodels.tsa.arima.model import ARIMA
import joblib
from pathlib import Path

BASE_DIR = Path.cwd()
SAVE_MODEL = BASE_DIR / "models/"
SAVE_MODEL.mkdir(parents=True, exist_ok=True)
DATA_PATH = (BASE_DIR / 
    "ev_charging_data/Dataset 2_Hourly EV loads - Per user.csv")

hrly_ev_load_df = pd.read_csv(DATA_PATH, sep=';')

hrly_ev_load_df = preprocessing_hrly_ev_load(hrly_ev_load_df)

hrly_ev_load_df['day'] = hrly_ev_load_df['date_from'].dt.date

daily_energy_df = hrly_ev_load_df[['day', 'synthetic_3_6_kwh']]

daily_energy_df = daily_energy_df.groupby(
    by='day', 
    as_index=True).agg(
    total_energy = ('synthetic_3_6_kwh', 'sum'))

min_value = 1e-4

daily_energy_df.loc[
    daily_energy_df["total_energy"] == 0,
    "total_energy"
] = min_value

daily_energy_df = daily_energy_df.copy()

# make the target variance stationary
daily_energy_df["rolling_avg_boxcox"], lam = (
    boxcox(daily_energy_df['total_energy'])
)

model = ARIMA(daily_energy_df['rolling_avg_boxcox'], order = (14,1,14))

fitted_model = model.fit()

joblib.dump({
    "model": fitted_model,
    "boxcox_lambda": lam,
    "last_date": daily_energy_df.index[-1],
    "fred": "Daily",
    "p": 14,
    "d": 1,
    "q": 14,
    "energy_col": "synthetic_3_6_kwh",
    }, SAVE_MODEL / "arima_bundle_p14_q14.pkl")