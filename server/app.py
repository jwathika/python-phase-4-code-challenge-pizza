#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, json, request, make_response
from flask_restful import Api, Resource, abort
import os
from flask_cors import CORS

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

CORS(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


class Restaurants(Resource):
    def get(self):
        restaurants: list = [
            res.to_dict(only=("id", "name", "address"))
            for res in Restaurant.query.all()
        ]
        response = make_response(restaurants, 200)
        print(type(restaurants))
        return response


class Pizzas(Resource):
    def get(self):
        pizzas: list = [
            res.to_dict(only=("id", "ingredients", "name")) for res in Pizza.query.all()
        ]
        response = make_response(pizzas, 200)
        return response


class ResPizzas(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_restaurant_pizza = RestaurantPizza(
                price=data["price"],
                pizza_id=data["pizza_id"],
                restaurant_id=data["restaurant_id"],
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return new_restaurant_pizza.to_dict(), 201
        # except ValueError:
        #     db.session.rollback()
        #     abort(400, errors="Price must be between 1 and 30")
        except Exception as e:
            db.session.rollback()
            abort(400, errors=["validation errors"])


class RestaurantsbyID(Resource):
    def get(self, id):

        # if not isinstance(id, int):
        #     return make_response("ID must be an integer", 400)

        restaurant = Restaurant.query.filter_by(id=id).first()

        if not restaurant:
            abort(404, error="Restaurant not found")

        restaurant_dict = restaurant.to_dict()
        # print(type(restaurant_dict))

        return make_response(restaurant_dict, 200)

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if not restaurant:
            abort(404, error="Restaurant not found")
        db.session.delete(restaurant)
        db.session.commit()
        restaurant_dict = {}
        return make_response(restaurant_dict, 204)


api.add_resource(Restaurants, "/restaurants")
api.add_resource(RestaurantsbyID, "/restaurants/<int:id>")
api.add_resource(Pizzas, "/pizzas")
api.add_resource(ResPizzas, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
