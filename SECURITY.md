# Security Policy

## Reporting Security Vulnerabilities

AEONRIFT handles agent process state, credentials, side-effect ledgers, and filesystem checkpoints. Security is paramount.

If you discover a security vulnerability (such as state forgery, credential leakage in checkpoints, or semantic rollback bypasses), please **DO NOT** open a public issue.

Instead, please report vulnerabilities directly to the maintainers at `security@aeonrift.org` or open a Private Security Advisory on GitHub.

## Security Architecture Highlights
- **Checkpoint Cryptographic Signatures**: All L0–L5 checkpoints are signed using HMAC-SHA256 / Ed25519 to prevent tampering.
- **Credential Masking**: Runtime state scrubbers eliminate API tokens and OAuth secrets from event logs before persistence.
- **Semantic Rollback Protection**: Prevents restored checkpoints from silently re-triggering non-idempotent side effects.
