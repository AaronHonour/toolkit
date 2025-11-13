"""Password hashing utilities."""

import hashlib
import secrets


class PasswordHasher:
    """Password hashing with salt.

    Examples:
        >>> hasher = PasswordHasher()
        >>> hashed = hasher.hash("my-password")
        >>> hasher.verify("my-password", hashed)
        True
    """

    def __init__(self, algorithm: str = "sha256", salt_length: int = 32) -> None:
        """Initialize PasswordHasher.

        Args:
            algorithm: Hashing algorithm (default: sha256)
            salt_length: Length of salt in bytes
        """
        self.algorithm = algorithm
        self.salt_length = salt_length

    def hash(self, password: str) -> str:
        """Hash password with salt.

        Args:
            password: Plain text password

        Returns:
            Hashed password with salt
        """
        salt = secrets.token_hex(self.salt_length)
        pwd_hash = self._hash_with_salt(password, salt)
        return f"{salt}${pwd_hash}"

    def verify(self, password: str, hashed: str) -> bool:
        """Verify password against hash.

        Args:
            password: Plain text password
            hashed: Hashed password

        Returns:
            True if password matches
        """
        try:
            salt, pwd_hash = hashed.split("$")
            return self._hash_with_salt(password, salt) == pwd_hash
        except ValueError:
            return False

    def _hash_with_salt(self, password: str, salt: str) -> str:
        """Hash password with given salt."""
        h = hashlib.new(self.algorithm)
        h.update((password + salt).encode())
        return h.hexdigest()
