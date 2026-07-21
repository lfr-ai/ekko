# Ekko Platform Specification

## Purpose

Define foundational behavior expectations for Ekko as a local-first AI-assisted
voice platform.

## Requirements

### Requirement: Local development runtime availability

The system MUST expose a local backend runtime and a local frontend runtime for
interactive development.

#### Scenario: Backend and frontend are reachable locally

- GIVEN the developer has started the project in development mode
- WHEN the developer opens the configured local backend URL and frontend URL
- THEN both runtimes respond successfully
- AND local development work can proceed without cloud dependencies

### Requirement: PII protection before model calls

The system MUST scrub configured sensitive patterns before outbound LLM calls.

#### Scenario: Sensitive content is anonymized in outbound request content

- GIVEN an input containing configured PII patterns
- WHEN the input is processed for model interaction
- THEN matched sensitive values are anonymized
- AND outbound model content does not contain raw matched PII values

### Requirement: Health visibility for backend runtime

The system MUST provide a health endpoint suitable for local service checks.

#### Scenario: Health endpoint reports service availability

- GIVEN the backend runtime is started
- WHEN a request is made to the health endpoint
- THEN the endpoint returns a successful status
- AND operators can confirm service availability for local diagnostics
