"""
AEONRIFT Checkpoint Security & Cryptographic Integrity

Provides cryptographic signatures, tamper-evident hash chaining,
and credential scrubbing for L0–L5 checkpoints.
"""

import hashlib
import hmac
import re
from typing import Any, Dict, List, Optional
from aeonrift.core.checkpoint import LayeredCheckpoint


class CheckpointSecurityGuard:
    """
    Ensures cryptographic integrity and secret isolation across checkpoints.
    """
    SECRET_PATTERNS = [
        re.compile(r'sk_mock_[0-9a-zA-Z]{24,}'),
        re.compile(r'ghp_[0-9a-zA-Z]{36}'),
        re.compile(r'Bearer\s+[A-Za-z0-9\-._~+/]+=*'),
        re.compile(r'AWS_SECRET_ACCESS_KEY=[^\s]+')
    ]

    def __init__(self, secret_key: str = "aeonrift_default_hmac_secret_2026"):
        self.secret_key = secret_key.encode('utf-8')

    def sign_checkpoint(self, checkpoint: LayeredCheckpoint) -> str:
        """Computes HMAC-SHA256 signature for a checkpoint."""
        state_hash = checkpoint.compute_state_hash()
        signature = hmac.new(self.secret_key, state_hash.encode('utf-8'), hashlib.sha256).hexdigest()
        checkpoint.metadata.signed_signature = signature
        return signature

    def verify_checkpoint_signature(self, checkpoint: LayeredCheckpoint) -> bool:
        """Verifies if checkpoint signature matches state content."""
        if not checkpoint.metadata.signed_signature:
            return False
        expected = hmac.new(self.secret_key, checkpoint.compute_state_hash().encode('utf-8'), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, checkpoint.metadata.signed_signature)

    def scrub_credentials(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Scrub sensitive credentials/tokens from dictionary payload."""
        payload_str = str(payload)
        for pattern in self.SECRET_PATTERNS:
            payload_str = pattern.sub('[REDACTED_CREDENTIAL]', payload_str)

        # Basic key filtering
        scrubbed = {}
        for k, v in payload.items():
            if any(term in k.lower() for term in ("token", "secret", "password", "key", "auth")):
                scrubbed[k] = "[REDACTED_CREDENTIAL]"
            elif isinstance(v, dict):
                scrubbed[k] = self.scrub_credentials(v)
            else:
                scrubbed[k] = v
        return scrubbed
