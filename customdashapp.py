import dash
from dash import html,dcc
from dash.dependencies import Input, Output
import pandas as pd
from sqlalchemy import create_engine, text
import matplotlib.pyplot as plt

# load dotenv
from dotenv import load_dotenv
import os
load_dotenv()
pss=os.getenv('PASS')

engine = create_engine(f'mysql://velocitatem:{pss}@localhost/sakila')

def get_data(query, engine):
    query = text(query)
    with engine.connect() as con:
        data = pd.read_sql(query, con)
    return data


queries = [
    """
select category.name, avg(film.rating) as avr from film
join film_category on film_category.film_id = film.film_id
join category on category.category_id = film_category.category_id
group by category.name
order by avr desc
;
    """,
    """
SELECT film.title, sum(amount) as sum
FROM payment
JOIN rental ON payment.rental_id = rental.rental_id
join inventory on rental.inventory_id = inventory.inventory_id
JOIN film on inventory.film_id = film.film_id
GROUP BY inventory.film_id
ORDER by sum desc
limit 5
;
    """,
# this one we use a histogram
    """
select customer.customer_id, sum(payment.amount) as tt from customer
join payment on payment.customer_id = customer.customer_id
group by customer.customer_id
order by tt desc
;
    """,
    """
select category.name, avg(film.rating) as avr from film
join film_category on film_category.film_id = film.film_id
join category on category.category_id = film_category.category_id
group by category.name
order by avr desc
;
    """,
    """
select * from
(select category.name, avg(film.length) as ad from film
join film_category on film.film_id = film_category.film_id
join category on category.category_id = film_category.category_id
group by category.category_id
) as subquery where ad >
( select avg(film.length) from film )
;
    """
]


axes = [
    ['category', 'average rating'],
    ['film', 'total amount'],
    ['customer', 'total amount'],
    ['category', 'average rating'],
    ['category', 'average length']
]

axes_points = [
    ["name", "avr"],
    ["title", "sum"],
    ["customer_id", "tt"],
    ["name", "avr"],
    ["name", "ad"]
]



data = [get_data(query, engine) for query in queries]

app = dash.Dash(__name__)

# add dropdown to view data and then predict data
app.layout = html.Div([
    html.H1('Sakila Dashboard')
    ] + [dcc.Graph( id='graph-{}'.format(i), figure={ 'data': [ { 'x': data[i][axes_points[i][0]], 'y': data[i][axes_points[i][1]], 'type': 'bar', 'name': axes[i][1] }, ], 'layout': { 'title': axes[i][0] } } ) for i in range(len(queries)) ] )


if __name__ == '__main__':
    app.run_server(debug=True)
