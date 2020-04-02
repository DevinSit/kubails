# {{cookiecutter.title}}

This 'service' is actually a cronjob that gets deployed alongside every namespace to handle doing database backups on a schedule.

Since it is a Kubails servce, all of the necessary configuration can be found in the root `kubails.json` config file. 

# How it Works

Basically, this service has its own image built and stored in Container Registry just like any other service. The only difference is that instead of using a `deployment` template, this service uses a `cronjob` template to run on a set schedule to `pg_dump` the database of the namespace and upload the dump to the `[GCP project ID]-cluster-database-backups` storage bucket. Pretty simple.
