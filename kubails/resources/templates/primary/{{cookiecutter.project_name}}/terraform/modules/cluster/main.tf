locals {
    cluster_name = "${var.cluster_base_name}-cluster"
}

# The Kubernetes cluster where all of the application containers will be deployed to.
resource "google_container_cluster" "primary" {
    name = "${local.cluster_name}"
    location = "${var.zone}"
    min_master_version = "${var.cluster_version}"
    remove_default_node_pool = true

    network = "${var.network_link}"
    subnetwork = "${var.subnetwork_link}"

    monitoring_service = "monitoring.googleapis.com/kubernetes"
    logging_service = "logging.googleapis.com/kubernetes"

    # Need to have an IP allocation policy setup so that IP Aliases get enabled.
    # And we need IP Aliases enabled to access a potential Memorystore (Redis) instance.
    # See Step 2 of https://cloud.google.com/memorystore/docs/redis/connecting-redis-instance#connecting-cluster
    ip_allocation_policy = {
        cluster_secondary_range_name = "${var.cluster_secondary_range_name}"
        services_secondary_range_name = "${var.services_secondary_range_name}"
    }

    lifecycle {
        # Terraform always wants to update the network/subnetwork values with a fuller URL, but it doesn't matter.
        # Can just ignore it.
        # As for the node pool, want to ignore it so that changes happen on dedicated resource below.
        ignore_changes = ["node_pool", "network", "subnetwork"]
    }

    node_pool {
        name = "default-pool"
    }
}

# The primary node pool for the Kubernetes cluster.
resource "google_container_node_pool" "primary" {
    name = "${google_container_cluster.primary.name}-node-pool"
    cluster = "${google_container_cluster.primary.name}"
    location = "${var.zone}"
    initial_node_count = "${var.initial_node_count}"
    version = "${var.cluster_version}"

    lifecycle {
        # Ignore changes to version since we want to update it ourselves.
        ignore_changes = ["version"]
    }

    autoscaling {
        min_node_count = "${var.min_node_count}"
        max_node_count = "${var.max_node_count}"
    }

    node_config {
        preemptible = "${var.preemptible_nodes}"
        disk_size_gb = "${var.node_disk_size}"
        machine_type = "${var.node_machine_type}"
        oauth_scopes = ["compute-rw", "storage-rw", "logging-write", "monitoring", "datastore", "pubsub"]

        tags = ["${local.cluster_name}", "nodes"]
    }
}

# A firewall rule that enables the Kubernetes master nodes to access the cert-manager 'webhook' service.
# This 'webhook' service offloads the validation of manifests for cert-manager.
# For reference: https://www.revsys.com/tidbits/jetstackcert-manager-gke-private-clusters/
resource "google_compute_firewall" "allow_cert_manager_webhook_to_cluster" {
    name = "allow-cert-manager-webhook-to-cluster"
    network = "${var.network_link}"

    source_ranges = ["${var.cluster_secondary_range_cidr}", "${var.services_secondary_range_cidr}"]
    target_tags = ["${local.cluster_name}"]

    allow {
        protocol = "tcp"
        ports = ["6443"]
    }
}

# A storage bucket used for storing backups taken from the in-cluster database(s).
resource "google_storage_bucket" "cluster_database_backups" {
    name = "${var.gcp_project}-cluster-database-backups"
    location = "${var.region}"
    storage_class = "NEARLINE"
}
