from depictio.api.v1.configs.settings_models import Settings
from depictio.api.v1.utils import get_config, validate_config

settings = validate_config(
    get_config("depictio/api/v1/configs/config_backend.yaml"), Settings
)
API_BASE_URL = f"http://{settings.fastapi['host']}:{settings.fastapi['port']}"
MONGODB_URL = f"mongodb://{settings.mongo['host']}:{settings.mongo['port']}/"
TOKEN = settings.auth["token"]