# Prerequisites

- python3 + pip
- git
- terraform 0.11 (https://www.terraform.io/downloads.html)
- gcloud (https://cloud.google.com/sdk/install)
- kubectl (from gcloud)
- docker 
- docker-compose
- helm

Optional:

- node + npm

Pre-steps:

1. Get gcloud authenticated to your project. Run `gcloud auth login` and `gcloud config set project [PROJECT_ID].

# Steps for Infra Deploy

1. Run `kubails new`.
2. Enter information.
3. Turn the folder into a git repo.
4. Push the git repo to GitHub/Bitbucket.
5. Create StackDriver workspace manually.
5. Run `kubails infra setup`.
6. Run `kubails infra deploy`.
7. Follow the prompt to setup name servers.
8. Confirm that name servers have been changed.
9. Once the cluster deployments are complete, now just have to wait for DNS to propagate so that a TLS certificate can be issued.
10. Connect GitHub to Source Repositories manually (i.e. delete the existing repo and then re-connect it).
11. Add Slack token to Cloud Build trigger.
12. Can now start developing and pushing code.

# Changes to be made to Kubails

- Add a MANIFEST.in file to include the templates/builder folders.
- Fix networking/main.tf to use the Terraform 0.12 attributes-as-blocks syntax.
- Fix the labels in monitoring/main.tf to use an 'equals' instead of block for Terraform 0.12.
- Modify the `kubails infra setup` log messages:
    - Change "Enabling APIS..." to "Enabling GCP APIs..."
    - Log a message for each API being enabled.
    - Add "[INFO]" to all user-facing log messages.
    - Add lines above/below log messages that start each step.
- Add better handling when storage bucket for terraform already exists.
- OK, I'm just abandoning Terraform 0.12 because it's doing weird shit to CLI '-var's.
    - Like, I think they changed the parsing so that when a command is like `terraform apply -var='\_\_project\_name="testing-kubails"`, it'll take the quotes as literal (this is what we currently do), but it seems to expect `-var='\_\_project\_name=testing-kubails'`, even though for other types (like lists or maps) it still expects double quotes for values!!! WTF.
- As a result, I think we should just put a message stating "Terraform 0.12 isn't supported yet".
- Need to change the cluster version to 1.15 from 1.15.4 so that it can just take the minor version.
- Need to add a wait for the cert-manager webhook service to come online.
- Well, as is tradition, cert-manager is being an absolute pain in the ass. 
    - Can't get past "dns record not yet propagated", even though they have when checking locally and on the cluster node.
    - Tried upgrading cert-manager to the latest 0.14.1, no dice.
    - I guess I'm just gonna leave it overnight and hope that it magically propagates...
- Investigate why `kubails infra deploy` tries to directly access `./service-account.json`. I think it has to do with the Cloud DNS account?
    - Yep, `deploy_cert_manager` in `services/cluster.py` uses a relative path for the service account file. Will need to change that. I don't know how though...
- Update Dockerfile Node versions
- Update NPM deps
