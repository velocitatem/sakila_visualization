import pandas as pd
import matplotlib.pyplot as plt
import sqlalchemy as sqla

# Replace 'username' and 'password' with your MySQL username and password
engine = sqla.create_engine('mysql://velocitatem:Saniroot1678@localhost/sakila')


def get_data(query, engine):
    query = sqla.text(query)
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

# plot bar charts
for i in [0,1,3,4]:
    data[i].plot.bar(x=axes_points[i][0], y=axes_points[i][1])
    plt.xlabel(axes[i][0])
    plt.ylabel(axes[i][1])
    plt.title("bar chart")
    plt.show()

# plot histogram
data[2].plot.hist(x=axes_points[2][0], y=axes_points[2][1])
plt.xlabel(axes[2][0])
plt.ylabel(axes[2][1])
plt.title("histogram")
plt.show()
