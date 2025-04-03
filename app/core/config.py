import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

ES_HOST = os.getenv("ES_HOST")
ES_INDEX = os.getenv("ES_INDEX")
ES_USERNAME = os.getenv("ES_USERNAME")
ES_PASSWORD = os.getenv("ES_PASSWORD")
