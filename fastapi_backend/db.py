import pymongo
import redis
from gridfs import GridFS
from fastapi_backend.configs.config import settings

client = pymongo.MongoClient(settings.mongo_url)
db = client[settings.mongo_db]
grid_fs = GridFS(db)
redis_cache = redis.Redis(
    host=settings.redis_host, port=settings.redis_port, db=settings.redis_db
)
