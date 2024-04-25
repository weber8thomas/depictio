from dotenv import load_dotenv
load_dotenv()

import logging


from depictio.api.v1.configs.settings_models import Settings
from depictio.api.v1.utils import get_config, validate_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(funcName)s - line %(lineno)d - %(message)s")

# Settings
# Overwrite priority: environment variables (.env) > config file (.yaml) > default values
settings = validate_config(get_config("depictio/api/v1/configs/config_backend.yaml"), Settings)

API_BASE_URL = f"http://{settings.fastapi.service_name}:{settings.fastapi.port}"
MONGODB_URL = f"mongodb://{settings.mongodb.service_name}:{settings.mongodb.port}/"
TOKEN = settings.auth.tmp_token

# FIXME: the token above is not used by Dash frontend, only by FastAPI backend
TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NjJhY2FiNDQ3ZDk5OGNkODg5Njc4YzEiLCJleHAiOjE3OTE4NDA0MzZ9.CD-n5cvmn-..."

logger = logging.getLogger("depictio")

logger.info(f"API_BASE_URL: {API_BASE_URL}")
logger.info(f"MONGODB_URL: {MONGODB_URL}")
logger.info(f"TOKEN: {TOKEN}")
logger.info(f"Token from .env: {settings.auth.tmp_token}")

