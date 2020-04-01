const axios = require("axios");
const BaseNotifier = require("./BaseNotifier");

const GITHUB_KEY_NAME = "GITHUB_ACCESS_TOKEN";

// Map of Cloud Build statuses to Github statuses.
const GITHUB_STATUS_MAP = {
    QUEUED: "pending",
    WORKING: "pending",
    SUCCESS: "success",
    FAILURE: "failure",
    INTERNAL_ERROR: "error",
    TIMEOUT: "error",
    CANCELLED: "failure"
};

class GithubNotifier extends BaseNotifier {
    async updateStatus() {
        // Get the access token.
        const accessToken = process.env.GITHUB_ACCESS_TOKEN;

        if (!accessToken) {
            console.log("GitHub access token:");
            console.log(accessToken);

            throw new Error("GitHub access token not specified.");
        }

        try {
            const url = this.generateUrl(this.owner, this.repo, this.sha, accessToken);

            // Post the new status to the commit SHA at Github
            return axios.post(
                url,
                {
                    state: GITHUB_STATUS_MAP[this.status],
                    description: `Cloud Build status: ${this.status}`,
                    target_url: this.logUrl,
                    context: "GCP Cloud Build"
                },
                {
                    headers: {
                        "User-Agent": "Cloud Build Notifier",
                        "Authorization": `token ${accessToken}`,
                    }
                }
            );
        } catch (e) {
            console.log("GitHub request error:")
            console.log(e);

            throw new Error(e);
        }
    }

    generateUrl(owner, repo, sha, accessToken) {
        return `https://api.github.com/repos/${owner}/${repo}/statuses/${sha}`;
    }
}

module.exports = GithubNotifier;
