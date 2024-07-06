from flask import Flask, render_template, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, Resource, abort
from flask_cors import CORS
from flask_caching import Cache
import os
import logging

from models import db, Restaurant, RestaurantPizza, Pizza

# Setup Flask
app = Flask(
    __name__,
    static_url_path="",
    static_folder="../client/build",
    template_folder="../client/build",
)

# Configure Flask app
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["CACHE_TYPE"] = "RedisCache"
app.config["CACHE_REDIS_HOST"] = os.environ.get("CACHE_REDIS_HOST")
app.config["CACHE_REDIS_PORT"] = 14610
app.config["CACHE_REDIS_DB"] = 0
app.config["CACHE_REDIS_PASSWORD"] = os.environ.get("CACHE_REDIS_PASSWORD")
app.config["CACHE_DEFAULT_TIMEOUT"] = 700  # Cache timeout in seconds
app.json.compact = False

# Initialize extensions
migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)
CORS(app)
cache = Cache(app)

# Setup logging
logging.basicConfig(level=logging.INFO)


@app.errorhandler(404)
def not_found(e):
    return render_template("index.html")


def fetch_from_cache_or_db(cache_key, db_query_fn):
    """Retrieve data from cache or fallback to database."""
    try:
        cached_data = cache.get(cache_key)
        if cached_data:
            logging.info(f"Cache hit for key: {cache_key}")
            return make_response(cached_data, 200)

        # Fetch from DB
        data = db_query_fn()
        cache.set(cache_key, data)
        return make_response(data, 200)
    except Exception as e:
        logging.error(f"Error fetching data: {str(e)}")
        return make_response({"error": "Database is down and no cache available"}, 500)


class Restaurants(Resource):
    def get(self):
        return fetch_from_cache_or_db(
            "restaurants",
            lambda: [
                res.to_dict(only=("id", "name", "address"))
                for res in Restaurant.query.all()
            ],
        )


class Pizzas(Resource):
    def get(self):
        return fetch_from_cache_or_db(
            "pizzas",
            lambda: [
                res.to_dict(only=("id", "ingredients", "name"))
                for res in Pizza.query.all()
            ],
        )


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
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating RestaurantPizza: {str(e)}")
            abort(400, errors=["validation errors"])


class RestaurantsbyID(Resource):
    def get(self, id):
        return fetch_from_cache_or_db(
            f"restaurant_{id}",
            lambda: Restaurant.query.filter_by(id=id).first_or_404().to_dict(),
        )

    def delete(self, id):
        try:
            restaurant = Restaurant.query.filter_by(id=id).first()
            if not restaurant:
                abort(404, error="Restaurant not found")
            db.session.delete(restaurant)
            db.session.commit()
            cache.delete(f"restaurant_{id}")
            return make_response({}, 204)
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error deleting Restaurant: {str(e)}")
            abort(400, errors=["deletion errors"])


api.add_resource(Restaurants, "/restaurants")
api.add_resource(RestaurantsbyID, "/restaurants/<int:id>")
api.add_resource(Pizzas, "/pizzas")
api.add_resource(ResPizzas, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
