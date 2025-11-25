import base64
import json
import os
from typing import Dict, Optional

import base58
import httpx
from solders.solders import Keypair, VersionedTransaction


class JupiterClient:
    """
    Base client for interacting with Jupiter API.
    Also acts as a parent class for all sub-clients.
    """

    def __init__(
        self,
        api_key: Optional[str],
        private_key_env_var: str,
        timeout: int,
    ):
        self.api_key = api_key
        self.base_url = (
            "https://api.jup.ag" if api_key else "https://lite-api.jup.ag"
        )
        self.private_key_env_var = private_key_env_var
        self.timeout = timeout
        self.client = httpx.Client(timeout=self.timeout)

    def close(self) -> None:
        self.client.close()

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    def _post_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    def _load_private_key_bytes(self) -> bytes:
        """Loads the private key from the environment
        variable as base58 or uint8 array."""
        pk_raw = os.getenv(self.private_key_env_var, "")
        pk_raw = pk_raw.strip()
        if pk_raw.startswith("[") and pk_raw.endswith("]"):
            try:
                arr = json.loads(pk_raw)
                if isinstance(arr, list) and all(
                    isinstance(x, int) and 0 <= x <= 255 for x in arr
                ):
                    return bytes(arr)
                else:
                    raise ValueError
            except Exception as e:
                raise ValueError(
                    f"Invalid uint8-array private key format: {e}"
                )
        try:
            return base58.b58decode(pk_raw)
        except Exception as e:
            raise ValueError(f"Invalid base58 private key format: {e}")

    def _get_public_key(self) -> str:
        wallet = Keypair.from_bytes(self._load_private_key_bytes())
        return str(wallet.pubkey())

    def _sign_base64_transaction(
        self, transaction_base64: str
    ) -> VersionedTransaction:
        transaction_bytes = base64.b64decode(transaction_base64)
        versioned_transaction = VersionedTransaction.from_bytes(
            transaction_bytes
        )
        return self._sign_versioned_transaction(versioned_transaction)

    def _sign_versioned_transaction(
        self, versioned_transaction: VersionedTransaction
    ) -> VersionedTransaction:
        wallet = Keypair.from_bytes(self._load_private_key_bytes())
        account_keys = versioned_transaction.message.account_keys
        wallet_index = account_keys.index(wallet.pubkey())

        signers = list(versioned_transaction.signatures)

        message_bytes = bytes(versioned_transaction.message)
        your_signature = wallet.sign_message(message_bytes)
        signers[wallet_index] = your_signature

        return VersionedTransaction.populate(
            versioned_transaction.message, signers
        )

    def _serialize_versioned_transaction(
        self, versioned_transaction: VersionedTransaction
    ) -> str:
        return base64.b64encode(bytes(versioned_transaction)).decode("utf-8")
