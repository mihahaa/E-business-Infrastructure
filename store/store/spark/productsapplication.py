from pyspark.sql import SparkSession
from pyspark.sql.functions import sum,col

import os

PRODUCTION = True if ("PRODUCTION" in os.environ) else False
print('Are we in a production env?')
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

resultSold=products.join(orderproduct,orderproduct["productId"]==products["idP"]).join(orders,orders["idO"]==orderproduct["orderId"])\
    .filter(orders.status=="COMPLETE").groupby("name").agg(sum(col("quantity")).alias("sold")).collect()

resultWaiting=products.join(orderproduct,orderproduct["productId"]==products["idP"]).join(orders,orders["idO"]==orderproduct["orderId"])\
    .filter(orders.status!="COMPLETE").groupby("name").agg(sum(col("quantity")).alias("waiting")).collect()

with open('outputSold.txt', 'w') as f:
    for row in resultSold:
        f.write(str(row["name"])+'|'+str(row["sold"])+'\n')
with open('outputWaiting.txt', 'w') as f:
    for row in resultWaiting:
        f.write(str(row["name"])+'|'+str(row["waiting"])+'\n')


spark.stop()






