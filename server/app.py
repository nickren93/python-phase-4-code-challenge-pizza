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


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


class Restaurants(Resource):
    def get(self):
        restaurants = [{"id": restaurant.id, "name": restaurant.name, "address": restaurant.address} \
                   for restaurant in Restaurant.query.all()]
        return make_response(restaurants, 200)


class RestaurantByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter(Restaurant.id == id).first()
        if restaurant:
            return make_response(restaurant.to_dict(), 200)   
        return {'error': 'Restaurant not found'}, 404

    def delete(self, id):
        restaurant = Restaurant.query.filter(Restaurant.id == id).first()
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response('', 204)  
        return {'error': 'Restaurant not found'}, 404


class Pizzas(Resource):
    def get(self):
        pizzas = [{"id": pizza.id, "name": pizza.name, "ingredients": pizza.ingredients} \
                   for pizza in Pizza.query.all()]
        return make_response(pizzas, 200)


class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        restaurant = Restaurant.query.filter(Restaurant.id == data.get('restaurant_id')).first()
        pizza = Pizza.query.filter(Pizza.id == data.get('pizza_id')).first()

        if restaurant and pizza:
            try:
                new_restaurant_pizza = RestaurantPizza(price=data.get('price'), \
                                restaurant_id=data.get('restaurant_id'), \
                                pizza_id=data.get('pizza_id'))
                db.session.add(new_restaurant_pizza)
                db.session.commit()
                return make_response(new_restaurant_pizza.to_dict(), 201)
            except ValueError:
                db.session.rollback()
                return {'errors': ["validation errors"]}, 400
            
        return {'errors': ["validation errors"]}, 400


api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantByID, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')


if __name__ == "__main__":
    app.run(port=5555, debug=True)
