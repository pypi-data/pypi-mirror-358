from typing import Any, Dict, Optional

import pydo
from rich.console import Console

console = Console()

# TODO: change this to DO manager


class DOClient:
    """Wrapper for DigitalOcean API client."""

    def __init__(self, token: str):
        self.token = token
        self.client = pydo.Client(token=token)

    def validate_token(self) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate the API token and return account info.

        Returns:
            (success, account_info) - success is True if token is valid
        """
        try:
            account = self.client.account.get()
            return True, account
        except Exception:
            return False, None

    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Get account information."""
        try:
            return self.client.account.get()
        except Exception as e:
            console.print(f"[red]Error fetching account info: {e}[/red]")
            return None

    def get_balance(self) -> Optional[Dict[str, Any]]:
        """Get account balance."""
        try:
            return self.client.balance.get()
        except Exception as e:
            console.print(f"[red]Error fetching balance: {e}[/red]")
            return None
