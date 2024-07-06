#!/usr/bin/env python3

from app import app
from models import db, Restaurant, Pizza, RestaurantPizza
from faker import Faker

fake = Faker()

with app.app_context():

    # This will delete any existing rows
    # so you can run the seed file multiple times without having duplicate entries in your database
    print("Deleting data...")
    Pizza.query.delete()
    Restaurant.query.delete()
    RestaurantPizza.query.delete()

    print("Creating restaurants...")
    restaurants = []
    for _ in range(10):
        restaurant = Restaurant(name=fake.company(), address=fake.address())
        restaurants.append(restaurant)

    print("Creating pizzas...")
    pizzas = []
    for _ in range(10):
        pizza = Pizza(
            name=fake.first_name(),
            ingredients=fake.words(nb=4, ext_word_list=None, unique=True),
        )
        pizzas.append(pizza)

    print("Creating RestaurantPizza...")
    restaurant_pizzas = []
    for _ in range(10):
        restaurant_pizza = RestaurantPizza(
            restaurant=fake.random_element(elements=restaurants),
            pizza=fake.random_element(elements=pizzas),
            price=fake.random_int(min=1, max=20),
        )
        restaurant_pizzas.append(restaurant_pizza)

    db.session.add_all(restaurants)
    db.session.add_all(pizzas)
    db.session.add_all(restaurant_pizzas)
    db.session.commit()

    print("Seeding done!")
