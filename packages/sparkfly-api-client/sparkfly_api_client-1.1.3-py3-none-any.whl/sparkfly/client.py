"""
Sparkfly API Client

A simplified wrapper around the generated OpenAPI client.
"""

import time
from typing import Optional, Dict, Any
from openapi_client import ApiClient, Configuration
from openapi_client.api import (
    AuthenticationApi,
    CampaignsApi,
    StoresApi,
    OffersApi,
    OfferStatesApi,
    MembersApi,
    ItemsApi,
    OfferListsApi,
    ImpressionsApi,
    EmailOptInApi,
    TemplatesApi,
    AudiencesApi,
    BIStoreListsApi,
    CtmApi,
    EligibleItemSetsApi,
    MemberPrivacyApi,
    OfferPOSOfferCodesApi,
    POSOfferCodesApi,
    StoreListsApi,
)


class Sparkfly:
    """
    A simplified client for the Sparkfly Platform API.

    This client handles authentication automatically and provides
    easy access to all API endpoints.
    """

    def __init__(
        self,
        identity: str,
        key: str,
        environment: str = "staging",
        host: Optional[str] = None,
        token: Optional[str] = None,
        token_expires_at: Optional[float] = None,
    ):
        """
        Initialize the Sparkfly client.

        Args:
            identity: Your Sparkfly account identity
            key: Your Sparkfly account secret key
            environment: The environment to use ('staging' or 'production')
            host: Optional custom host URL (overrides environment).
                 Must be one of the valid Sparkfly base URLs:
                 - https://api-staging.sparkfly.com (staging)
                 - https://api.sparkfly.com (production)
                 The /v1.0 suffix will be added automatically
            token: Optional pre-existing auth token
            token_expires_at: Optional token expiration timestamp
        """
        self.identity = identity
        self.key = key
        self.environment = environment

        # Determine the host URL
        if host:
            # Validate that the host is one of the valid base URLs
            valid_base_hosts = [
                "https://api-staging.sparkfly.com",
                "https://api.sparkfly.com",
            ]
            if host not in valid_base_hosts:
                raise ValueError(
                    f"Invalid host URL. Must be one of: {', '.join(valid_base_hosts)}"
                )

            # Always append /v1.0 to the base URL
            self.host = f"{host}/v1.0"
        elif environment.lower() == "production":
            self.host = "https://api.sparkfly.com/v1.0"
        elif environment.lower() == "staging":
            self.host = "https://api-staging.sparkfly.com/v1.0"
        else:
            raise ValueError("Environment must be 'staging' or 'production'")

        self._token = token
        self._token_expires_at = token_expires_at

        # Initialize the API client
        self._config = Configuration(
            host=self.host,
            api_key={
                "XAuthIdentity": identity,
                "XAuthKey": key,
            },
        )
        self._api_client = ApiClient(configuration=self._config)

        # Initialize API classes
        self.auth = AuthenticationApi(self._api_client)
        self.campaigns = CampaignsApi(self._api_client)
        self.stores = StoresApi(self._api_client)
        self.offers = OffersApi(self._api_client)
        self.offer_states = OfferStatesApi(self._api_client)
        self.members = MembersApi(self._api_client)
        self.items = ItemsApi(self._api_client)  # Includes item sets functionality
        self.offer_lists = OfferListsApi(self._api_client)
        self.impressions = ImpressionsApi(self._api_client)
        self.email_opt_in = EmailOptInApi(self._api_client)
        self.templates = TemplatesApi(self._api_client)
        self.audiences = AudiencesApi(self._api_client)
        self.bi_store_lists = BIStoreListsApi(self._api_client)
        self.ctm = CtmApi(self._api_client)
        self.eligible_item_sets = EligibleItemSetsApi(self._api_client)
        self.member_privacy = MemberPrivacyApi(self._api_client)
        self.offer_pos_offer_codes = OfferPOSOfferCodesApi(self._api_client)
        self.pos_offer_codes = POSOfferCodesApi(self._api_client)
        self.store_lists = StoreListsApi(self._api_client)

    @property
    def token(self) -> Optional[str]:
        """Get the current authentication token."""
        return self._token

    @property
    def token_expires_at(self) -> Optional[float]:
        """Get the token expiration timestamp."""
        return self._token_expires_at

    def is_token_valid(self) -> bool:
        """Check if the current token is still valid."""
        if not self._token or not self._token_expires_at:
            return False
        return time.time() < self._token_expires_at

    def authenticate(self) -> str:
        """
        Authenticate with the Sparkfly API and get a token.

        Returns:
            The authentication token

        Raises:
            Exception: If authentication fails
        """
        try:
            # Request authentication token
            response = self.auth.post_auth_with_http_info()

            # Extract the token from the response headers
            if hasattr(response, "headers") and "X-Auth-Token" in response.headers:
                self._token = response.headers["X-Auth-Token"]
            else:
                # Fallback: check if the token is in the API client configuration
                self._token = self._config.api_key.get("XAuthToken")

            if not self._token:
                raise Exception("No authentication token received from the API")

            # Set token expiration to 24 hours from now
            self._token_expires_at = time.time() + (24 * 60 * 60)  # 24 hours

            # Update the API client configuration with the token
            self._config.api_key["XAuthToken"] = self._token

            return self._token

        except Exception as e:
            raise Exception(f"Authentication failed: {e}")

    def ensure_authenticated(self) -> str:
        """
        Ensure we have a valid authentication token.

        Returns:
            The authentication token
        """
        if not self.is_token_valid():
            return self.authenticate()
        return self._token

    def call_api(self, api_method, *args, **kwargs):
        """
        Call an API method with automatic authentication.

        Args:
            api_method: The API method to call
            *args: Arguments to pass to the method
            **kwargs: Keyword arguments to pass to the method

        Returns:
            The API response
        """
        # Ensure we're authenticated
        self.ensure_authenticated()

        # Call the API method
        return api_method(*args, **kwargs)
