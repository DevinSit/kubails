const {IncomingWebhook} = require("@slack/webhook");
const BaseNotifier = require("./BaseNotifier");

class SlackNotifier extends BaseNotifier {
    async sendMessage() {
        // Get the URL for the webhook.
        const webhookUrl = process.env.SLACK_WEBHOOK;

        if (!webhookUrl) {
            console.log("Slack webhook url:");
            console.log(webhookUrl);

            throw new Error("Slack webhook url not specified.");
        }

        const webhook = new IncomingWebhook(webhookUrl);

        const message = {
            mrkdwn: true,
            attachments: [
                {
                    title: `Build \`${this.id}\``,
                    title_link: this.logUrl,
                    color: "danger",
                    fields: [{
                        title: "Status",
                        value: this.status,
                        short: true
                    }, {
                        title: "Repo",
                        value: this.repo,
                        short: true
                    }, {
                        title: "Branch",
                        value: this.branch,
                        short: true
                    }, {
                        title: "Commit",
                        value: this.sha.slice(0, 7),
                        short: true
                    }]
                }
            ]
        };

        return webhook.send(message);
    }
}

module.exports = SlackNotifier;
