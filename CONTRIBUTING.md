# Contributing

Please open an issue before a large change. Keep source-dataset adapters isolated, preserve the
canonical factor order, and add tests for behavior changes. Never commit third-party media, model
weights, credentials, live-service responses, personal paths, or private annotations.

Run `python -m unittest discover -s tests -v` and validate any changed manifest before proposing a
pull request. Security or privacy-sensitive reports should use the private reporting mechanism
configured by the repository owner rather than a public issue.
