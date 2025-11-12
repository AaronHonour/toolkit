"""JWT token handling."""

import json
import time
from typing import Any


class JWT:
    """
    JWT token encoder/decoder.

    Examples:
        >>> jwt = JWT(secret="my-secret")
        >>> token = jwt.encode({"user_id": 123})
        >>> claims = jwt.decode(token)
    """

    def __init__(self, secret: str, algorithm: str = "HS256", expiration: int = 3600):
        self.secret = secret
        self.algorithm = algorithm
        self.expiration = expiration

    def encode(self, payload: dict[str, Any], exp: int | None = None) -> str:
        """
        Encode payload to JWT token.

        Args:
            payload: Data to encode
            exp: Expiration time (seconds from now)

        Returns:
            JWT token string
        """
        import base64
        import hashlib
        import hmac

        # Add expiration
        if exp is None:
            exp = self.expiration

        payload = dict(payload)
        payload["exp"] = int(time.time()) + exp
        payload["iat"] = int(time.time())

        # Create header
        header = {"alg": self.algorithm, "typ": "JWT"}

        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")

        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self.secret.encode(), message.encode(), hashlib.sha256
        ).digest()
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")

        return f"{message}.{signature_b64}"

    def decode(self, token: str, verify: bool = True) -> dict[str, Any]:
        """
        Decode JWT token.

        Args:
            token: JWT token string
            verify: Whether to verify signature

        Returns:
            Decoded payload

        Raises:
            ValueError: If token is invalid or expired
        """
        import base64
        import hashlib
        import hmac

        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token format")

        header_b64, payload_b64, signature_b64 = parts

        # Verify signature
        if verify:
            message = f"{header_b64}.{payload_b64}"
            expected_signature = hmac.new(
                self.secret.encode(), message.encode(), hashlib.sha256
            ).digest()
            expected_signature_b64 = (
                base64.urlsafe_b64encode(expected_signature).decode().rstrip("=")
            )

            if signature_b64 != expected_signature_b64:
                raise ValueError("Invalid signature")

        # Decode payload
        payload_json = base64.urlsafe_b64decode(payload_b64 + "=" * (4 - len(payload_b64) % 4))
        payload = json.loads(payload_json)

        # Check expiration
        if "exp" in payload and payload["exp"] < time.time():
            raise ValueError("Token expired")

        return payload
