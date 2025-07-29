"""Tag transactions based on account."""

import ast
from typing import Any

from beancount.core.data import Entries, Transaction

__plugins__ = ["tag"]


def tag(entries: Entries, _, config_str: str) -> tuple[Entries, list[Any]]:
    """Tag transactions based on account.

    Args:
        entries: A list of beancount entries.
        config_str: A string containing the configuration for the plugin.

    Returns:
        A tuple of the modified entries and a list of errors.
    """
    config = ast.literal_eval(config_str)
    accounts = config.get("accounts", None)
    if not accounts:
        return entries, ["no accounts defined"]

    new_entries = entries[:]

    errors = []
    for acct, tag in accounts.items():
        print(f"Running tag for {acct}, tag {tag}")

        for transId, entry in enumerate(new_entries):
            if not isinstance(entry, Transaction):
                continue
            if all(post.account != acct for post in entry.postings):
                continue
            new_entries[transId] = entry._replace(tags=frozenset(set(entry.tags).union([tag])))

    return new_entries, errors
