from typing import Any, Dict, Optional

from jup_python_sdk.clients.jupiter_client import JupiterClient
from jup_python_sdk.models.ultra_api.ultra_execute_request_model import (
    UltraExecuteRequest,
)
from jup_python_sdk.models.ultra_api.ultra_order_request_model import (
    UltraOrderRequest,
)


class UltraApiClient(JupiterClient):
    """
    A client for interacting with the Jupiter Ultra API.
    Inherits from JupiterClient.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        private_key_env_var: str = "PRIVATE_KEY",
        timeout: int = 10,
    ):
        super().__init__(
            api_key=api_key,
            private_key_env_var=private_key_env_var,
            timeout=timeout,
        )

    def order(self, request: UltraOrderRequest) -> Dict[str, Any]:
        """
        Get an order from the Jupiter Ultra API.

        Args:
            request (UltraOrderRequest): The request parameters for the order.

        Returns:
            dict: The dict api response.
        """
        params = request.to_dict()

        url = f"{self.base_url}/ultra/v1/order"
        response = self.client.get(
            url, params=params, headers=self._get_headers()
        )
        response.raise_for_status()

        return response.json()  # type: ignore

    def execute(self, request: UltraExecuteRequest) -> Dict[str, Any]:
        """
        Execute the order with the Jupiter Ultra API.

        Args:
            request (UltraExecuteRequest): The execute request parameters.

        Returns:
            dict: The dict api response.
        """
        payload = request.to_dict()

        url = f"{self.base_url}/ultra/v1/execute"
        response = self.client.post(
            url, json=payload, headers=self._get_headers()
        )
        response.raise_for_status()

        return response.json()  # type: ignore

    def order_and_execute(self, request: UltraOrderRequest) -> Dict[str, Any]:
        """
        Get an order from the Jupiter Ultra API and execute it immediately.

        Args:
            request (UltraOrderRequest): The request parameters for the order.

        Returns:
            dict: The dict api response.
        """
        order_response = self.order(request)

        request_id = order_response["requestId"]
        signed_transaction = self._sign_base64_transaction(
            order_response["transaction"]
        )

        execute_request = UltraExecuteRequest(
            request_id=request_id,
            signed_transaction=self._serialize_versioned_transaction(
                signed_transaction
            ),
        )

        return self.execute(execute_request)

    def balances(self, address: str) -> Dict[str, Any]:
        """
        Get token balances of an account from the Jupiter Ultra API.

        Args:
            address (str): The public key of the account to get balances for.

        Returns:
            dict: The dict api response.
        """
        url = f"{self.base_url}/ultra/v1/balances/{address}"
        response = self.client.get(url, headers=self._get_headers())
        response.raise_for_status()

        return response.json()  # type: ignore

    def holdings(self, address: str) -> Dict[str, Any]:
        """
        Get token holdings of an account from the Jupiter Ultra API.

        Args:
            address (str): The public key of the account to get holdings for.

        Returns:
            dict: The dict api response containing portfolio value and detailed
                  token account information organized by mint address.
        """
        url = f"{self.base_url}/ultra/v1/holdings/{address}"
        response = self.client.get(url, headers=self._get_headers())
        response.raise_for_status()

        return response.json()  # type: ignore

    def shield(self, mints: list[str]) -> Dict[str, Any]:
        """
        Get token information and warnings for specific mints
        from the Jupiter Ultra API.

        Args:
            mints (list[str]): List of token mint addresses
            to get information for.

        Returns:
            dict: The dict api response with warnings information.
        """
        params = {"mints": ",".join(mints)}

        url = f"{self.base_url}/ultra/v1/shield"
        response = self.client.get(
            url, params=params, headers=self._get_headers()
        )
        response.raise_for_status()

        return response.json()  # type: ignore
