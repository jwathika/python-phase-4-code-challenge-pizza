from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # add relationship
    pizzas = db.relationship(
        "RestaurantPizza", back_populates="restaurant", lazy="dynamic"
    )
    # add serialization rules
    serialize_rules = ("-restaurant_pizzas.restaurant",)

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # add relationship
    restaurants = db.relationship(
        "RestaurantPizza", back_populates="pizza", lazy="dynamic"
    )
    # add serialization rules
    serialize_rules = ("-restaurant_pizzas.pizza",)

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(
        db.Integer,
        CheckConstraint("price > 0 AND price <= 30"),
        nullable=False,
    )
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"))
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"))
    pizza = db.relationship(
        "Pizza",
        back_populates="restaurants",
        cascade="all,delete",
        uselist=False,
    )
    restaurant = db.relationship(
        "Restaurant", back_populates="pizzas", cascade="all,delete", uselist=False
    )

    # add validation
    @validates("price")
    def validate_price(self, key, value):
        if not (1 <= value <= 30):
            raise ValueError("Price must be between 1 and 30")
        return value

    # add serialization rules
    serialize_rules = ("-restaurant.restaurant_pizzas", "-pizza.restaurant_pizzas")

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
