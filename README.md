# bedrock-safe-logging

This build creates a wrapper around customizable AWS Bedrock LLMs. The purpose of this build was to demonstrate features of safe logging for enterprise use cases. 

SSO into the AWS CLI to get started then run `make build` to build and run the image as a container in Docker.

## Features
- Safe Logging:
    - Choose to configure prompt logging
    - Trace id maintained across logs throughout lifetime of request
    - Sensitive PII such as credit card numbers, SSNs, email addresses, AWS keys, etc ... are automatically redacted from logs

- Integration & Unit Tests:
    - Automatic unit and integration tests
    - Run `make test` for unit testing
    - Run `make test-integration` for end to end integration test

 - Repository Secret Scanning:
   - Run `make scan` to conduct a repository-wide scan for hardcoded credentials
   - Discovered credentials in source code are cited with file name and line of incident
