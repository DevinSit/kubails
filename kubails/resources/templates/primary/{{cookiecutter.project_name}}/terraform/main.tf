################################################################################
# TERRAFORM CONFIGURATION
################################################################################

terraform {
    backend "gcs" {
        credentials = "../{{cookiecutter.project_name}}-account.json"
        bucket = "{{cookiecutter.project_name}}-terraform"
    }
}

provider "google" {
    credentials = "../${var.__project_name}-account.json"
    project = "${var.__gcp_project_id}"
    region = "${var.__gcp_project_region}"
    version = "~> 2.20.1"
}

################################################################################
# PRIMARY RESOURCES
################################################################################

module "cicd" {
    source = "./modules/cicd"

    gcp_project = "${var.__gcp_project_id}"
    repo_name = "${var.__project_name}"
    repo_host = "${var.__remote_repo_host}"
    repo_owner = "${var.__remote_repo_owner}"
}

module "kms" {
    source = "./modules/kms"

    region = "${var.__gcp_project_region}"
    key_name = "${var.__gcp_project_id}-key"
    key_ring_name = "${var.__gcp_project_id}-key-ring"
}

module "dns" {
    source = "./modules/dns"

    dns_zone_name = "${var.__project_name}"
    domain = "${var.__domain}" 
    ip_name = "${var.__project_name}-ip"
}

module "networking" {
    source = "./modules/networking"

    region = "${var.__gcp_project_region}"
    network_name = "${var.__project_name}-network"
    subnetwork_name = "${var.__project_name}-subnetwork"
}

module "cluster" {
    source = "./modules/cluster"

    gcp_project = "${var.__gcp_project_id}"
    region = "${var.__gcp_project_region}"
    zone = "${var.__gcp_project_zone}"

    cluster_base_name = "${var.__project_name}"
    initial_node_count = "${var.cluster_initial_node_count}"
    node_machine_type = "${var.cluster_machine_type}"
    node_disk_size = "${var.cluster_disk_size}"
    preemptible_nodes = "${var.cluster_preemptible}"

    network_link = "${module.networking.network_link}"
    subnetwork_link = "${module.networking.subnetwork_link}"

    cluster_secondary_range_name = "${module.networking.subnetwork_secondary_range_1_name}"
    cluster_secondary_range_cidr = "${module.networking.subnetwork_secondary_range_1_cidr}"
    services_secondary_range_name = "${module.networking.subnetwork_secondary_range_2_name}"
    services_secondary_range_cidr = "${module.networking.subnetwork_secondary_range_2_cidr}"
}

module "monitoring" {
    source = "./modules/monitoring"

    gcp_project = "${var.__gcp_project_id}"

    domain = "${var.__domain}"
    uptime_check_base_name = "${var.__project_name}"
    alerts_email = "${var.__domain_owner_email}"
}

module "logging" {
    source = "./modules/logging"

    region = "${var.__gcp_project_region}"
    cluster_name = "${module.cluster.cluster_name}"
    logging_base_name = "${var.__gcp_project_id}"
}
