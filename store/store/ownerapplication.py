from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, ProductCategory,Product,Category
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_
import re
import io
import csv
import requests

application = Flask(__name__)
application.config.from_object(Configuration)

jwt=JWTManager(application)

@application.route("/update", methods=["POST"])
@jwt_required()
def update():
    if not get_jwt_identity():
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    elif int(get_jwt()['role'])!=0:
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    else:
        try:
            tmp = request.files["file"]
        except Exception as e:
            return jsonify({'message': 'Field file is missing.'}), 400
        reader = csv.reader(io.StringIO(request.files["file"].stream.read().decode("utf-8")))
        whichline=0
        products=[]
        pk=[]
        for row in reader:
            if(len(row)>=3):
                if(re.match(r'\b\+?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?\b',row[2])):
                    if(not Product.query.filter(Product.name==row[1]).first()):
                        temp=[]
                        temp.append(row[1])
                        temp.append(float(row[2]))
                        products.append(temp)
                        temp2=[]
                        temp2.append(row[1])
                        for k in row[0].split('|'):
                            temp2.append(k)
                        pk.append(temp2)
                    else:
                        return jsonify({'message': 'Product '+row[1]+' already exists.'}), 400
                else:
                    return jsonify({'message': 'Incorrect price on line ' + str(whichline) + '.'}), 400
            else:
                return jsonify({'message': 'Incorrect number of values on line '+str(whichline)+'.'}), 400
            whichline=whichline+1
        for p in products:
            database.session.add(Product(name=p[0],price=p[1]))
            database.session.commit()
        for p in pk:
            ind=0
            for p1 in p:
                if ind!=0:
                    if(not Category.query.filter(Category.categoryName==p1).first()):
                        database.session.add(Category(categoryName=p1))
                        database.session.commit()
                ind=ind+1
        for p in pk:
            ind = 0
            idp=-1
            for p1 in p:
                if ind == 0:
                    idp=Product.query.filter(Product.name==p1).first().idP
                else:
                    database.session.add(ProductCategory(productId=idp,categoryId=Category.query.filter(Category.categoryName == p1).first().idC))
                    database.session.commit()
                ind = ind + 1
        return jsonify({},200)

@application.route("/", methods=["GET"])
def index():
    return "Hello world!"

@application.route("/product_statistics", methods=["GET"])
@jwt_required()
def product_statistics():
    if not get_jwt_identity():
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    elif int(get_jwt()['role'])!=0:
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    else:
        try:
            response = requests.get(url='http://storespark:5002/spark_products')
            return response.json()
        except Exception as e:
            pass
        return jsonify({}),200

@application.route("/category_statistics", methods=["GET"])
@jwt_required()
def category_statistics():
    if not get_jwt_identity():
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    elif int(get_jwt()['role'])!=0:
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    else:
        try:
            response = requests.get(url='http://storespark:5002/spark_categories')
            return response.json()
        except Exception as e:
            pass
        return jsonify({}),200


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
