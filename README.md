# Github Issue Adapter

AWS Lambda function that copies GitHub issues hourly into an Exasol table. 

## Deploy

This app is currently deployed int the `jb-dev` exasol AWS account.

You can deploy the app using the [AWS SAM CLI](https://aws.amazon.com/serverless/sam/):

```shell
sam build
sam deploy
```

## Usage

To analyze the issues you can use SQL. As a start take a look at the queries in [queries.sql](queries.sql). 