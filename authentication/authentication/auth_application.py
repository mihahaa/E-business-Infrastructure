from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, User
from email.utils import parseaddr
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_
import re

application = Flask(__name__)
application.config.from_object(Configuration)


@application.route("/register_customer", methods=["POST"])
def register_customer():
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    if len(email) == 0 or len(password) == 0 or len(forename) == 0 or len(surname) == 0:
        if len(forename) == 0:
            return jsonify({'message': 'Field forename is missing.'}), 400
        elif len(surname) == 0:
            return jsonify({'message': 'Field surname is missing.'}), 400
        elif len(email) == 0:
            return jsonify({'message': 'Field email is missing.'}), 400
        else:
            return jsonify({'message': 'Field password is missing.'}), 400
    else:
        if not re.match(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',email):
            return jsonify({'message': 'Invalid email.'}), 400
        else:
            if len(password) < 8:
                return jsonify({'message': 'Invalid password.'}), 400
            else:
                if User.query.filter(User.email == email).first():
                    return jsonify({'message': 'Email already exists.'}), 400
                else:
                    user = User(forename=forename, surname=surname, email=email, password=password, role=2)
                    database.session.add(user)
                    database.session.commit()
                    return jsonify({}), 200


@application.route("/register_courier", methods=["POST"])
def register_courier():
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    if len(email) == 0 or len(password) == 0 or len(forename) == 0 or len(surname) == 0:
        if len(forename) == 0:
            return jsonify({'message': 'Field forename is missing.'}), 400
        elif len(surname) == 0:
            return jsonify({'message': 'Field surname is missing.'}), 400
        elif len(email) == 0:
            return jsonify({'message': 'Field email is missing.'}), 400
        else:
            return jsonify({'message': 'Field password is missing.'}), 400
    else:
        if not re.match(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',email):
            return jsonify({'message': 'Invalid email.'}), 400
        else:
            if len(password) < 8:
                return jsonify({'message': 'Invalid password.'}), 400
            else:
                if User.query.filter(User.email == email).first():
                    return jsonify({'message': 'Email already exists.'}), 400
                else:
                    user = User(forename=forename, surname=surname, email=email, password=password, role=1)
                    database.session.add(user)
                    database.session.commit()
                    return jsonify({}), 200


jwt = JWTManager(application)


@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    refreshClaims = get_jwt()

    additionalClaims = {
        "forename": refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "role": refreshClaims["role"],

    }

    return Response(create_access_token(identity=identity, additional_claims=additionalClaims), status=200)


@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    if len(email) == 0 or len(password) == 0:
        if len(email) == 0:
            return jsonify({'message': 'Field email is missing.'}), 400
        else:
            return jsonify({'message': 'Field password is missing.'}), 400
    else:

        if not re.match(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',email):
            return jsonify({'message': 'Invalid email.'}), 400
        else:
            user = User.query.filter(and_(User.email == email, User.password == password)).first()

            if not user:
                return jsonify({'message': 'Invalid credentials.'}), 400
            else:
                f = user.forename
                s = user.surname
                r = user.role
                e = user.email
                i = user.id

                additionalClaims = {
                    "forename": f,
                    "surname": s,
                    "role": str(r),
                    "id": str(i)
                }

                accessToken = create_access_token(identity=e, additional_claims=additionalClaims)
                refreshToken = create_refresh_token(identity=e, additional_claims=additionalClaims)

                return jsonify(accessToken=accessToken, refreshToken=refreshToken)


@application.route("/delete", methods=["POST"])
@jwt_required()
def delete():
    e = get_jwt_identity()

    if not e:
        return jsonify({'msg': 'Missing Authorization Header'}), 401
    else:
        if not User.query.filter(User.email == e).first():
            return jsonify({'message': 'Unknown user.'}), 400
        else:
            database.session.delete(User.query.filter(User.email == e).first())
            database.session.commit()
            return jsonify({}, 200)


@application.route("/check", methods=["POST"])
@jwt_required()
def check():
    return "Token is valid!"

@application.route("/", methods=["GET"])
def index():
    return "Hello world!"

if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)



