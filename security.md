# Security Policy

## Temporary Dependency Risk Exception

The project currently uses:

- `presidio-anonymizer==2.2.363`
- `cryptography==46.0.7`

`pip-audit` reports `GHSA-537c-gmf6-5ccf` for `cryptography`.
The patched version is `48.0.1`, but the current Presidio Anonymizer
release requires `cryptography>=46.0.4,<47.0.0`.

Upgrading `cryptography` independently would therefore create an
unsupported and internally inconsistent dependency environment.

The advisory is temporarily ignored in CI while remaining documented
and visible in the workflow logs. This exception should be removed when
Presidio releases a compatible version supporting a patched
`cryptography` release.

This project is a portfolio demonstration and is not deployed as a
production service.