# Proposed project/application names

Shortlist of modern, concise names for the voice-bot project. Pick one and we can perform an automated rename across the repo.

- vox — short, memorable, speaks to "voice"; package name: `vox`
- voxai — explicitly AI-powered voice assistant; package name: `voxai`
- voxb — abbreviation of "voice-bot"; package name: `voxb`
- vce — "voice conversational engine" (abbrev); package name: `vce`

Recommended next steps to rename package to `vox` (example):

1. Update `pyproject.toml` name to `vox`.
2. Rename package folder `src/voice` -> `src/vox` and update imports (a repository-wide search/replace: `from voice.` -> `from vox.`).
3. Update Dockerfile, Makefile, and CI workflows to reference the new package name.
4. Run tests and static checks; fix import paths as needed.
