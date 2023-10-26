import dash
from dash import html,dcc
from dash.dependencies import Input, Output
import pandas as pd
from sqlalchemy import create_engine, text

# Connect to the Sakila database
from dotenv import load_dotenv
import os
load_dotenv()
pss=os.getenv('PASS')


engine = create_engine(f'mysql://velocitatem:{pss}@localhost/sakila')

query = f"""
SELECT DATE(rental_date) AS rental_day, COUNT(rental_id) AS rental_count
FROM rental, inventory, film, film_category
WHERE rental.inventory_id = inventory.inventory_id AND
inventory.film_id = film.film_id AND
film.film_id = film_category.film_id AND
category_id = 1
GROUP BY rental_day;
"""

with engine.connect() as con:
    rental_data = pd.read_sql(text(query), con)

import datetime as dt
# convert date to float
rental_data["rental_day"] = pd.to_datetime(rental_data["rental_day"])
rental_data["rental_day"] = rental_data["rental_day"].map(dt.datetime.toordinal)
# set index
rental_data.set_index("rental_day", inplace=True)


import pmdarima as pm
# prediction data using sarimax from pmdarima
model = pm.auto_arima(rental_data, start_p=1, start_q=1,
                        test='adf',       # use adftest to find optimal 'd'
                        max_p=3, max_q=3,  # maximum p and q
                        m=1,              # frequency of series
                        d=None,           # let model determine 'd'
                        seasonal=False,   # No Seasonality
                        start_P=0,
                        D=0,
                        trace=True,
                        error_action='ignore',
                        suppress_warnings=True,
                        stepwise=True)
print(model.summary())

import pickle
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)
