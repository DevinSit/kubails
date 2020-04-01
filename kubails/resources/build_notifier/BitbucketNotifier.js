const axios = require("axios");
const BaseNotifier = require("./BaseNotifier");

const BITBUCKET_TOKEN_KEY_NAME = "BITBUCKET_ACCESS_TOKEN";
const BITBUCKET_USER_KEY_NAME = "BITBUCKET_USER";

// Map of Cloud Build statuses to Bitbucket statuses.
const BITBUCKET_STATUS_MAP = {
    QUEUED: "INPROGRESS",
    WORKING: "INPROGRESS",
    SUCCESS: "SUCCESSFUL",
    FAILURE: "FAILED",
    INTERNAL_ERROR: "FAILED",
    TIMEOUT: "FAILED",
    CANCELLED: "STOPPED"
};

class BitbucketNotifier extends BaseNotifier {
    async updateStatus() {
        // Get the access token and user.
        const accessToken = process.env.BITBUCKET_ACCESS_TOKEN;
        const user = process.env.BITBUCKET_USER;

        if (!accessToken || !user) {
            console.log("Bitbucket access token:");
            console.log(accessToken);
            console.log("Bitbucket user:");
            console.log(user);

            throw new Error("Bitbucket access token or user not specified.");
        }

        try {
            const url = this.generateUrl(this.owner, this.repo, this.sha, accessToken, user);

            // Post the new status to the commit SHA at Bitbucket.
            return axios.post(url, {
                state: BITBUCKET_STATUS_MAP[this.status],
                description: `Cloud Build status: ${this.status}`,
                url: this.logUrl,
                key: "GCP-CLOUD-BUILD"
            });
        } catch (e) {
            console.log("Bitbucket request error: ");
            console.log(e);

            throw new Error(e);
        }
    }

    generateUrl(owner, repo, sha, accessToken, user) {
        return `https://${user}:${accessToken}@api.bitbucket.org/2.0/repositories/${owner}/${repo}/commit/${sha}/statuses/build`;
    }
}

module.exports = BitbucketNotifier;
