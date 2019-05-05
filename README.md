# Kubails

`Kubails` is an opinionated framework for **organizing and developing Docker-based services** for deployment on Google Kubernetes Engine (on Google Cloud Platform). `Kubails` combines industry standard DevOps tooling to handle setting up your local development environment, your CI/CD pipeline, and your cloud infrastructure, so that you can focus on what really matters: building your project.

The key features of `Kubails` are:

- **Opinionated Project Architecture**: Worry less about about managing servers, pipelines, and deployments; `Kubails` does the heavy lifting of making these things work for you so that you can focus more on writing your application code.

- **Modern Developer Experience**: With a local docker-compose based development environment and a per-branch Kubernetes deployment setup, you can ensure consistency and reproducibility across the entire lifecycle of your application's development. You can be certain that what you have on your branch is going to work exactly the same way in production.

- **Robust Infrastructure Management**: Combining tools like Terraform, Kubernetes, and Helm, `Kubails` offers a robust and standardized way of managing your immutable cloud infrastructure. The default setup gets you up and running quickly, but leaves open the option to adding or tweaking whatever you need. And with the centralized config file, your infrastructure configuration is as DRY as it can be.

- **Comprehensive CLI**: Wrapping together all of the functionality needed to create, deploy, and manage `Kubails` projects, the `Kubails` CLI acts as the glue-code between all of the different DevOps tools to both centralize project-specific configuration and provide a single interface for controlling your projects.

## ⚠️ Disclaimer

`Kubails` is very much **alpha** software; it is highly advised that you don't go using it for production-class projects.

It is, however, appreciated if you try it out and share your feedback!

## Installation

Before installing the `Kubails` CLI, make sure you meet all of the prerequisites outlined in the [Getting Started](./docs/GettingStarted.md) guide.

The `Kubails` CLI is not yet published on `pip`, so it must be installed **from this repo**:

```
$ git clone git@github.com:DevinSit/kubails.git
$ cd kubails
$ pip install .
```

For more info on getting started and setting up a new `Kubails` project, see the [Getting Started](./docs/GettingStarted.md) guide.

## Documentation

You can find all of the `Kubails` documentation [here](./docs/index.md).

## Roadmap

While GitHub issues are used for public-facing requests, bug reports, etc, a separate **Trello board** is used to organize what is currently being worked on and what is coming up in the future.

It can be found [here](https://trello.com/b/IbIhQ9Bx).

## Contributing

See the [CONTRIBUTING](CONTRIBUTING.md) file for details.

## Authors

- **Devin Sit**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.
