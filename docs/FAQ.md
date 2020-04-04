## FAQ

### What does Kubails actually _do_?

Ultimately, **Kubails** is a CLI tool that wraps together many technologies like **Docker**, **Kubernetes**, **Terraform**, and **Google Cloud Platform (GCP)**. It removes the drudgery of manually configuring all these tools to work together so that you focus more on product development.

When creating a new Kubails project, you get an entire folder structure bootstrapped for you. It will contain all the configuration needed to get up and running, including Terraform configs, Helm manifests, and Cloud Build (CI/CD) config. Learn more about [Folder Structure](#TODO).

Additionally, you can choose from some predefined templates for generating your services (e.g. frontend, backend, etc). Learn more about [Service Templates](#TODO).

Once the project has been created, you can deploy all of the necessary infrastructure to your GCP project of choice using the `kubails` CLI. Among other things, this will create a Kubernetes (GKE) cluster where all your code will be deployed as Docker services. Learn more about [Infrastructure](#TODO).

Finally, during development, a **Cloud Build** pipeline will automatically deploy code from _every_ commit from _every_ branch to a live environment on the Kubernetes cluster. Each branch gets its own dedicated URL (with SSL/TLS) and cluster namespace, so that all branches are functionally equivalent (including your master/production branch). Learn more about [Per Branch Deployments](#TODO) and [CI/CD](#TODO).

### Wait, you said _a_ Kubernetes cluster? Like one? For everything?

Yes, each branch (including the one you designate as 'production', e.g. `master`) gets deployed onto a single Kubernetes cluster.

Now, this cluster can be configured with as many nodes as you need, but obviously having production colocated with a bunch of 'staging' environments isn't an ideal high-availability setup.

However, high-availability isn't the point of a Kubails setup; rapid deployment and prototyping is. Heck, the default node type is 'preemptible' (i.e. the node can be deleted at any time) to save on server costs, so high-availability _really_ isn't the goal.

### What if I _do_ want high-availability?

Then don't use Kubails.

But if you _do_ use Kubails, then you have a couple options.

First, the Kubernetes cluster could always be reconfigured to be regional (i.e. multi-zonal) so that nodes (and masters) are spread across more than one zone. Additionally, using non-preemptible (i.e. regular) nodes would also be a good step.

But if you want to go so far as to keep production in an entirely separate cluster, then even while it is technically possible, I would suggest not using Kubails.

### What exactly are the technologies that Kubails uses?

Here's a quick rundown:

- `kubails` CLI: Written in **Python** with the [click](https://click.palletsprojects.com/en/7.x/) CLI framework
- Infrastructure management: [Terraform](https://www.terraform.io/)
- Cloud hosting: [Google Cloud Platform](https://cloud.google.com/) (GCP)
- Service containerization: [Docker](https://www.docker.com/)
- Container orchestration: [Kubernetes](https://cloud.google.com/kubernetes-engine) (GKE)
- Kubernetes manifests: Templated using [Helm](https://helm.sh/) (Tiller is not used)
- CI/CD: [Cloud Build](https://cloud.google.com/cloud-build)
- DNS: [Cloud DNS](https://cloud.google.com/dns)
- SSL/TLS: [Let's Encrypt](https://letsencrypt.org/) through [cert-manager](https://github.com/jetstack/cert-manager)
- Secrets Management: [Cloud Key Management Service](https://cloud.google.com/kms)
- Monitoring: [Stackdriver](https://cloud.google.com/products/operations)
- Git hosting: Supports repositories hosted on [GitHub](https://github.com/) and [Bitbucket](https://bitbucket.org/)

### Do I need to know how Docker, Kubernetes, Terraform, etc. work?

For the most part, yes! Unlike a managed service, using Kubails for your project is a 'host it yourself, manage it yourself' situation.

And while Kubails can get you pretty far, I'd be lying if I said it could completely replace your DevOps team :)

As such, you'll want to be familiar with most, if not all, of the underlying technologies in order to be able adapt them to fit your changing needs as well as to fix things as they come up.

### What if I want to replace your technology choice X with my technology choice Y?

Well depending on which technology X is (and which technology Y is), that may be next to impossible.

You're of course free to _try_ and switch technologies around, but that kind of defeats the purpose of Kubails being a _highly-opionated_ framework.

So... sorry, but only my technology choice X is supported!

### Aww come on, I really want to use AWS instead of GCP...

I had toyed around with porting Kubails to AWS at one point, but life got in the way...

Ultimately, it _should_ be doable, since Kubernetes is Kubernetes and everything else more-or-less has AWS equivalents, but I'm personally happy enough with GCP at the moment that I don't care enough to port it.

Of course, if someone wants to contribute a port, by all means!

So... no AWS! (for now)

### I saw 'centralized configuration' mentioned as a feature? Something about a `kubails.json` file?

Yes! One of the biggest selling points of Kubails is that it provides a way to share configuration between all the different tools it uses (most notably, between Helm and Terraform).

With the `kubails.json` file at the root of every project, Kubails can take these values and inject them into all of its the tools. This means no more copy/pasting values between Helm's `values.yaml` and Terraform's `.tfvars` — just change the value in `kubails.json` and you're good to go.

### Ugh, another configuration file I have to deal with?

Yep!

### Wait, why is the configuration file JSON? Why can't it be YAML?

Well, originally it was because I thought a JSON file could be used directly as a `-var-file` for Terraform and a values file for Helm (since JSON is technically a subset of YAML), but due to some technical limitations that I hit, this wasn't possible.

However, I had already gotten so far using a JSON file for configuration that I didn't bother switching it out for YAML, so... here we are.

Adding support for a `kubails.yaml` file might be something to come in the future.

### Why should I use Kubails? Why should I use Kubails over X?

Good question! See [this page](#TODO) if you need some more convincing.

### Why should I _not_ use Kubails?

An equally good question! We've got a [page](#TODO) for that too.
