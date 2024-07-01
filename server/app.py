#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)
class RestaurantListResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict() for restaurant in restaurants]

class RestaurantResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return restaurant.to_dict()
        return {"error": "Restaurant not found"}, 404

    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return '', 204
        return {"error": "Restaurant not found"}, 404

class PizzaListResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict() for pizza in pizzas]

class RestaurantPizzaResource(Resource):
    def post(self):
        data = request.get_json()
        price = data.get('price')
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')

        if not (1 <= price <= 30):
            return {"errors": ["validation errors"]}, 400

        try:
            restaurant_pizza = RestaurantPizza(
                price=price,
                pizza_id=pizza_id,
                restaurant_id=restaurant_id
            )
            db.session.add(restaurant_pizza)
            db.session.commit()
            return restaurant_pizza.to_dict(), 201
        except Exception as e:
            return {"errors": [str(e)]}, 400

api.add_resource(RestaurantListResource, '/restaurants')
api.add_resource(RestaurantResource, '/restaurants/<int:id>')
api.add_resource(PizzaListResource, '/pizzas')
api.add_resource(RestaurantPizzaResource, '/restaurant_pizzas')

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


if __name__ == "__main__":
    app.run(port=5555, debug=True)
