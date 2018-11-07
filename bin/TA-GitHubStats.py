# Python Standard Libraries
import json
import logging
import sys
# Third-Party Libraries
import requests
# Splunk Provided Libraries
from splunklib import six
from splunklib.modularinput import Argument
from splunklib.modularinput import Event
from splunklib.modularinput import Script
from splunklib.modularinput import Scheme
# Custom Libraries
from scrape_stats import GITHUB_REPOS_ENDPOINT
from scrape_stats import get_releases_endpoint
from scrape_stats import get_traffic_clone_endpoint
from scrape_stats import get_traffic_view_endpoint


SPLUNK_APP_NAME = "TA-GitHubStats"


logging.root
logging.root.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.root.addHandler(handler)


class MyScript(Script):

    def get_scheme(self):
        """Generates the scheme of the modular input.

        Returns:
            (Scheme): The Splunk Python SDK Scheme object.
                https://github.com/splunk/splunk-sdk-python/blob/master/splunklib/modularinput/scheme.py
        """
        scheme = Scheme("GitHub Stats")
        scheme.description = "Get interesting statistics from GitHub for an organization."
        scheme.use_external_validation = True
        scheme.use_single_instance = True
        # ----------------------------------------------------------------------
        github_username_argument = Argument("github_username")
        github_username_argument.data_type = Argument.data_type_string
        github_username_argument.description = ("The username used to "
                                                "authenticate with GitHub.")
        github_username_argument.required_on_create = True
        # ----------------------------------------------------------------------
        github_access_token_argument = Argument("github_access_token")
        github_access_token_argument.data_type = Argument.data_type_string
        github_access_token_argument.description = ("The access token used to"
                                                    " authenticate with GitHub."
                                                    " Used in place of a"
                                                    " password.")
        github_access_token_argument.required_on_create = True
        # ----------------------------------------------------------------------
        github_organization_argument = Argument("github_organization")
        github_organization_argument.data_type = Argument.data_type_string
        github_organization_argument.description = ("The GitHub organization to"
                                                    " use for scraping stats.")
        github_organization_argument.required_on_create = True
        # ----------------------------------------------------------------------
        scheme.add_argument(github_username_argument)
        scheme.add_argument(github_access_token_argument)
        scheme.add_argument(github_organization_argument)

        return scheme

    def validate_input(self, validation_definition):
        github_username = validation_definition.parameters["github_username"]
        github_access_token = validation_definition.parameters["github_access_token"]
        github_organization = validation_definition.parameters["github_organization"]

        repos_response = requests.get(GITHUB_REPOS_ENDPOINT.format(owner=github_organization),
                                      auth=(github_username, github_access_token))

        if repos_response.status_code != 200:
            raise ValueError(("The information provided for the {} Splunk App"
                              " was invalid."
                              " Username: {}"
                              " Access Token: **********"
                              " Organization: {}"
                              " HTTP Code: {}"
                              " HTTP Status: {}").format(SPLUNK_APP_NAME,
                                                         github_username,
                                                         github_organization,
                                                         repos_response.status_code,
                                                         repos_response.reason))

    def stream_events(self, input_definition, event_writer):
        for input_name, input_item in six.iteritems(input_definition.inputs):

            github_username = input_item["github_username"]
            github_access_token = input_item["github_access_token"]
            github_organization = input_item["github_organization"]

            generate_repo_stats = True
            github_repos_url = GITHUB_REPOS_ENDPOINT.format(owner=github_organization)

            while generate_repo_stats:
                repos_response = requests.get(github_repos_url,
                                              auth=(github_username, github_access_token))
                for repository in repos_response.json():
                    repository_name = repository["name"]
                    repository_id = repository["id"]

                    # FORKS
                    event = Event()
                    event.stanza = input_name
                    event.data = ("github_organization={github_organization}"
                                  " repository_name={repository_name}"
                                  " repository_id={repository_id}"
                                  " endpoint=repository"
                                  " data={response_data}"
                                  ).format(
                        github_organization=github_organization,
                        repository_name=repository_name,
                        repository_id=repository_id,
                        response_data=json.dumps(repository),
                    )
                    event_writer.write_event(event)
                    # CLONES
                    traffic_clones_response = get_traffic_clone_endpoint(github_username,
                                                                         github_access_token,
                                                                         github_organization,
                                                                         repository_name)
                    event = Event()
                    event.stanza = input_name
                    event.data = ("github_organization={github_organization}"
                                  " repository_name={repository_name}"
                                  " repository_id={repository_id}"
                                  " endpoint=traffic/clones"
                                  " data={response_data}"
                                  ).format(
                        github_organization=github_organization,
                        repository_name=repository_name,
                        repository_id=repository_id,
                        response_data=json.dumps(traffic_clones_response),
                    )
                    event_writer.write_event(event)
                    # VIEWS
                    traffic_views_response = get_traffic_view_endpoint(github_username,
                                                                       github_access_token,
                                                                       github_organization,
                                                                       repository_name)
                    event = Event()
                    event.stanza = input_name
                    event.data = ("github_organization={github_organization}"
                                  " repository_name={repository_name}"
                                  " repository_id={repository_id}"
                                  " endpoint=traffic/views"
                                  " data={response_data}"
                                  ).format(
                        github_organization=github_organization,
                        repository_name=repository_name,
                        repository_id=repository_id,
                        response_data=json.dumps(traffic_views_response),
                    )
                    event_writer.write_event(event)
                    # RELEASES
                    releases_response = get_releases_endpoint(github_username,
                                                              github_access_token,
                                                              github_organization,
                                                              repository_name)
                    event = Event()
                    event.stanza = input_name
                    event.data = ("github_organization={github_organization}"
                                  " repository_name={repository_name}"
                                  " repository_id={repository_id}"
                                  " endpoint=releases"
                                  " data={response_data}"
                                  ).format(
                        github_organization=github_organization,
                        repository_name=repository_name,
                        repository_id=repository_id,
                        response_data=json.dumps(releases_response),
                    )
                    event_writer.write_event(event)

                if "next" in repos_response.links:
                    github_repos_url = repos_response.links["next"]["url"]
                else:
                    generate_repo_stats = False


if __name__ == "__main__":
    sys.exit(MyScript().run(sys.argv))
