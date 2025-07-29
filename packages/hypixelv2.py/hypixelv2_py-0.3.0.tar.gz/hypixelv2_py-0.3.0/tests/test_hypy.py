import pytest_asyncio
import pytest
from respx import MockRouter

from hypy import (
    HypyAsync,
    HypixelAPIError,
    HypixelRequestError,
    HypixelHTTPError,
    HypixelRateLimitError,
    HypixelForbiddenError,
    HypixelNotFoundError,
    HypixelValidationError,
    HypixelInvalidResponseError,
    HypixelUnprocessableEntityError
)

from hypy.modals import (
    BazaarResponse,
    ProfileResponse,
    ProfilesResponse,
    MuseumResponse,
    GardenResponse,
    BingoDataResponse,
    FireSalesResponse,
    CollectionsResponse,
    SkillsResponse,
    ItemsResponse,
    ElectionsResponse,
    BingoResponse,
    NewsResponse,
    RequestAuctionsResponse,
    ActiveAuctionsResponse,
    RecentlyEndedAuctionsResponse
)

URL = "https://api.hypixel.net/v2/"

@pytest_asyncio.fixture
async def api_client():
    client = HypyAsync(api_key="1234567890abcdefghijklmnopstuvwxyz")
    yield client
    await client.close()

@pytest.fixture
def respx_router():
    router = MockRouter(assert_all_called=True)
    with router:
        yield router

@pytest.mark.asyncio
async def test_bazaar(api_client: HypyAsync, respx_router: MockRouter):
    mock_bazaar_data = {
      "success": True,
      "lastUpdated": 1590854517479,
      "products": {
        "INK_SACK:3": {
          "product_id": "INK_SACK:3",
          "sell_summary": [
            {
              "amount": 20569,
              "pricePerUnit": 4.2,
              "orders": 1
            },
            {
              "amount": 140326,
              "pricePerUnit": 3.8,
              "orders": 2
            }
          ],
          "buy_summary": [
            {
              "amount": 640,
              "pricePerUnit": 4.8,
              "orders": 1
            },
            {
              "amount": 640,
              "pricePerUnit": 4.9,
              "orders": 1
            },
            {
              "amount": 25957,
              "pricePerUnit": 5,
              "orders": 3
            }
          ],
          "quick_status": {
            "productId": "INK_SACK:3",
            "sellPrice": 4.2,
            "sellVolume": 409855,
            "sellMovingWeek": 8301075,
            "sellOrders": 11,
            "buyPrice": 4.99260315136572,
            "buyVolume": 1254854,
            "buyMovingWeek": 5830656,
            "buyOrders": 85
          }
        }
      }
    }
    respx_router.get(f"{URL}skyblock/bazaar").respond(status_code=200, json=mock_bazaar_data)
    bazaar_response = await api_client.bazaar()
    assert isinstance(bazaar_response, BazaarResponse)
    assert bazaar_response.success is True
    assert bazaar_response.last_updated == 1590854517479
    assert "INK_SACK:3" in bazaar_response.products
    assert bazaar_response.products["INK_SACK:3"].quick_status.sell_price == 4.2

@pytest.mark.asyncio
async def test_profile_api_failure(api_client: HypyAsync, respx_router: MockRouter):
    profile_uuid = "1234567890"
    mock_failure_response = {
        "success": False,
        "cause": "Malformed UUID"
    }
    respx_router.get(f"{URL}skyblock/profile?profile={profile_uuid}").respond(status_code=422, json=mock_failure_response)
    with pytest.raises(HypixelUnprocessableEntityError, match="Malformed UUID"):
        await api_client.profile(profile_uuid=profile_uuid)

@pytest.mark.asyncio
async def test_profile_forbidden(api_client: HypyAsync, respx_router: MockRouter):
    profile_uuid = "1234567890"
    mock_forbidden_response = {
        "success": False,
        "cause": "Invalid API key"
    }
    respx_router.get(f"{URL}skyblock/profile?profile={profile_uuid}").respond(status_code=403, text="Invalid API key")
    with pytest.raises(HypixelForbiddenError, match="Invalid API key"):
        await api_client.profile(profile_uuid=profile_uuid)

@pytest.mark.asyncio
async def test_bazaar_validation_error(api_client: HypyAsync, respx_router: MockRouter):
    invalid_bazaar_data = {
        "success": True,
        "lastUpdated": 1590854517479
    }
    respx_router.get(f"{URL}skyblock/bazaar").respond(status_code=200, json=invalid_bazaar_data)
    with pytest.raises(HypixelValidationError) as excinfo:
        await api_client.bazaar()
    assert "BazaarResponse" in str(excinfo.value)
    
