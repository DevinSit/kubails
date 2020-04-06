---
description: Here's why you should use Kubails for your next project.
---

Here we're going to take a moment to discuss **why I built Kubails** and **why you should use it** for your next project.

If you haven't already, I suggest going through the [Introduction](./README.md) and the [FAQ](./FAQ.md) to learn more about _what_ Kubails is.

# Why did I build Kubails?

I originally built Kubails as **a replacement for a bunch of scripts**. These scripts were more-or-less accomplishing the same things that Kubails does now: managing infrastructure, templating manifests, and enabling Docker services to run in the Cloud.

However, what I really wanted was a **centralized place to store configuration**. Between Helm `values.yaml` files and Terraform `.tfvars`, there was a good bit of data duplication going on. As such, I wanted one spot to put everything.

All together, the first versions of Kubails were just a light wrapper around some existing Terraform and Helm configs that I had been using.

Over time I would add more and more features: per branch deployments, service templates, secrets management, etc.

And now Kubails is a framework for very quickly bootstrapping new projects and proof-of-concepts, while still getting all the benefits of a modern developer experience.

# Why should you use Kubails?

I think there's a few good reasons why you might want to consider trying out Kubails for your next project.

## High level decisions are already made for you

This one's simple: you've already been around the block with a bunch of Cloud technologies and just want someone to bash you over the head and tell you what to use.

Pick Kubails and you've got **a box of decisions ready to go**.

## Getting a new project setup is really fast

**1 hour**. That's roughly how long it takes to get a project up and running.

Take an hour and **play around with Kubails**. You'll either be impressed by all the 'magic', or utterly defeated because my documentation missed something and you can't get it to work for the life of you.

That's OK.

## Per branch deployments are amazing

Seriously, per branch deployments are such a **killer thing to experience** and develop with that _they alone_ are enough to make Kubails worth it.

Here's just **a couple use cases** for who would appreciate this:

* **Product Owners**: Can easily check out in-progress work to make sure it matches the spec without having to spin up the code themselves or getting someone else to do it.
* **QA**: Per branch deployments are the height of 'automated manual testing' — you automatically get an environment for manually testing everything.
* **Designers**: No longer have to stand behind the developers back to see design changes; they can hop onto a branch environment from the comfortable distance afforded by Slack.
* **Developers**: No longer have to worry about 'it works on my machine'. If it works on a branch environment, it'll work in production.

## There is relatively low lock-in

OK, this one is _really_ counterintuitive, but hear me out.

As much as Kubails is highly opinionated about things like infrastructure and project structure, it it **entirely devoid of opinion** of what you run _on_ the infrastructure.

This really goes back to the power of Docker: if you can dockerize a service, then it'll run on Kubails. If it can run on Kubails, then it can **run anywhere a Docker container can**.

I've even experienced this in practice, several times. One time, I built out a prototype using Kubails and then switched the Docker services to be hosted on an on-premise OpenShift cluster.

OpenShift is pretty darn close to Kubernetes, so it's no wonder that went smoothly. But another time, I had finished building an app and just wanted to host it even more cheaply. So all I did was cut out the Docker services and deploy them to GCP [Cloud Run](https://cloud.google.com/run). Serverless — it's great too!

## You already use Docker, Kubernetes, GCP, etc

If you already make use of a lot of the technologies that Kubails does, then this goes back to the first point: all the decisions are made for you.

Except with Kubails, all the tools are well integrated together, so you **don't have to write a bunch of glue scripts** like I did before Kubails.

## You _want_ to use Docker, Kubernetes, GCP, etc

Now this is certainly one of the weaker cases. If you are in the process of learning and trying out all these technologies, then Kubails can help **serve as an example** of how you might tie them all together.

You can setup a Kubails project then **poke around and see how everything works together**. Then you can start deconstructing it and picking off the pieces that you want and just use those.

## You are the creator of Kubails

A little tongue-in-cheek here, but if you are creator the Kubails, then you are **uniquely suited to using Kubails**: you know all the ins-and-outs, how the source code works, what'll break if you try to do something weird, etc.

This is to say that if you haven't dealt with the problems that Kubails solves or felt the power of the solutions it gives, then it'll seem like Kubails is just too much complexity for what you're getting out of it.

# Why should you use Kubails over X?

There's a whole class of various managed and unmanaged products and services for _hosting web apps_, so why would anyone want to **choose Kubails in particular**?

Well, here's a couple of specific examples.

## Heroku and Review Apps

Honestly, there's really only one reason why you might choose Kubails here: **costs**.

As you scale up, running more and more dynos on Heroku can get real expensive, real fast. As such, choosing to go with an unmanaged product like Kubails can help cut down on server costs at a certain scale.

Of course, it also **costs time** (i.e. money) to manage your own stuff, so while Kubails helps to save on setup time, it doesn't exactly eliminate maintenance time.

As such, you should use Kubails over Heroku if you _want_ to manage your own infrastructure and _potentially_ keep monetary costs down.

Otherwise, Heroku's still a solid service.

## Any other managed PaaS (think AWS Elastic Beanstalk, GCP App Engine, etc)

Unless that PaaS has per branch deployments (or some equivalent), then the answer is "**per branch deployments**".

Otherwise, you're probably better off with a managed PaaS.

## A service like [Dockup](https://getdockup.com/)

Here's a type of service that, like Heroku, is much more directly comparable to Kubails.

In effect, this kind of service delivers "managed per branch deployments" — you manage your own server infrastructure and the service gives you a bunch of ondemand staging environments.

Here, Kubails would manage both your server infrastructure _and_ your ondemand staging environments. So if you want an **all-in-one solution**, Kubails might be a good choice.
