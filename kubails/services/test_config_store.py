from parameterized import parameterized
from unittest import TestCase
from . import config_store


class TestCli(TestCase):
    def setUp(self):
        self.maxDiff = None

    @parameterized.expand([
        # Case 1: Can make no modifications to normal string-type or list-type keys
        (
            {"__gcp_project_id": "some-id", "__some_list": ["a value"]},
            {"__gcp_project_id": "some-id", "__some_list": ["a value"]}
        ),

        # Case 2: Can flatten simple single-nested level maps with strings
        (
            {
                "__services": {
                    "frontend": {
                        "host": "domain.com"
                    }
                }
            },
            {
                "__services": {
                    "frontend__host": "domain.com"
                }
            }
        ),

        # Case 3: Can flatten simple single-nested level maps with lists
        (
            {
                "__services": {
                    "frontend": {
                        "templates": ["deployment", "service", "ingress"]
                    }
                }
            },
            {
                "__services": {
                    "frontend__templates__0": "deployment",
                    "frontend__templates__1": "service",
                    "frontend__templates__2": "ingress"
                }
            }
        ),

        # Case 4: Can flatten complex arbitrarily nested maps with strings or lists
        (
            {
                "__services": {
                    "frontend": {
                        "secrets": {
                            "name": "frontend-secrets",
                            "file": ".env.encrypted",
                            "variables": ["CLIENT_SECRET"]
                        }
                    }
                }
            },
            {
                "__services": {
                    "frontend__secrets__name": "frontend-secrets",
                    "frontend__secrets__file": ".env.encrypted",
                    "frontend__secrets__variables__0": "CLIENT_SECRET"
                }
            }
        ),

        # Case 5: Can flatten lists of maps
        (
            {
                "__services": {
                    "frontend": {
                        "env": [
                            {"name": "NODE_ENV", "value": "production"},
                            {"name": "SOME_ENV", "value": "SOME_VALUE"}
                        ]
                    }
                }
            },
            {
                "__services": {
                    "frontend__env__0__name": "NODE_ENV",
                    "frontend__env__0__value": "production",
                    "frontend__env__1__name": "SOME_ENV",
                    "frontend__env__1__value": "SOME_VALUE"
                }
            }
        ),

        # Case 6: Can flatten complex, arbitrarily nested layers of lists and maps
        (
            {
                "__services": {
                    "frontend": {
                        "env": [
                            {
                                "name": "NODE_ENV",
                                "value": "production",
                                "some_list": [
                                    {"some_key": "some-value"}
                                ]
                            },
                            {"name": "SOME_ENV", "value": "SOME_VALUE"}
                        ]
                    }
                }
            },
            {
                "__services": {
                    "frontend__env__0__name": "NODE_ENV",
                    "frontend__env__0__value": "production",
                    "frontend__env__0__some_list__0__some_key": "some-value",
                    "frontend__env__1__name": "SOME_ENV",
                    "frontend__env__1__value": "SOME_VALUE"
                }
            }
        ),

        # Case 7: Can flatten a top level list that has maps

        (
            {
                "__some-key": [
                    {"some_key": "some_value", "some_key_2": "some_value_2"},
                    {"another_key": "another_value"}
                ]
            },
            {
                "__some-key": {
                    "0__some_key": "some_value",
                    "0__some_key_2": "some_value_2",
                    "1__another_key": "another_value"
                }
            }
        ),

        # Case 8: Can flatten a top level list that has lists

        (
            {
                "__some-key": [
                    ["value1", "value2"],
                    ["value3", "value4"]
                ]
            },
            {
                "__some-key": {
                    "0__0": "value1",
                    "0__1": "value2",
                    "1__0": "value3",
                    "1__1": "value4"
                }
            }
        ),

        # Case 9: Can flatten a top level list that has lists of maps

        (
            {
                "__some-key": [
                    [{"key1": "value1"}, {"key2": "value2"}],
                    [{"key3": "value3"}, {"key4": "value4"}]
                ]
            },
            {
                "__some-key": {
                    "0__0__key1": "value1",
                    "0__1__key2": "value2",
                    "1__0__key3": "value3",
                    "1__1__key4": "value4"
                }
            }
        )
    ])
    def test_flatten_config(self, config, expected_flattened_config):
        config_service = config_store.ConfigStore(config=config)
        flattened_config = config_service.get_flattened_config()
        self.assertDictEqual(flattened_config, expected_flattened_config)
