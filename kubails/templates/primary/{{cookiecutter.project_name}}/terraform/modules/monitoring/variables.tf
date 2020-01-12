variable "gcp_project" {
    type = "string"
}

variable "domain" {
    type = "string"
}

variable "uptime_check_base_name" {
    type = "string"
}

variable "uptime_check_timeout" {
    type = "string"
    default = "10s"
}

variable "uptime_check_period" {
    type = "string"
    default = "300s"
}

variable "alerts_email" {
    type = "string"
}
