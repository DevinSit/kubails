const BaseNotifier = require("./BaseNotifier");
const BitbucketNotifier = require("./BitbucketNotifier");
const GithubNotifier = require("./GithubNotifier");
const SlackNotifier = require("./SlackNotifier");

const PROVIDER_BITBUCKET = "bitbucket";
const PROVIDER_GITHUB = "github";
const SUPPORTED_PROVIDERS = [PROVIDER_BITBUCKET, PROVIDER_GITHUB];

const PROVIDER_NOTIFIER_MAP = {
    [PROVIDER_BITBUCKET]: BitbucketNotifier,
    [PROVIDER_GITHUB]: GithubNotifier
};

// (theoretically) All of the Cloud Build statuses.
const ACTIONABLE_STATUSES = [
    "QUEUED", "WORKING", "SUCCESS", "FAILURE",
    "INTERNAL_ERROR", "TIMEOUT", "CANCELLED"
];

const FAILURE_STATUSES = [
    "FAILURE", "INTERNAL_ERROR", "TIMEOUT"
];

/* A Cloud Function that gets called whenever a message is pushed to the 'cloud-builds' topic.
 * Handles Bitbucket/Github notifications.
 */
exports.gitHostNotifier = async (data, context) => {
    const notifierData = extractNotifierData(data, context, ACTIONABLE_STATUSES);

    if (!notifierData) {
        return;
    }

    const Notifier = PROVIDER_NOTIFIER_MAP[notifierData.provider];
    const notifier = new Notifier(notifierData);

    return notifier.updateStatus();
};

/* A Cloud Function that gets called whenever a message is pushed to the 'cloud-builds' topic.
 * Handles Slack failure notifications.
 */
exports.slackFailureNotifier = async (data, context) => {
    const notifierData = extractNotifierData(data, context, FAILURE_STATUSES);

    if (!notifierData) {
        return;
    }

    const slackNotifier = new SlackNotifier(notifierData);
    return slackNotifier.sendMessage();
};

const extractNotifierData = (data, context, statuses = ACTIONABLE_STATUSES) => {
    const build = parseBuild(data.data);

    // See the end of this file for a sample 'build' object.
    const {id, status, logUrl} = build;

    if (!build.sourceProvenance) {
        // This build doesn't come from a repo; no need to notify anything.
        // For example, App Engine can create builds for itself when deploying.
        return null;
    }

    const sha = build.sourceProvenance.resolvedRepoSource.commitSha;

    if (!sha) {
        // This build doesn't come from a repo; no need to notify anything.
        // For example, App Engine can create builds for itself when deploying.
        return null;
    }

    const {provider, owner, repo} = parseRepoInfo(build);
    const branch = build.source.repoSource.branchName;

    if (
        // Ignore statuses that we don't care about for this notifier.
        // e.g. We use all statuses (ACTIONABLE_STATUSES) for Github/Bitbucket,
        // but we only use the failure statuses (FAILURE_STATUSES) for Slack.
        (statuses.indexOf(status) === -1)

        // Make sure the provider is supported.
        || (!SUPPORTED_PROVIDERS.includes(provider))

        // Only send messages to the specified repo, if one was specified.
        || (process.env.TARGET_REPO && repo !== process.env.TARGET_REPO && process.env.TARGET_REPO !== "all")
    ) {
        return null;
    }

    return new BaseNotifier({id, status, logUrl, sha, provider, owner, repo, branch});
};

const parseBuild = (data) => JSON.parse(new Buffer(data, "base64").toString());

const parseRepoInfo = (build) => {
    // `build.source.repoSource.repoName` looks like this: 'github_devinsit_kubails'.
    //
    // This function assumes a general format of PROVIDER_OWNER_REPO-NAME.
    // This is very likely to not always be true.
    // For example, it used to be hyphens instead of underscores!

    const repoInfo = build.source.repoSource.repoName;
    const [provider, owner, ...repo] = repoInfo.split("_");

    return {
        provider,
        owner,
        // Recombine the repo name if it used underscores.
        repo: repo.join("_")
    };
};

/*

(LATEST) Build object structure for reference (Bitbucket).

"{ id: 'ecec9d77-b929-4707-972c-c4fe2a40bc4c',
  projectId: 'devinsit-personal-projects',
  status: 'WORKING',
  source:
   { repoSource:
      { projectId: 'devinsit-personal-projects',
        repoName: 'bitbucket_dsrobo620_kubails',     <--- Note how it uses underscores instead of hypens now
        branchName: 'KBA-19' } },
  steps:
   [ { name: 'kennethreitz/pipenv',
       args: [Array],
       id: 'Install dependencies, test, and lint',
       waitFor: [Array],
       entrypoint: 'bash' } ],
  createTime: '2018-12-14T04:17:23.162340120Z',
  startTime: '2018-12-14T04:17:24.112070151Z',
  timeout: '600s',
  logsBucket: 'gs://26871575867.cloudbuild-logs.googleusercontent.com',
  sourceProvenance:
   { resolvedRepoSource:
      { projectId: 'devinsit-personal-projects',
        repoName: 'bitbucket_dsrobo620_kubails',
        commitSha: 'ad1ad09c81b6865a6135b38421b7fbe828a77eaa' } },
  buildTriggerId: 'daab55ff-3431-4508-bb0d-b21aa0ca7926',
  options: { substitutionOption: 'ALLOW_LOOSE', logging: 'LEGACY' },
  logUrl: 'https://console.cloud.google.com/gcr/builds/ecec9d77-b929-4707-972c-c4fe2a40bc4c?project=26871575867',
  tags:
   [ 'event-a308a8f6-610b-4b7d-b2fb-19a15a1ce924',
     'trigger-daab55ff-3431-4508-bb0d-b21aa0ca7926' ] } 'build'"
 */

/*
(OLD) Build object structure for reference (Github).

{ id: '09858dba-2518-48c1-ad88-b7fe497cab64',
 projectId: 'testing-kubails',
 status: 'WORKING',
 source:
  { repoSource:
	 { projectId: 'testing-kubails',
	   repoName: 'github-devinsit-kubails',
	   branchName: 'APU-20' } },
 steps:
  [ { name: 'kennethreitz/pipenv',
	  args: [Object],
	  entrypoint: 'bash' } ],
 createTime: '2018-04-26T00:22:07.585674768Z',
 startTime: '2018-04-26T00:22:08.514193270Z',
 timeout: '600s',
 logsBucket: 'gs://93509042731.cloudbuild-logs.googleusercontent.com',
 sourceProvenance:
  { resolvedRepoSource:
	 { projectId: 'testing-kubails',
	   repoName: 'github-devinsit-kubails',
	   commitSha: '8e9dd680f8c26ea41cc73866a1227bf0ec40e774' } },
 buildTriggerId: 'a500fb04-91a4-4d34-ab5d-f2de2d5928e5',
 options: { substitutionOption: 'ALLOW_LOOSE' },
 logUrl: 'https://console.cloud.google.com/gcr/builds/09858dba-2518-48c1-ad88-b7fe497cab64?project=93509042731
',
 substitutions:
  { _INVOCATION_ID: '5bfbf49e-4c09-4bc6-9f6e-82f13584bf66',
	_PLAN_EVALUATION_ID: '9bb2c42c-5615-4c63-863b-4cd45ad115f6',
	_PROJECT_NUMBER: '93509042731' },
 tags:
  [ 'event-885991ab-a45b-4691-af6a-6a7a64f3f07e',
	'trigger-a500fb04-91a4-4d34-ab5d-f2de2d5928e5',
	'eval-9bb2c42c-5615-4c63-863b-4cd45ad115f6',
	'invocation-5bfbf49e-4c09-4bc6-9f6e-82f13584bf66' ] }
*/

/*
(OLD) Build object structure for reference (Bitbucket).

{ id: '4e675e8e-2403-46ab-a5a5-91ed761a4f3a',
 projectId: 'buzzword-bingo-app',
 status: 'WORKING',
 source:
  { repoSource:
	 { projectId: 'buzzword-bingo-app',
	   repoName: 'bitbucket-dsrobo620-cookie-test',
	   branchName: 'testing-3' } },
 steps:
  [ { name: 'gcr.io/buzzword-bingo-app/builder',
	  args: [Object] } ],
 createTime: '2018-08-27T01:16:41.113768989Z',
 startTime: '2018-08-27T01:16:41.864562994Z',
 timeout: '600s',
 logsBucket: 'gs://550665981060.cloudbuild-logs.googleusercontent.com',
 sourceProvenance:
  { resolvedRepoSource:
	 { projectId: 'buzzword-bingo-app',
	   repoName: 'bitbucket-dsrobo620-cookie-test',
	   commitSha: '2b6fcdf42a880693b8d7b60b0a6394478b6e2a78' } },
 buildTriggerId: '1aec2694-c44d-4d8c-bd31-9e97fc3bf342',
 options: { substitutionOption: 'ALLOW_LOOSE' },
 logUrl: 'https://console.cloud.google.com/gcr/builds/4e675e8e-2403-46ab-a5a5-91ed761a4f3a?project=550665981060',
 tags:
  [ 'event-2525932f-f44e-4d37-b421-da671c248abd',
	'trigger-1aec2694-c44d-4d8c-bd31-9e97fc3bf342' ] }
*/
