import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from sqlalchemy import create_engine, text
import pandas as pd

# MySQL connection

from dotenv import load_dotenv
import os
load_dotenv()
pss=os.getenv('PASS')

engine = create_engine(f'mysql://velocitatem:{pss}@localhost/sakila')

token = os.getenv('INFLUX_TOKEN')
org = "Lusiana"
url = "http://localhost:8086"

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)



# Query to get data from MySQL
Q = """
SELECT DATE(rental_date) AS rental_day, COUNT(rental_id) AS rental_count
FROM rental, inventory, film, film_category
WHERE rental.inventory_id = inventory.inventory_id AND
inventory.film_id = film.film_id AND
film.film_id = film_category.film_id AND
category_id = 1
GROUP BY rental_day;
"""

# Fetch data from MySQL
with engine.connect() as con:
    rental_data = pd.read_sql(text(Q), con)

# Convert date to datetime format

rental_data["rental_day"] = pd.to_datetime(rental_data["rental_day"])
rental_data["rental_day"] = rental_data["rental_day"].apply(lambda x: int(x.timestamp()))

# exit program

bucket="sakila"

write_api = write_client.write_api(write_options=SYNCHRONOUS)

# Prepare data for InfluxDB



import time
for index, row in rental_data.iterrows():
    point = (
        Point("rental_count")
        .tag("category", "Action")
        .field("rental_count", int(row["rental_count"]))
        .time(row['rental_day'])
    )
    print(point)
    print(row["rental_day"], row["rental_count"])
    res=write_api.write(bucket=bucket, record=point)



# Close connection to MySQL
engine.dispose()

# Close connection to InfluxDB
write_client.close()
