from typing import Any, Dict, Type  # noqa
from .config_generators import (  # noqa
    ConfigGenerator,
    DatabaseBackupGenerator,
    ExpressConfigGenerator,
    FlaskConfigGenerator,
    ReactConfigGenerator
)

SERVICE_BACKEND_DATABASE_BACKUP = "backend-database-backup"
SERVICE_BACKEND_EXPRESS = "backend-express"
SERVICE_BACKEND_FEATHERS = "backend-feathers"
SERVICE_BACKEND_FLASK = "backend-flask"
SERVICE_FRONTEND_REACT = "frontend-react"

SERVICE_TEMPLATES = [
    SERVICE_BACKEND_DATABASE_BACKUP,
    SERVICE_BACKEND_EXPRESS,
    SERVICE_BACKEND_FEATHERS,
    SERVICE_BACKEND_FLASK,
    SERVICE_FRONTEND_REACT
]

SERVICES_CONFIG = {
    SERVICE_BACKEND_DATABASE_BACKUP: DatabaseBackupGenerator,
    SERVICE_BACKEND_EXPRESS: ExpressConfigGenerator,
    SERVICE_BACKEND_FEATHERS: ExpressConfigGenerator,
    SERVICE_BACKEND_FLASK: FlaskConfigGenerator,
    SERVICE_FRONTEND_REACT: ReactConfigGenerator
}  # type: Dict[str, Type[ConfigGenerator]]
