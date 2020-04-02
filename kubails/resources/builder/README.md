# Kubails Builder

This is a custom build step for GCP Cloud Build. It is used by the Kubails framework to fill in gaps with the default set of Cloud Build builders (namely, running ruby scripts and make commands in an environment that also has access to Helm).

For the curious, the reason ruby scripts are used is because ruby is the only (common/sane) scripting language with a yaml parser in its standard library (i.e. no installation of external libraries is required to parse yaml) -- Node, Python, and Bash all don't have a standard yaml parser (for some reason).

# Deployment

The custom build step (a Docker image) only needs to be deployed once per GCP project. To do so, we can use Cloud Build itself to build and deploy the Docker image ;)

```
gcloud builds submit . --config=cloudbuild.yaml
```

Alternatively, it can be deployed using the `kubails` CLI as part of `kubails infra setup`.

# Example Cloud Build Configuration

Once the Docker image has been deployed, the custom build step can now be referenced in a Cloud Build configuration. For example:

```
steps:
    # Build, tag, and push the Docker containers
    - name: "gcr.io/$PROJECT_ID/kubails-builder"
      args: ["make", "build-push-images"]  # Can reference a (ruby) script that calls 'docker'

    # Generate the Kubernetes manifests from the Helm templates
    - name: "gcr.io/$PROJECT_ID/kubails-builder"
      args: ["make", "generate-manifests"] # Can reference a (ruby) script that calls 'helm'

    # Deploy the manifests to the Kubernetes cluster
    - name: "gcr.io/cloud-builders/kubectl"
      args: ["apply", "--recursive", "-f", "manifests"]
      env:
          - "CLOUDSDK_COMPUTE_ZONE=us-east1-d"
          - "CLOUDSDK_CONTAINER_CLUSTER=some-cluster"
```
