# Kubails

**Kubails** is a highly opinionated framework for enabling rapid deployment and prototyping of Docker-based web services.

That is, if you're developing a web app, **Kubails** makes a bunch of tooling and infrastructure decisions for you so that you can get your app deployed in **less than an hour**. Then you can start iterating quickly while being supported by modern development comforts like **repeatable environments**, **true CI/CD**, and **per branch deployments**.

So if this sounds like the sort of thing that would be helpful for your project, then try out Kubails and get to building _now_.

The key features of Kubails are:

* **Fast initial setup**: Get deployed and developing in less than an hour.
* **Opinionated project architecture**: Worry less about deciding between one person's cloud or another.
* **Robust infrastructure management**: With Terraform and Helm, everything is just configuration as code.
* **Centralized configuration**: `kubails.json` is your entrypoint to keeping Terraform, Helm, and everything else in sync.
* **Scale as you grow**: By the power of _The Cloud™_ and Kubernetes, you can scale as much as you have money.
* **Modern developer experience**: Between Docker and per branch deployments, you can be sure that what works in one place works everywhere.

## ⚠️ Disclaimer

Kubails is still **alpha** software.

While the underlying technologies are mostly production-ready, using **Kubails** for production projects is certainly at **your own risk**!

## Quick Installation

Before installing the `kubails` CLI, make sure you meet all of the prerequisites outlined in the [Getting Started](https://docs.kubails.com/gettingstarted) guide.

The `kubails` CLI is not yet published on `pip`, so it must be installed **from this repo**:

```
$ git clone git@github.com:DevinSit/kubails.git
$ cd kubails
$ pip install .
```

For more info on getting started and setting up a new Kubails project, see the [Getting Started](https://docs.kubails.com/gettingstarted) guide.

## Documentation

You can find all of the Kubails documentation [here](https://docs.kubails.com/).

## Roadmap

While GitHub issues are used for public-facing requests, bug reports, etc, a separate **Trello board** is used to organize what is currently being worked on and what is coming up in the future.

It can be found [here](https://trello.com/b/IbIhQ9Bx).

## Contributing

See the [CONTRIBUTING](CONTRIBUTING.md) file for details.

## Authors

- **Devin Sit**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.
