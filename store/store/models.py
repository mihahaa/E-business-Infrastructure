from flask_sqlalchemy import SQLAlchemy;

database = SQLAlchemy()


class ProductCategory(database.Model):
    __tablename__ = "productcategory";
    idPC = database.Column(database.Integer, primary_key=True);
    productId = database.Column(database.Integer, database.ForeignKey("products.idP"), nullable=False);
    categoryId = database.Column(database.Integer, database.ForeignKey("categories.idC"), nullable=False);


class Category(database.Model):
    __tablename__ = "categories"

    idC = database.Column(database.Integer, primary_key=True)
    categoryName = database.Column(database.String(256), nullable=False, unique=True)

    products = database.relationship("Product", secondary=ProductCategory.__table__, back_populates="categories")

class OrderProduct(database.Model):
    __tablename__ = "orderproduct";
    idOP = database.Column(database.Integer, primary_key=True);
    orderId = database.Column(database.Integer, database.ForeignKey("orders.idO"), nullable=False);
    productId = database.Column(database.Integer, database.ForeignKey("products.idP"), nullable=False);
    quantity = database.Column(database.Integer, nullable=False)

class Product(database.Model):
    __tablename__ = "products"

    idP = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False, unique=True)
    price = database.Column(database.Float, nullable=False)

    categories = database.relationship("Category", secondary=ProductCategory.__table__, back_populates="products")
    orders=database.relationship("Order", secondary=OrderProduct.__table__, back_populates="products")

class Order(database.Model):
    __tablename__ = "orders"

    idO = database.Column(database.Integer, primary_key=True)
    userId = database.Column(database.Integer, nullable=False)
    status = database.Column(database.String(256), nullable=False)
    timestamp = database.Column(database.DateTime, nullable=False)
    userEmail = database.Column(database.String(256), nullable=False)

    products = database.relationship("Product", secondary=OrderProduct.__table__, back_populates="orders")

