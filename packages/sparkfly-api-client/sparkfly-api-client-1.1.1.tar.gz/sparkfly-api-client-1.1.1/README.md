# Sparkfly API Client

A Python client library for the Sparkfly Platform API.

## Installation

```bash
pip install sparkfly-api-client
```

## Quick Start

```python
from sparkfly import Sparkfly

# Initialize the client with your credentials
client = Sparkfly(
    identity="your-account-identity",
    key="your-secret-key"
)

# The client automatically handles authentication
# You can now use any of the API endpoints

# Get campaigns
campaigns = client.campaigns.get_campaigns()

# Get stores
stores = client.stores.get_stores()

# Create an offer
from openapi_client.models import OfferRequest, OfferRequestOffer

offer_data = OfferRequestOffer(
    name="Test Offer",
    description="A test offer",
    # ... other fields
)
offer_request = OfferRequest(offer=offer_data)
new_offer = client.offers.post_offer(offer_request)
```

## Authentication

The client automatically handles authentication for you. When you create a client instance, it will:

1. Use your identity and key to authenticate with the `/auth` endpoint
2. Store the authentication token
3. Automatically include the token in all subsequent API calls
4. Refresh the token when it expires (tokens are valid for 24 hours)

## Available API Endpoints

The client provides access to all Sparkfly API endpoints:

- **Authentication**: `client.auth`
- **Campaigns**: `client.campaigns`
- **Stores**: `client.stores`
- **Offers**: `client.offers`
- **Offer States**: `client.offer_states`
- **Members**: `client.members`
- **Items**: `client.items` (includes item sets functionality)
- **Offer Lists**: `client.offer_lists`
- **Impressions**: `client.impressions`
- **Email Opt-in**: `client.email_opt_in`
- **Templates**: `client.templates`
- **Audiences**: `client.audiences`
- **BI Store Lists**: `client.bi_store_lists`
- **CTM**: `client.ctm`
- **Eligible Item Sets**: `client.eligible_item_sets`
- **Member Privacy**: `client.member_privacy`
- **Offer POS Offer Codes**: `client.offer_pos_offer_codes`
- **POS Offer Codes**: `client.pos_offer_codes`
- **Store Lists**: `client.store_lists`

## Examples

### Working with Campaigns

```python
# Get all campaigns
campaigns = client.campaigns.get_campaigns()

# Get a specific campaign
campaign = client.campaigns.get_campaign(campaign_id="123")

# Create a new campaign
from openapi_client.models import CampaignRequest, CampaignRequestCampaign

campaign_data = CampaignRequestCampaign(
    name="Summer Sale",
    description="Summer sale campaign",
    # ... other fields
)
campaign_request = CampaignRequest(campaign=campaign_data)
new_campaign = client.campaigns.post_campaign(campaign_request)
```

### Working with Stores

```python
# Get all stores
stores = client.stores.get_stores()

# Get a specific store
store = client.stores.get_store(store_id="456")

# Create a new store
from openapi_client.models import StoreRequest, StoreRequestStore

store_data = StoreRequestStore(
    name="Downtown Location",
    number="001",
    # ... other fields
)
store_request = StoreRequest(store=store_data)
new_store = client.stores.post_store(store_request)
```

### Working with Offers

```python
# Get all offers
offers = client.offers.get_offers()

# Get a specific offer
offer = client.offers.get_offer(offer_id="789")

# Create a new offer
from openapi_client.models import OfferRequest, OfferRequestOffer

offer_data = OfferRequestOffer(
    name="20% Off",
    description="20% off all items",
    # ... other fields
)
offer_request = OfferRequest(offer=offer_data)
new_offer = client.offers.post_offer(offer_request)
```

### Working with Items and Item Sets

```python
# Get all items
items = client.items.get_items()

# Get all item sets
item_sets = client.items.get_item_sets()

# Get a specific item set
item_set = client.items.get_item_sets_item_set_id(item_set_id="123")

# Create a new item set
from openapi_client.models import ItemSetRequest, ItemSetRequestItemSet

item_set_data = ItemSetRequestItemSet(
    name="Summer Collection",
    description="Items for summer season",
    # ... other fields
)
item_set_request = ItemSetRequest(item_set=item_set_data)
new_item_set = client.items.post_item_sets(item_set_request)

# Add an item to an item set
client.items.post_item_sets_item_set_id_items_id(item_set_id="123", id="456")

# Get items in an item set
items_in_set = client.items.get_item_sets_item_set_id_items(item_set_id="123")
```

## Configuration

You can customize the client configuration:

```python
client = Sparkfly(
    identity="your-account-identity",
    key="your-secret-key",
    host="https://api.sparkfly.com/v1.0"  # Use production instead of staging
)
```

## Error Handling

The client will raise exceptions for API errors:

```python
try:
    campaign = client.campaigns.get_campaign(campaign_id="invalid-id")
except Exception as e:
    print(f"Error: {e}")
```

## Token Management

The client automatically manages authentication tokens, but you can also work with them manually:

```python
# Check if token is valid
if client.is_token_valid():
    print("Token is still valid")

# Get current token
token = client.token

# Force re-authentication
new_token = client.authenticate()
```

## Development

This client is generated from the Sparkfly OpenAPI specification and provides a type-safe interface to all API endpoints. The underlying OpenAPI client handles all the HTTP communication, serialization, and authentication details.


