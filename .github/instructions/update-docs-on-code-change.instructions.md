---
description: Automatically update documentation files when application code changes require documentation updates
applyTo: '**/*.{md,py,yml,yaml,json}'
---

# Update Documentation on Code Change

## Overview

Ensure documentation stays synchronized with code changes by detecting when README.md,
API documentation, configuration guides, and other docs need updates based on code
modifications.

## When to Update Documentation

Automatically check if documentation updates are needed when:

- New features or functionality are added
- API endpoints, methods, or interfaces change
- Breaking changes are introduced
- Dependencies or requirements change
- Configuration options or environment variables are modified
- Installation or setup procedures change
- Command-line interfaces or scripts are updated
- Code examples in documentation become outdated

## Documentation Update Rules

### README.md Updates

Always update README.md when:

- Adding new features: add to Features section, include usage examples
- Modifying installation/setup: update Getting Started and prerequisite lists
- Adding new CLI commands: document syntax, options, default values
- Changing configuration: update examples and document new environment variables

### API Documentation Updates

Sync API documentation when:

- New endpoints are added: document HTTP method, path, parameters, request/response examples
- Endpoint signatures change: update parameter lists, response schemas
- Authentication or authorization changes: update auth examples, security requirements

### Code Example Synchronization

Verify and update code examples when:

- Function signatures change: update all snippets, verify they compile/run
- API interfaces change: revise example requests/responses, client code examples
- Best practices evolve: replace outdated patterns, add deprecation notices

### Configuration Documentation

Update configuration docs when:

- New environment variables are added: add to `.env.example` and update the per-environment quick reference section at the bottom of the file
- Config file structure changes: update example files, document new options
- Deployment configuration changes: update Docker/Kubernetes configs, deployment guides
- Environment precedence changes: document compose/pydantic precedence and override behavior

## Best Practices

- Update documentation in the same commit as code changes
- Include before/after examples for changes
- Test code examples before committing
- Use consistent formatting and terminology
- Document limitations and edge cases
- Provide migration paths for breaking changes
- Keep documentation DRY (link instead of duplicating)

## Do NOT

- Commit code changes without updating documentation
- Leave outdated examples in documentation
- Document features that don't exist yet
- Use vague or ambiguous language
- Forget to update changelog
- Ignore broken links or failing examples

## Review Checklist

- [ ] README.md reflects current project state
- [ ] All new features are documented
- [ ] Code examples are tested and work
- [ ] API documentation is complete and accurate
- [ ] Configuration examples are up to date
- [ ] Breaking changes are documented with migration guide
- [ ] CHANGELOG.md is updated
- [ ] Links are valid and not broken
- [ ] Installation instructions are current
- [ ] Environment variables are documented
