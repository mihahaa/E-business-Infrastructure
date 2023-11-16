import os;

databaseUrl = os.environ["STORE_DATABASE_URL"];

class Configuration ( ):
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/store";
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
