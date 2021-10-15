import os.path

import yaml

TEST_CONFIG_FILE_NAME = "test-config.yml"

GITHUB_TOKEN_PROPERTY = "github_token"


class TestConfig:
    def __init__(self, github_token: str):
        self._github_token = github_token

    def github_token(self) -> str:
        return self._github_token


def read_test_config() -> TestConfig:
    try:
        with open(os.path.dirname(__file__) + "/../../" + TEST_CONFIG_FILE_NAME, "r") as stream:
            parsed = yaml.safe_load(stream)
            if GITHUB_TOKEN_PROPERTY not in parsed:
                raise Exception(
                    "Missing required property '" + GITHUB_TOKEN_PROPERTY + "' in './" + TEST_CONFIG_FILE_NAME + "'. " +
                    "Please set the property to your github-access token.")
            return TestConfig(parsed[GITHUB_TOKEN_PROPERTY])
    except FileNotFoundError:
        raise Exception("Could not find required test config './" + TEST_CONFIG_FILE_NAME + "'. "
                                                                                            "Please create that file in the project directory and add 'github_token: <YOUR TOKEN>'.")
