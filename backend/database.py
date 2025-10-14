import os
from dotenv import load_dotenv
import motor.motor_asyncio

# Load environment variables from .env file
load_dotenv()

#Use the MongoDB container hostname ("mongo")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")

# Create MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)

# Define database name
db = client.user_auth_db
