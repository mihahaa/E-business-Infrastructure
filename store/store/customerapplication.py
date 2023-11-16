from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, ProductCategory, Product, Category, Order, OrderProduct
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


@application.route("/search", methods=["GET"])
@jwt_required()
def search():
    if not get_jwt_identity():
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    elif int(get_jwt()['role']) != 2:
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    else:
        p = request.args.get('name')
        c = request.args.get('category')
        if p is None:
            p = ''
        if c is None:
            c = ''
        k1 = Category.query.join(ProductCategory).join(Product).filter(Product.name.like(f"%{p}%")).all()
        k1 = list(set(k1))
        k2 = Category.query.filter(Category.categoryName.like(f"%{c}%")).all()
        k2 = list(set(k2))
        kf = []
        for item1 in k1:
            for item2 in k2:
                if item1.categoryName == item2.categoryName:
                    kf.append(item1)
        kf = list(set(kf))
        p1 = Product.query.join(ProductCategory).join(Category).filter(Category.categoryName.like(f"%{c}%")).all()
        p1 = list(set(p1))
        p2 = Product.query.filter(Product.name.like(f"%{p}%")).all()
        p2 = list(set(p2))
        pf = []
        for item1 in p1:
            for item2 in p2:
                if item1.name == item2.name:
                    pf.append(item1)
        pf = list(set(pf))

        pff = []

        for item in pf:
            pff.append({
                "categories": [item1.categoryName for item1 in
                               Category.query.join(ProductCategory).join(Product).filter(Product.idP == item.idP).all()],
                "id": item.idP,
                "name": item.name,
                "price": item.price
            })

        sol = {
            "categories": [item.categoryName for item in kf],
            "products": pff
        }

        return jsonify(sol), 200


@application.route("/", methods=["GET"])
def index():
    return "Hello world!"


@application.route("/order", methods=["POST"])
@jwt_required()
def order():
    if not get_jwt_identity():
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    elif int(get_jwt()['role']) != 2:
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    else:
        try:
            tmp = request.json["requests"]
        except Exception as e:
            return jsonify({'message': 'Field requests is missing.'}), 400
        reqs = request.json["requests"]
        ind = 0
        for r in reqs:
            try:
                tmp = r["id"]
            except Exception as e:
                return jsonify({'message': 'Product id is missing for request number ' + str(ind) + '.'}), 400
            try:
                tmp = r["quantity"]
            except Exception as e:
                return jsonify({'message': 'Product quantity is missing for request number ' + str(ind) + '.'}), 400
            if (re.match(r'\b[1-9]\d*\b', str(r["id"]))):
                if (re.match(r'\b[1-9]\d*\b', str(r["quantity"]))):
                    if (Product.query.filter(Product.idP == r["id"]).first()):
                        pass
                    else:
                        return jsonify({'message': 'Invalid product for request number ' + str(ind) + '.'}), 400
                else:
                    return jsonify({'message': 'Invalid product quantity for request number ' + str(ind) + '.'}), 400
            else:
                return jsonify({'message': 'Invalid product id for request number ' + str(ind) + '.'}), 400
            ind = ind + 1
        o = Order(userId=int(get_jwt()['id']), status="CREATED", timestamp=datetime.datetime.utcnow().isoformat(),userEmail=get_jwt_identity())
        database.session.add(o)
        database.session.commit()
        for r in reqs:
            database.session.add(OrderProduct(orderId=o.idO, productId=r["id"], quantity=r["quantity"]))
            database.session.commit()
        return jsonify({'id': o.idO}), 200


@application.route("/status", methods=["GET"])
@jwt_required()
def status():
    if not get_jwt_identity():
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    elif int(get_jwt()['role']) != 2:
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    else:
        orderi = Order.query.filter(Order.userId == get_jwt()['id']).all()
        listf = []
        for o in orderi:
            ordi = OrderProduct.query.filter(OrderProduct.orderId == o.idO).all()
            pf = []
            cf = 0
            for o1 in ordi:
                katovi = [k.categoryName for k in
                          Category.query.join(ProductCategory).filter(ProductCategory.productId == o1.productId).all()]
                p = Product.query.filter(Product.idP == o1.productId).first()
                n1 = {
                    "categories": katovi,
                    "name": p.name,
                    "price": p.price,
                    "quantity": o1.quantity
                }
                pf.append(n1)
                cf = cf + (p.price * o1.quantity)
            n2 = {
                "products": pf,
                "price": cf,
                "status": o.status,
                "timestamp": o.timestamp
            }
            listf.append(n2)
        n3 = {
            "orders": listf
        }
        return jsonify(n3), 200


@application.route("/delivered", methods=["POST"])
@jwt_required()
def delivered():
    if not get_jwt_identity():
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    elif int(get_jwt()['role']) != 2:
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    else:
        try:
            tmp = request.json["id"]
        except Exception as e:
            return jsonify({'message': 'Missing order id.'}), 400
        r = request.json["id"]
        if (not re.match(r'\b[1-9]\d*\b', str(r))):
            return jsonify({'message': 'Invalid order id.'}), 400
        o = Order.query.filter(and_(Order.idO == str(r), Order.status != "CREATED", Order.status != "COMPLETE")).first()
        if (o):
            pass
        else:
            return jsonify({'message': 'Invalid order id.'}), 400
        o.status = "COMPLETE"
        database.session.commit()
        return jsonify({}, 200)

if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
