from __future__ import annotations

from cli.settings import settings
from cli.settings.core import ACTIVE_TOKEN_FILE_NAME
from cli.settings.migrate_token_file import InvalidTokenError, UnsupportedTokenVersionError, migrate_legacy_token
from cli.settings.token_file import TokenFile, dumps


def _migrate_legacy_tokens(tokens: list[TokenFile]) -> tuple[list[TokenFile], set[str]]:
    """
    Determine which tokens can be updated and which should be removed.

    Returns:
        tuple of (updated_tokens, invalid_tokens)
    """
    updated_tokens: list[TokenFile] = []
    invalid_tokens: set[str] = set()

    for token in tokens:
        try:
            migrated_token = migrate_legacy_token(token)
            if migrated_token.version != token.version:
                updated_tokens.append(migrated_token)
        except (InvalidTokenError, UnsupportedTokenVersionError):
            # Token not valid or unsupported version, mark for removal
            invalid_tokens.add(token.name)

    return updated_tokens, invalid_tokens


def _write_updated_tokens(updated_tokens: list[TokenFile]) -> None:
    for updated_token in updated_tokens:
        settings.remove_token_file(name=updated_token.name)
        if updated_token.type == "authorized_user":
            settings.add_personal_token(dumps(updated_token), overwrite_if_exists=True)
        elif updated_token.type == "service_account":
            settings.add_service_account_token(dumps(updated_token))
        else:
            raise ValueError(f"Unsupported token type: {updated_token.type}")


def _remove_invalid_tokens(invalid_tokens: set[str]) -> None:
    for token_name in invalid_tokens:
        settings.remove_token_file(name=token_name)


def _remove_old_secret_file() -> bool:
    old_activated_secret_file = settings.config_dir / ACTIVE_TOKEN_FILE_NAME
    old_secret_exists = old_activated_secret_file.exists()
    if old_secret_exists:
        old_activated_secret_file.unlink(missing_ok=True)
    return old_secret_exists


def migrate_any_legacy_tokens(tokens: list[TokenFile]) -> bool:
    """
    Migrate any legacy tokens to the latest TokenFile format.

    Returns True if any tokens were migrated, False otherwise.
    """
    # Get tokens to update/remove
    updated_tokens, invalid_tokens = _migrate_legacy_tokens(tokens)

    # Perform file operations
    _write_updated_tokens(updated_tokens)
    _remove_invalid_tokens(invalid_tokens)

    # Remove old secret file if exists
    old_secret_removed = _remove_old_secret_file()
    if old_secret_removed:
        return True  # We migrated at least one token

    # only return True if we migrated at least one token
    return len(updated_tokens) + len(invalid_tokens) > 0
