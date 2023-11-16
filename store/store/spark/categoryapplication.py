from pyspark.sql import SparkSession
from pyspark.sql.functions import sum,desc,asc

import os

PRODUCTION = True if ("PRODUCTION" in os.environ) else False
DATABASE_IP = os.environ["DATABASE_IP"] if ("DATABASE_IP" in os.environ) else "localhost"

builder = SparkSession.builder.appName("PySpark Database example")

if (not PRODUCTION):
    builder = builder.master("local[*]") \
        .config(
        "spark.driver.extraClassPath",
        "mysql-connector-j-8.0.33.jar"
    )

spark = builder.getOrCreate()

products = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_IP}:3306/store") \
    .option("dbtable", "store.products") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

orderproduct = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_IP}:3306/store") \
    .option("dbtable", "store.orderproduct") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

orders = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_IP}:3306/store") \
    .option("dbtable", "store.orders") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

categories = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_IP}:3306/store") \
    .option("dbtable", "store.categories") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

productcategory = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_IP}:3306/store") \
    .option("dbtable", "store.productcategory") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

first=categories.join(productcategory,productcategory["categoryId"]==categories["idC"])
second=first.join(products,products["idP"]==first["productId"])
third=second.join(orderproduct,second["idP"]==orderproduct["productId"])
fourth=third.join(orders,third["orderId"]==orders["idO"])
fifth=fourth.filter(fourth["status"]=="COMPLETE")
sixth=fifth.groupby("idC").agg(sum("quantity"))
seventh=categories.join(sixth,categories["idC"]==sixth["idC"],"left")
eighth=seventh.fillna({"sum(quantity)":0})
ninth=eighth.orderBy(desc("sum(quantity)"),asc("categoryName"))

with open('outputCategories.txt', 'w') as f:
    for i in ninth.collect():
        f.write(i["categoryName"]+'\n')

spark.stop()






