from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, ProductCategory, Product, Category,Order,OrderProduct
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_
import re
import datetime
import io
import csv


application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)

@application.route("/", methods=["GET"])
def index():
    return "Hello world!"


@application.route("/pick_up_order", methods=["POST"])
@jwt_required()
def pick_up_order():
    if not get_jwt_identity():
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    elif int(get_jwt()['role']) != 1:
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    else:
        try:
            tmp = request.json["id"]
        except Exception as e:
            return jsonify({'message': 'Missing order id.'}), 400
        r = request.json["id"]
        if(not re.match(r'\b[1-9]\d*\b',str(r))):
            return jsonify({'message': 'Invalid order id.'}), 400
        o=Order.query.filter(and_(Order.idO == str(r),Order.status!="PENDING",Order.status!="COMPLETE")).first()
        if(o):
            pass
        else:
            return jsonify({'message': 'Invalid order id.'}), 400
        o.status="PENDING"
        database.session.commit()
        return jsonify({},200)

@application.route("/orders_to_deliver", methods=["GET"])
@jwt_required()
def orders_to_deliver():
    if not get_jwt_identity():
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    elif int(get_jwt()['role']) != 1:
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    else:
        return jsonify({"orders":[{"id":item.idO,"email":item.userEmail} for item in Order.query.filter(Order.status=="CREATED").all()]}),200

if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)