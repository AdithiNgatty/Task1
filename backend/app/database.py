import os
from pymongo import MongoClient

MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "root")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "example")
MONGO_DB = os.getenv("MONGO_INITDB_DATABASE", "user_auth_db")
MONGO_HOST = os.getenv("MONGO_HOST", "mongodb")  # Use service name from docker-compose

MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:27017/{MONGO_DB}?authSource=admin"

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]