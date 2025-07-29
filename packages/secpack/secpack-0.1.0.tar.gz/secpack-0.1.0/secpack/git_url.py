import re

class ParsedGitURL:
    """
    A simple class representing the parsed components of a Git URL or path.
    """
    def __init__(self, type_, resource, user, repo):
        self.type = type_
        self.resource = resource
        self.user = user
        self.repo = repo

    def __str__(self):
        return "<ParsedGitURL type={} resource={} user={} repo={}>".format(
            self.type, self.resource, self.user, self.repo
        )

    def __repr__(self):
        return self.__str__()


def is_valid_github_username(username):
    """
    Validates a GitHub username based on length, allowed characters, and no consecutive dashes.
    """
    return (
        1 <= len(username) <= 39 and
        re.match(r'^[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?$', username) and
        '--' not in username
    )


def is_valid_github_repo_name(repo):
    """
    Validates a GitHub repository name based on length and allowed characters.
    """
    return (
        1 <= len(repo) <= 100 and
        re.match(r'^[a-zA-Z0-9._-]+$', repo)
    )


def parse_git_url(src, allow_plain_resources=None):
    """
    Parses various Git or GitHub-style URLs and paths into components.

    Supported formats:
    - https://host/user/repo.git         → https_git
    - https://host/user/repo             → https_plain (if allowed)
    - git@host:user/repo.git             → ssh_git
    - github:user/repo                   → github_short
    - user/repo                          → github_path (strict GitHub rules)
    - host/user/repo.git                 → domain_git
    - host/user/repo                     → domain_plain (if host allowed)

    Args:
        src: The Git URL or path string to parse.
        allow_plain_resources: Optional set of hostnames allowed for plain URLs without `.git`.

    Returns:
        ParsedGitURL instance with parsed components or None if the format is not recognized.
    """
    if allow_plain_resources is None:
        allow_plain_resources = {"github.com"}

    https_git_pattern = re.compile(r'^(https?)://([^/]+)/([^/]+)/([^/]+)\.git/?$')
    https_plain_pattern = re.compile(r'^(https?)://([^/]+)/([^/]+)/([^/]+)/?$')
    ssh_pattern = re.compile(r'^git@([^:]+):([^/]+)/([^/]+)\.git$')
    github_short_pattern = re.compile(r'^github:([^/]+)/([^/]+)$')
    github_path_pattern = re.compile(r'^([a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?)/([a-zA-Z0-9._-]{1,100})$')
    domain_git_pattern = re.compile(r'^([^/]+)/([^/]+)/([^/]+)\.git$')
    domain_plain_pattern = re.compile(r'^([^/]+)/([^/]+)/([^/]+)/?$')

    m = https_git_pattern.match(src)
    if m:
        scheme, resource, user, repo = m.groups()
        return ParsedGitURL("{}_git".format(scheme), resource, user, repo)

    m = https_plain_pattern.match(src)
    if m:
        scheme, resource, user, repo = m.groups()
        if resource in allow_plain_resources:
            return ParsedGitURL("{}_plain".format(scheme), resource, user, repo)

    m = ssh_pattern.match(src)
    if m:
        resource, user, repo = m.groups()
        return ParsedGitURL("ssh_git", resource, user, repo)

    m = github_short_pattern.match(src)
    if m:
        user, repo = m.groups()
        if is_valid_github_username(user) and is_valid_github_repo_name(repo):
            return ParsedGitURL("github_short", "github.com", user, repo)

    m = github_path_pattern.match(src)
    if m:
        user, repo = m.groups()
        if is_valid_github_username(user) and is_valid_github_repo_name(repo):
            return ParsedGitURL("github_path", "github.com", user, repo)

    m = domain_git_pattern.match(src)
    if m:
        resource, user, repo = m.groups()
        return ParsedGitURL("domain_git", resource, user, repo)

    m = domain_plain_pattern.match(src)
    if m:
        resource, user, repo = m.groups()
        if resource in allow_plain_resources:
            return ParsedGitURL("domain_plain", resource, user, repo)

    return None