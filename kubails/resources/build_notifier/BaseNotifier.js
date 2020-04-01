class BaseNotifier {
    constructor({id, status, logUrl, sha, provider, owner, repo, branch}) {
        this.id = id;
        this.status = status;
        this.logUrl = logUrl;
        this.sha = sha;
        this.provider = provider;
        this.owner = owner;
        this.repo = repo;
        this.branch = branch;
    }
}

module.exports = BaseNotifier;
