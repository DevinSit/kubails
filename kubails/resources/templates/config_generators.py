from typing import Any, Dict, List
from kubails.services.config_store import _ConfigStore

ExtraConfigType = Dict[str, str]
ExtraConfigOptionsType = List[ExtraConfigType]


class ConfigGenerator:
    """
    Base class from which service-dependent config generators are extended from.
    Really more of an interface than anything.
    """

    extra_config_options = []  # type: ExtraConfigOptionsType

    def __init__(
        self,
        name: str,
        config_store: _ConfigStore,
        extra_config: ExtraConfigType,
        has_database_volume: bool = False,
        has_deps_volume: bool = False,
        is_service: bool = True
    ) -> None:
        self.name = name
        self.config_store = config_store
        self.extra_config = extra_config

        self.has_database_volume = has_database_volume
        self.has_deps_volume = has_deps_volume
        self.is_service = is_service

    def generate_kubails_config(self) -> Dict[str, Any]:
        return {}

    def generate_compose_config(self) -> Dict[str, Any]:
        return {}

    def has_compose_database_volume(self) -> bool:
        return self.has_database_volume

    def has_compose_deps_volume(self) -> bool:
        return self.has_deps_volume

    def is_external_service(self) -> bool:
        return self.is_service


class DatabaseBackupGenerator(ConfigGenerator):
    extra_config_options = [
        {
            "option_name": "database_service",
            "prompt": "Enter the name of the database service to backup"
        }
        ]  # type: ExtraConfigOptionsType

    def __init__(self, name: str, config_store: _ConfigStore, extra_config: ExtraConfigType) -> None:
        ConfigGenerator.__init__(
            self,
            name,
            config_store,
            extra_config,
            has_database_volume=False,
            has_deps_volume=False,
            is_service=False
        )

    def generate_kubails_config(self) -> Dict[str, Any]:
        name = self.name
        database_service = self.extra_config["database_service"]
        backup_bucket = "{}-cluster-database-backups".format(self.config_store.gcp_project_id)

        return {
            name: {
                "env": [
                    {
                        "name": "PGHOST",
                        "value": database_service
                    },
                    {
                        "name": "PGDATABASE",
                        "value": "app-database"
                    },
                    {
                        "name": "PGUSER",
                        "value": "app-database-user"
                    },
                    {
                        "name": "BACKUP_BUCKET",
                        "value": backup_bucket
                    }
                ],
                "fixed_tag": "latest",
                "host": None,
                "production_replicas": None,
                "replicas": None,
                "schedule": "0 3 * * *",
                "templates": [
                    "cronjob"
                ]
            }
        }

    def generate_compose_config(self) -> Dict[str, Any]:
        return None


class ExpressConfigGenerator(ConfigGenerator):
    def __init__(self, name: str, config_store: _ConfigStore, extra_config: ExtraConfigType) -> None:
        ConfigGenerator.__init__(
            self,
            name,
            config_store,
            extra_config,
            has_database_volume=True,
            has_deps_volume=True,
            is_service=True
        )

    def generate_kubails_config(self) -> Dict[str, Any]:
        name = self.name
        database_service = "{}-database".format(name)

        return {
            database_service: {
                "container_port": "5432",
                "env": [
                    {
                        "name": "POSTGRES_DB",
                        "value": "app-database"
                    },
                    {
                        "name": "POSTGRES_USER",
                        "value": "app-database-user"
                    }
                ],
                "host": database_service,
                "external_port": "5432",
                "folder": None,
                "image": "postgres:11.1",
                "image_in_project": False,
                "persistent_volume": {
                    "mount_path": "/var/lib/postgresql/data",
                    "storage_class": "standard",
                    "size": "5Gi",
                    "sub_path": "database"
                },
                "templates": [
                    "deployment",
                    "service"
                ],
                "type": "ClusterIP"
            },
            name: {
                "container_port": "5000",
                "external_port": "80",
                "pre_startup_command": "npm run db:retryable-migrate && npm run db:seed",
                "templates": [
                    "deployment",
                    "ingress",
                    "service"
                ],
                "type": "NodePort",
                "wait_for_service": database_service
            }
        }

    def generate_compose_config(self) -> Dict[str, Any]:
        name = self.name
        database_service = "{}-database".format(name)
        database_migrate_service = "{}-migrate".format(database_service)

        return {
            database_service: {
                "image": "postgres:11.1",
                "environment": {
                    "POSTGRES_DB": "app-database",
                    "POSTGRES_USER": "app-database-user"
                },
                "volumes": [
                    "{}-data:/var/lib/postgresql/data".format(database_service)
                ]
            },
            database_migrate_service: {
                "build": {
                    "context": "./{}".format(name)
                },
                "image": name,
                "command": "sh -c \"npm run db:retryable-migrate && npm run db:seed\"",
                "links": [
                    database_service
                ],
                "depends_on": [
                    database_service
                ]
            },
            name: {
                "image": name,
                "command": "npm start",
                "ports": ["5000:5000"],
                "links": [
                    database_service
                ],
                "depends_on": [
                    database_migrate_service,
                    database_service
                ],
                "volumes": [
                    "./{}/:/backend".format(name),
                    "{}-deps:/backend/node_modules".format(name)
                ]
            }
        }


class FlaskConfigGenerator(ConfigGenerator):
    def __init__(self, name: str, config_store: _ConfigStore, extra_config: ExtraConfigType) -> None:
        ConfigGenerator.__init__(
            self,
            name,
            config_store,
            extra_config,
            has_database_volume=False,
            has_deps_volume=False,
            is_service=True
        )

    def generate_kubails_config(self) -> Dict[str, Any]:
        name = self.name

        return {
            name: {
                "container_port": "5000",
                "external_port": "80",
                "templates": [
                    "deployment",
                    "ingress",
                    "service"
                ],
                "type": "NodePort"
            }
        }

    def generate_compose_config(self) -> Dict[str, Any]:
        name = self.name

        return {
            name: {
                "build": "./{}".format(name),
                "environment": {
                    "PYTHONUNBUFFERED": "0"
                },
                "image": "{}".format(name),
                "ports": ["5000:5000"],
                "command": "python src/main.py",
                "volumes": [
                    "./{}/:/app".format(name)
                ]
            }
        }


class ReactConfigGenerator(ConfigGenerator):
    def __init__(self, name: str, config_store: _ConfigStore, extra_config: ExtraConfigType) -> None:
        ConfigGenerator.__init__(
            self,
            name,
            config_store,
            extra_config,
            has_database_volume=False,
            has_deps_volume=True,
            is_service=True
        )

    def generate_kubails_config(self) -> Dict[str, Any]:
        name = self.name

        return {
            name: {
                "container_port": "80",
                "env": [
                    {
                        "name": "NODE_ENV",
                        "value": "production"
                    }
                ],
                "external_port": "80",
                "templates": [
                    "deployment",
                    "ingress",
                    "service"
                ],
                "type": "NodePort"
            }
        }

    def generate_compose_config(self) -> Dict[str, Any]:
        name = self.name

        return {
            name: {
                "build": {
                    "context": "./{}".format(name),
                    "args": {
                        "app_env": "dev"
                    }
                },
                "image": name,
                "ports": ["3000:3000"],
                "volumes": [
                    "./{}/:/frontend".format(name),
                    "{}-deps:/frontend/node_modules".format(name)
                ]
            }
        }
