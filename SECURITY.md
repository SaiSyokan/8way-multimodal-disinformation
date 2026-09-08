# Security policy

Do not report exposed credentials or private dataset records in a public issue. Use the repository's
private security-advisory channel after the owner enables it. Revoke any exposed service credential
immediately and remove it from the complete Git history, not only the latest commit.

The evidence collectors read credentials from environment-supported mechanisms. Never commit `.env`
files, Google service-account JSON, downloaded page archives, or private evidence snapshots.
