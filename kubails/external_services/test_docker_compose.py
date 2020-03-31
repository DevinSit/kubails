from parameterized import parameterized
from unittest import TestCase
from . import docker_compose


mock_services_config = {
    "frontend": {"ports": ["3000:3000"]},
    "backend": {"ports": ["5000:5000"]}
}

no_conflicting_ports = {"name": {"ports": ["1000:1000"]}}

one_conflicting_port = {"name": {"ports": ["3000:3000"]}}
fixed_one_conflicting_port = {"name": {"ports": ["3001:3000"]}}

two_conflicting_port = {"name": {"ports": ["3000:3000", "5000:5000"]}}
fixed_two_conflicting_port = {"name": {"ports": ["3001:3000", "5001:5000"]}}

consecutive_conflicting_ports = {"name": {"ports": ["3000:3000", "3001:3001"]}}
fixed_consecutive_conflicting_ports = {"name": {"ports": ["3001:3000", "3002:3001"]}}


class TestDockerCompose(TestCase):
    def setUp(self):
        self.docker_compose = docker_compose.DockerCompose()

    @parameterized.expand([
        # Case 1: No conflicting ports.
        (mock_services_config, no_conflicting_ports, no_conflicting_ports),

        # Case 2: One conflicting port in the new service.
        (mock_services_config, one_conflicting_port, fixed_one_conflicting_port),

        # Case 3: Two conflicting port in the new service.
        (mock_services_config, two_conflicting_port, fixed_two_conflicting_port),

        # Case 4: Consecutive conflicting ports.
        (mock_services_config, consecutive_conflicting_ports, fixed_consecutive_conflicting_ports)
    ])
    def test_can_fix_conflicting_ports(self, services_config, new_service_config, fixed_service_config):
        self.docker_compose._fix_conflicting_ports(services_config, new_service_config)
        self.assertEqual(new_service_config, fixed_service_config)
