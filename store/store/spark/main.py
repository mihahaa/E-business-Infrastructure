from flask import Flask
import os
import subprocess

application = Flask(__name__)


@application.route("/spark_products", methods=["GET"])
def spark_products():
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "/app/productsapplication.py"

    os.environ["SPARK_SUBMIT_ARGS"] = "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"

    result = subprocess.check_output(["/template.sh"])
    md={}

    try:

        with open('outputSold.txt', 'r') as f:
            ls=f.readlines()
        for row in ls:
            name=row.split('|')[0]
            application.logger.info(f'name is {name}\n')
            sold=row.split('|')[1]
            application.logger.info(f'sold is {sold}\n')
            md[name]={
                "name":name,
                "sold":int(sold),
                "waiting":0
            }
        with open('outputWaiting.txt', 'r') as f:
            ls=f.readlines()
        for row in ls:
            name = row.split('|')[0]
            application.logger.info(f'name is {name}\n')
            waiting = row.split('|')[1]
            application.logger.info(f'waiting is {waiting}\n')
            if name not in md.keys():
                md[name]={
                    "name":name,
                    "sold":0,
                    "waiting":int(waiting)
                }
            else:
                md[name]["waiting"] = int(waiting)

        lista = []

        for key, value in md.items():
            application.logger.info(f'value is {value}\n')
            lista.append(value)
        sol={'statistics':lista}
        application.logger.info(sol)
        return sol

    except Exception as e:
        application.logger.info("sjebo")
    return result.decode()

@application.route("/spark_categories", methods=["GET"])
def spark_categories():
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "/app/categoryapplication.py"

    os.environ["SPARK_SUBMIT_ARGS"] = "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"

    result = subprocess.check_output(["/template.sh"])
    application.logger.info(result.decode())
    try:
        with open('outputCategories.txt', 'r') as f:
            ls = f.readlines()
        lista=[]
        for l in ls:
            lista.append(l[:-1])
        return { 'statistics':lista }
    except Exception as e:
        pass
    return result.decode()

if (__name__ == "__main__"):
    application.run(host="0.0.0.0", debug=True, port=5002)