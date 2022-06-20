# Github Issue Adapter

AWS Lambda function that copies GitHub issues hourly into an Exasol table. 

## Deploy

This app is currently deployed int the `exa-aws-pin-dev` exasol AWS account.

You can deploy the app using the [AWS SAM CLI](https://aws.amazon.com/serverless/sam/):

```shell
sam build
sam deploy
```

## Usage

To analyze the issues you can use SQL. As a start take a look at the queries in [queries.sql](queries.sql).

## Development

Install dependencies:

```shell
pip3 install -r github_issue_adapter/requirements.txt
pip3 install -r github_issue_adapter/test_requirements.txt
```

This will install `pytest` to `$HOME/.local/bin`. You might need to add this to the `PATH`:

```shell
export PATH="$HOME/.local/bin:$PATH"
```

Create file `test-config.yml` with your personal GitHub access token:

```yaml
github_token: ghp_...
```

Run tests with

```shell
pytest -v --cov --cov-report=xml --cov-report=html
````
