locals {
    frontend_check = "${var.uptime_check_base_name}-frontend"
}

# Uptime check for monitoring the frontend -- i.e. the root domain.
resource "google_monitoring_uptime_check_config" "frontend_check" {
    display_name = "${local.frontend_check}"
    timeout = "${var.uptime_check_timeout}"
    period = "${var.uptime_check_period}"

    http_check {
        path = "/"
        port = "443"
        use_ssl = true
        validate_ssl = true
    }

    monitored_resource {
        type = "uptime_url"
        
        labels = {
            project_id = "${var.gcp_project}"
            host = "${var.domain}"
        }
    }
}

# Notification channel for emails.
resource "google_monitoring_notification_channel" "email" {
    display_name = "Email Alerts"
    type = "email"

    labels = {
        email_address = "${var.alerts_email}"
    }
}

# Alerting policy for the frontend check that alerts on the email
# notification channel whenever the uptime check fails.
resource "google_monitoring_alert_policy" "frontend_check_alerting_policy" {
    display_name = "${var.uptime_check_base_name}-frontend-alerting-policy"
    combiner = "OR"

    conditions {
        display_name = "Uptime Check for ${local.frontend_check}"

        # Figuring out this whole configuration was done by manually by creating an Uptime Check alerting policy
        # and then inspecting its configuration using `gcloud alpha monitoring policies list`.
        condition_threshold {
            filter = "resource.type=\"uptime_url\" AND metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND metric.label.check_id=\"${google_monitoring_uptime_check_config.frontend_check.uptime_check_id}\""

            aggregations {
                alignment_period = "1200s"
                cross_series_reducer = "REDUCE_COUNT_FALSE"
                per_series_aligner = "ALIGN_NEXT_OLDER"
                group_by_fields = ["resource.*"]
            }

            comparison = "COMPARISON_GT"
            duration = "${var.uptime_check_period}"
            threshold_value = "1"

            trigger {
                count = "1"
            }
        }
    }

    notification_channels = ["${google_monitoring_notification_channel.email.name}"]
}
