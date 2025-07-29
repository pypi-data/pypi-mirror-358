import json
import httpx
from pydantic import BaseModel, ValidationError
from typing import Type, TypeVar, Optional, Any, Dict
from hypy.exceptions import (
    HypixelAPIError,
    HypixelRequestError,
    HypixelHTTPError,
    HypixelRateLimitError,
    HypixelForbiddenError,
    HypixelNotFoundError,
    HypixelValidationError,
    HypixelInvalidResponseError,
    HypixelBadRequestError,
    HypixelUnprocessableEntityError,
    HypixelServiceUnavailableError
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

T = TypeVar('T', bound=BaseModel)

class Hypy:
    URL = "https://api.hypixel.net/v2/"
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
        self._client = httpx.Client(headers={"API-Key": self.api_key})
        self.headers = {
            "API-Key": self.api_key
        }

    def close(self):
        self._client.close()

    def _make_request(self, endpoint: str, model: Optional[Type[T]], params: Optional[Dict[str, Any]] = None, requires_auth: bool = True) -> T | Dict[str, Any]:
        full_url = self.URL + endpoint.lstrip("/")
        current_headers = self.headers if requires_auth else None
        try:
            response = self._client.get(full_url, params=params, headers=current_headers)
            if response.status_code == 400:
                raise HypixelBadRequestError(response)
            if response.status_code == 422:
                raise HypixelUnprocessableEntityError(response)
            if response.status_code == 429:
                raise HypixelRateLimitError(response)
            if response.status_code == 403:
                raise HypixelForbiddenError(response)
            if response.status_code == 404:
                raise HypixelNotFoundError(response)
            if response.status_code == 503:
                raise HypixelServiceUnavailableError(response)
            response.raise_for_status()
            data = response.json()
            if not data.get("success"):
                cause = data.get("cause", "Unknown error")
                raise HypixelInvalidResponseError(f"API request was not successful: {cause}")
            if model:
                try:
                    return model.model_validate(data)
                except ValidationError as e:
                    raise HypixelValidationError(model, e) from e
            else:
                return data

        except httpx.RequestError as e:
            raise HypixelRequestError(e) from e
        except httpx.HTTPStatusError as e:
            raise HypixelHTTPError(e.response) from e
        except json.JSONDecodeError as e:
            raise HypixelInvalidResponseError(f"Failed to decode JSON response: {e}") from e
        except HypixelAPIError:
            raise
        except Exception as e:
            raise HypixelAPIError(f"An unexpected error occurred: {e}") from e

    def bazaar(self) -> BazaarResponse:
        """
        Returns the list of products along with their sell summary, buy summary and quick status.\n
        **Product Description**\n
        The returned product info has 3 main fields:\n
        * ``buy_summary``
        * ``sell_summary``
        * ``quick_status``
        ``buy_summary`` and ``sell_summary`` are the current top 30 orders for each transaction type (in-game example: Stock of Stonks).\n
        ``quick_status`` is a computed summary of the live state of the product (used for advanced mode view in the bazaar):\n
        * ``sellVolume`` and ``buyVolume`` are the sum of item amounts in all orders.\n
            * ``sellPrice`` and ``buyPrice`` are the weighted average of the top 2% of orders by volume.
            * ``movingWeek`` is the historic transacted volume from last 7d + live state.
            * ``sellOrders`` and ``buyOrders`` are the count of active orders.\n
        **Doesn't require an API key.**\n
        See More: `Hypixel API Documentation <https://api.hypixel.net/#tag/SkyBlock/paths/~1v2~1skyblock~1bazaar/get>`_
        :return: BazaarResponse
        """
        return self._make_request(endpoint="skyblock/bazaar", model=BazaarResponse, requires_auth=False)

    def profile(self, profile_uuid: str) -> ProfileResponse:
        """
        SkyBlock profile data, such as stats, objectives etc. The data returned can differ depending on the players in-game API settings.
        :param profile_uuid:
        :return: ProfileResponse
        """
        return self._make_request(endpoint="skyblock/profile", model=ProfileResponse, requires_auth=True, params={"profile": profile_uuid})

    def profiles(self, player_uuid: str):
        """
        SkyBlock profile data, such as stats, objectives etc. The data returned can differ depending on the players in-game API settings.
        :param player_uuid:
        :return: ProfilesResponse
        """
        return self._make_request(endpoint="skyblock/profiles", model=ProfilesResponse, requires_auth=True, params={"uuid": player_uuid})

    def museum(self, profile_uuid: str):
        """
        SkyBlock museum data for all members of the provided profile. The data returned can differ depending on the players in-game API settings.
        :param profile_uuid:
        :return: MuseumResponse
        """
        return self._make_request(endpoint="skyblock/museum", model=MuseumResponse, requires_auth=True, params={"profile": profile_uuid})

    def garden(self, profile_uuid: str):
        """
        SkyBlock garden data for the provided profile.
        :param profile_uuid:
        :return: GardenResponse
        """
        return self._make_request(endpoint="skyblock/garden", model=GardenResponse, requires_auth=True, params={"profile": profile_uuid})

    def bingo_data(self, player_uuid: str):
        """
        Bingo data for participated events of the provided player.
        :param player_uuid:
        :return: BingoDataResponse
        """
        return self._make_request(endpoint="skyblock/bingo", model=BingoDataResponse, requires_auth=True, params={"uuid": player_uuid})

    def firesale(self):
        """
        Retrieve the currently active or upcoming Fire Sales for SkyBlock.\n
        **Doesn't require an API key.**
        :return: FireSalesResponse
        """
        return self._make_request(endpoint="skyblock/firesales", model=FireSalesResponse, requires_auth=False)

    def collections(self):
        """
        Information regarding Collections in the SkyBlock game.\n
        **Doesn't require an API key.**
        :return: CollectionsResponse
        """
        return self._make_request(endpoint="resources/skyblock/collections", model=CollectionsResponse, requires_auth=False)

    def skills(self):
        """
        Information regarding skills in the SkyBlock game.\n
        **Doesn't require an API key.**
        :return: SkillsResponse
        """
        return self._make_request(endpoint="resources/skyblock/skills", model=SkillsResponse, requires_auth=False)

    def items(self):
        """
        Information regarding items in the SkyBlock game.\n
        **Doesn't require an API key.**
        :return: ItemsResponse
        """
        return self._make_request(endpoint="resources/skyblock/items", model=ItemsResponse, requires_auth=False)

    def elections(self):
        """
        Information regarding the current mayor and ongoing election in SkyBlock.\n
        **Doesn't require an API key.**
        :return: ElectionsResponse
        """
        return self._make_request(endpoint="resources/skyblock/election", model=ElectionsResponse, requires_auth=False)

    def bingo(self):
        """
        Information regarding the current bingo event and its goals.\n
        **Doesn't require an API key.**
        :return: BingoResponse
        """
        return self._make_request(endpoint="resources/skyblock/bingo", model=BingoResponse, requires_auth=False)

    def news(self):
        """
        Fetches the news data from the Hypixel API.\n
        :return: NewsResponse
        """
        return self._make_request(endpoint="skyblock/news", model=NewsResponse, requires_auth=True)

    def request_auctions(self, player_uuid: Optional[str] = None, profile_uuid: Optional[str] = None, auction_uuid: Optional[str] = None) -> RequestAuctionsResponse:
        """
        Returns the auctions selected by the provided query. Only one query parameter can be used in a single request, and cannot be filtered by multiple.
        :param player_uuid: User UUID
        :param profile_uuid: Skyblock Profile UUID
        :param auction_uuid: Auction UUID
        :return: RequestAuctionsResponse
        """
        params = {}
        if player_uuid:
            params["player"] = player_uuid
        if profile_uuid:
            params["profile"] = profile_uuid
        if auction_uuid:
            params["uuid"] = auction_uuid
        return self._make_request(endpoint="skyblock/auction", model=RequestAuctionsResponse, requires_auth=True, params={"uuid": auction_uuid, "profile": profile_uuid, "player": player_uuid})

    def active_auctions(self, page: int = 0):
        """
        Returns the currently active auctions sorted by last updated first and paginated.
        **Doesn't require an API key.**
        :param page: Page number for pagination (default is 0).
        :return: ActiveAuctionsResponse
        """
        return self._make_request(endpoint="skyblock/auctions", model=ActiveAuctionsResponse, requires_auth=False, params={"page": page})

    def recently_ended_auction(self):
        """
        SkyBlock auctions which ended in the last 60 seconds.
        **Doesn't require an API key.**
        :return: RecentlyEndedAuctionResponse
        """
        return self._make_request(endpoint="skyblock/auctions_ended", model=RecentlyEndedAuctionsResponse, requires_auth=False)