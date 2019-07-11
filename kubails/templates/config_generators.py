from typing import Any, Dict


class ConfigGenerator:
    def __init__(
        self, name: str,
        has_database_volume: bool = False,
        has_deps_volume: bool = False
    ) -> None:
        self.name = name
        self.has_database_volume = has_database_volume
        self.has_deps_volume = has_deps_volume

    def generate_kubails_config(self) -> Dict[str, Any]:
        return {}

    def generate_compose_config(self) -> Dict[str, Any]:
        return {}

    def has_compose_database_volume(self) -> bool:
        return self.has_database_volume

    def has_compose_deps_volume(self) -> bool:
        return self.has_deps_volume


class ExpressConfigGenerator(ConfigGenerator):
    def __init__(self, name: str) -> None:
        ConfigGenerator.__init__(
            self,
            name,
            has_database_volume=True,
            has_deps_volume=True
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
    def __init__(self, name: str) -> None:
        ConfigGenerator.__init__(
            self,
            name,
            has_database_volume=False,
            has_deps_volume=False
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
    def __init__(self, name: str) -> None:
        ConfigGenerator.__init__(
            self,
            name,
            has_database_volume=False,
            has_deps_volume=True
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
