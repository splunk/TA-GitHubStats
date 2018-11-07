import requests

# (FORKS) https://developer.github.com/v3/repos/#list-organization-repositories
GITHUB_REPOS_ENDPOINT = "https://api.github.com/orgs/{owner}/repos"
# (CLONES) https://developer.github.com/v3/repos/traffic/#clones
GITHUB_TRAFFIC_CLONES_ENDPOINT = ("https://api.github.com/repos/{owner}/"
                                  "{repo_name}/traffic/clones")
# (VIEWS) https://developer.github.com/v3/repos/traffic/#views
GITHUB_TRAFFIC_VIEWS_ENDPOINT = ("https://api.github.com/repos/{owner}/"
                                 "{repo_name}/traffic/views")
# (ASSET RELEASES) https://developer.github.com/v3/repos/releases/#list-releases-for-a-repository
GITHUB_RELEASES_ENDPOINT = ("https://api.github.com/repos/{owner}/"
                            "{repo_name}/releases")


def get_traffic_clone_endpoint(github_username, github_access_token, github_organization, repository_name):
    traffic_clones_response = requests.get(GITHUB_TRAFFIC_CLONES_ENDPOINT.format(owner=github_organization,
                                                                                 repo_name=repository_name),
                                           auth=(github_username, github_access_token))
    return traffic_clones_response.json()


def get_traffic_view_endpoint(github_username, github_access_token, github_organization, repository_name):
    traffic_views_response = requests.get(GITHUB_TRAFFIC_VIEWS_ENDPOINT.format(owner=github_organization,
                                                                               repo_name=repository_name),
                                          auth=(github_username, github_access_token))
    return traffic_views_response.json()


def get_releases_endpoint(github_username, github_access_token, github_organization, repository_name):
    releases_response = requests.get(GITHUB_RELEASES_ENDPOINT.format(owner=github_organization,
                                                                     repo_name=repository_name),
                                     auth=(github_username, github_access_token))
    return releases_response.json()
