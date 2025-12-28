import pandas as pd

def preprocessing_hrly_ev_load(df: pd.DataFrame):

    df = df.rename(columns={
        "User_ID": "user_id",
        "session_ID": "session_id",
        "Synthetic_3_6kW": "synthetic_3_6_kwh",
        "Synthetic_7_2kW": "synthetic_7_2_kwh",
        "Flex_3_6kW": "flex_3_6_kwh",
        "Flex_7_2kW": "flex_7_2_kwh",
    })

    df['date_from'] = pd.to_datetime(df['date_from'], 
                                format="%d.%m.%Y %H:%M")
    df['date_to'] = pd.to_datetime(df['date_to'], 
                                format="%d.%m.%Y %H:%M")

    energy_cols = [
        "synthetic_3_6_kwh",
        "synthetic_7_2_kwh",
        "flex_3_6_kwh",
        "flex_7_2_kwh",
    ]

    df[energy_cols] = (
        df[energy_cols]
        .replace(",", ".", regex=True)
    )

    df[energy_cols] = df[energy_cols].apply(
        pd.to_numeric, errors="coerce"
    )
    
    return df