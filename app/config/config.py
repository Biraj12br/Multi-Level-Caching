import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    SQLALCHEMY_DATABASE_URI = (
        f"mysql://"
        f"{os.getenv('MYSQL_USER')}:"
        f"{os.getenv('MYSQL_PASSWORD')}@"
        f"{os.getenv('MYSQL_HOST')}:"
        f"{os.getenv('MYSQL_PORT')}/"
        f"{os.getenv('MYSQL_DB')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = int(os.getenv("REDIS_PORT"))

    L1_CACHE_TTL = int(os.getenv("L1_CACHE_TTL"))
    L2_CACHE_TTL = int(os.getenv("L2_CACHE_TTL"))