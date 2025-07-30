from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass
from json import JSONDecodeError
from typing import Any, Dict, Optional

from dacite import from_dict

from cli.settings.token_file import TokenFile


def upgrade_config(config: dict[str, Any]) -> Optional[dict[str, Any]]:
    """
    Reads a JSON config from in_path, replaces each account's 'credentials_name'
    with 'credentials_file' (by calling get_filename_for_name), and writes the result
    back to out_path (or overwrites in_path if out_path is None).
    """
    from cli.settings import TokenNotFoundError, settings

    accounts = config.get("accounts", {})
    to_delete = []
    found_old = False
    for account, info in list(accounts.items()):
        cred_name = info.pop("credentials_name", None)
        if not cred_name:
            continue
        found_old = True
        try:
            cred_file = settings.get_token_file(cred_name).get_token_file_name()
        except TokenNotFoundError:
            # schedule this account for removal
            to_delete.append(account)
            print(f"Dropping account {account!r}: token file for {cred_name} not found")
            continue

        info["credentials_file"] = cred_file

    # actually remove them
    for account in to_delete:
        del accounts[account]

    if found_old:
        return config
    return None


def _from_dict(data: dict[str, Any]) -> ConfigFile:
    from cli.settings import settings

    config = upgrade_config(data)
    if config is not None:
        print("Migrating old configuration format")
        updated_config: ConfigFile = from_dict(ConfigFile, config)
        settings.write_config_file(updated_config)
        return updated_config
    return from_dict(ConfigFile, data)


def loads(data: str) -> ConfigFile:
    try:
        d = json.loads(data)
        return _from_dict(d)
    except JSONDecodeError as e:
        # ErrorPrinter.print_generic_error("Invalid json format, config.json")
        raise JSONDecodeError(
            f"File config.json is not valid json, please edit or remove file to have it re-created ({e.msg})", pos=e.pos, doc=e.doc
        )


def dumps(config: ConfigFile) -> str:
    return json.dumps(dataclasses.asdict(config), default=str)


@dataclass
class Account:
    credentials_file: str
    default_organization: Optional[str] = None
    # Add project as well


@dataclass
class ConfigFile:
    version: str = "1.0"
    active: Optional[str] = None
    accounts: Dict[str, Account] = dataclasses.field(default_factory=dict)

    def get_active_default_organisation(self) -> Optional[str]:
        active_account = self.get_active()
        return active_account.default_organization if active_account is not None else None

    def get_active(self) -> Optional[Account]:
        if self.active is not None:
            account = self.accounts.get(self.active)
            if account is not None:
                return account
            raise KeyError(f"Activated account {self.active} is not a valid account")
        return None

    def activate(self, email: str) -> None:
        account = self.accounts.get(email)

        if account is not None:
            self.active = email
        else:
            raise KeyError(f"Account {email} does not exists")

    def get_account(self, email: str) -> Optional[Account]:
        if self.accounts:
            return self.accounts[email]
        return None

    def remove_account(self, email: str) -> None:
        if self.accounts:
            self.accounts.pop(email, None)

    def init_account(self, email: str, token_file: TokenFile) -> None:
        if self.accounts is None:
            self.accounts = {}

        account = self.accounts.get(email)
        if not account:
            account = Account(credentials_file=token_file.get_token_file_name())
        else:
            account.credentials_file = token_file.get_token_file_name()
        self.accounts[email] = account

    def set_account_field(self, email: str, default_organization: Optional[str] = None) -> ConfigFile:
        if self.accounts is None:
            self.accounts = {}

        account = self.accounts.get(email)
        if not account:
            raise KeyError(f"Account with email {email} has not been initialized with token")

        # Update only fields explicitly passed
        if default_organization is not None:
            account.default_organization = default_organization

        return self
