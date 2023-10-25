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

# Create the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Sakila Rental Data Over Time"),

    # Dropdown to select a category
    dcc.Dropdown(
        id='category-dropdown',
        options=[
            {'label': 'Category 1', 'value': 1},
            {'label': 'Category 2', 'value': 2},
            # Add more options based on your data
        ],
        value=1  # Default selected option
    ),

    # Line chart to display data over time
    dcc.Graph(id='line-chart')
])

# Define callback to update the line chart based on the selected category
@app.callback(
    Output('line-chart', 'figure'),
    [Input('category-dropdown', 'value')]
)
def update_line_chart(selected_category):
    # SQL query to retrieve data for the selected category over time
    query = f"""
    SELECT DATE(rental_date) AS rental_day, COUNT(rental_id) AS rental_count
    FROM rental, inventory, film, film_category
    WHERE rental.inventory_id = inventory.inventory_id AND
    inventory.film_id = film.film_id AND
    film.film_id = film_category.film_id AND
    category_id = {selected_category}
    GROUP BY rental_day;
    """

    with engine.connect() as con:
        rental_data = pd.read_sql(text(query), con)

    # import model and predict the next 30 days
    import pickle
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)




    # Create the line chart with predictions and real data

    fig = {
        'data': [
            { 'x': rental_data.index, 'y': rental_data['rental_count'], 'type': 'line', 'name': 'Real Data' },
        ],
        'layout ': { 'title': 'Sakila Rental Data Over Time' }
    }


    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
