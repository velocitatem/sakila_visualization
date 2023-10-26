# read data from influx db
import pandas as pd
import influxdb_client
from influxdb_client import InfluxDBClient
import pmdarima as pm
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# load dotenv
from dotenv import load_dotenv
import os
load_dotenv()
pss=os.getenv('INFLUX_TOKEN')
# connect to influxdb
org = "Lusiana"
url = "http://localhost:8086"
token = pss

client = InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()


# Query data
query = """
from(bucket: "sakila")
  |> range(start: 0, stop: now())
  |> filter(fn: (r) => r["_measurement"] == "rental_count") |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
"""
df = query_api.query_data_frame(query)

# Data transformation
df["_time"] = pd.to_datetime(df["_time"], unit='s')
# start from year 200
df = df[df["_time"] > "2000-01-01"]
# earlier than september 2005
df = df[df["_time"] < "2005-09-01"]
df["rental_count"] = df["rental_count"].astype(int)
df = pd.DataFrame({"rental_day": df["_time"], "rental_count": df["rental_count"]})
df = df.set_index("rental_day")

# Forecasting
model = pm.auto_arima(df, start_p=1, start_q=1,
                      test='adf',
                      max_p=3, max_q=3,
                      m=1,
                      d=None,
                      seasonal=False,
                      start_P=0,
                      D=0,
                      trace=True,
                      error_action='ignore',
                      suppress_warnings=True,
                      stepwise=True)

# Forecast next 30 days
predicted = model.predict(n_periods=30)
print(predicted)
# 40    41.716645
# 41    29.613509
# 42    41.465003

forecast = pd.DataFrame(index=pd.date_range(start=df.index[-1], periods=31, freq="D", closed="right"))
forecast["rental_count"] = predicted.tolist()
print(forecast)
# Initialize Dash App
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div([
    dcc.Graph(id='forecast-plot')
])

# Populate Graph
@app.callback(
    Output('forecast-plot', 'figure'),
    [Input('forecast-plot', 'id')]
)
def update_graph(dummy):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['rental_count'], mode='lines', name='Actual'))
    fig.add_trace(go.Scatter(x=forecast.index, y=forecast['rental_count'], mode='lines', name='Forecast'))
    fig.update_layout(title='Rental Count Forecast',
                      xaxis_title='Date',
                      yaxis_title='Rental Count')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
