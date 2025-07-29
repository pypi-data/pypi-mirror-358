from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, List, Dict, Any, Annotated
from datetime import datetime, timezone

def timestamp_to_datetime(timestamp: Optional[int]) -> Optional[str]:
    if timestamp is None:
        return None
    if not isinstance(timestamp, (int, float)):
        raise ValueError("Timestamp must be an integer or float")
    try:
        dt_obj = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
        return dt_obj.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OSError) as e:
        raise ValueError(f"Invalid timestamp: {timestamp}") from e

# Bazaar Modals

class SummaryOrder(BaseModel):
    amount: int
    price_per_unit: float = Field(alias="pricePerUnit")
    orders: int
    class Config:
        extra = "ignore"
        validate_by_name = True

class QuickStatus(BaseModel):
    product_id: str = Field(alias="productId")
    sell_price: float = Field(alias="sellPrice", default=0.0)
    sell_volume: int = Field(alias="sellVolume", default=0)
    sell_moving_week: int = Field(alias="sellMovingWeek", default=0)
    sell_orders: int = Field(alias="sellOrders", default=0)
    buy_price: float = Field(alias="buyPrice", default=0.0)
    buy_volume: float = Field(alias="buyVolume", default=0)
    buy_moving_week: int = Field(alias="buyMovingWeek", default=0)
    buy_orders: int = Field(alias="buyOrders", default=0)
    class Config:
        extra = "ignore"
        validate_by_name = True

class BazaarProduct(BaseModel):
    product_id: str
    sell_summary: List[SummaryOrder] = Field(default_factory=list)
    buy_summary: List[SummaryOrder] = Field(default_factory=list)
    quick_status: QuickStatus
    class Config:
        extra = "ignore"
        validate_by_name = True

class BazaarResponse(BaseModel):
    success: bool
    last_updated: int = Field(alias="lastUpdated")
    products: Dict[str, BazaarProduct]
    class Config:
        extra = "ignore"
        validate_by_name = True

# Profile Modals

class Currencies(BaseModel):
    coin_purse: float = 0.0
    class Config:
        extra = "ignore"

class Pet(BaseModel):
    uuid: Optional[str] = None
    uniqueId: Optional[str] = None
    type: Optional[str] = None
    exp: float = 0.0
    active: bool = False
    tier: Optional[str] = None
    heldItem: Optional[str] = None
    candyUsed: int = 0
    skin: Optional[str] = None
    class Config:
        extra = "ignore"
        validate_by_name = True

class PetsData(BaseModel):
    pets: List[Pet] = Field(default_factory=list)
    class Config:
        extra = "ignore"

class MembersDetails(BaseModel):
    rift: Optional[Any] = None
    player_data: Optional[Dict[str, Any]] = None
    events: Optional[Dict[str, Any]] = None
    accessory_bag_storage: Optional[Dict[str, Any]] = None
    leveling: Optional[Dict[str, Any]] = None
    jacobs_contest: Optional[Dict[str, Any]] = None
    nether_island: Optional[Dict[str, Any]] = None
    experimentation: Optional[Dict[str, Any]] = None
    mining_core: Optional[Dict[str, Any]] = None
    bestiary: Optional[Dict[str, Any]] = None
    quests: Optional[Dict[str, Any]] = None
    player_stats: Optional[Dict[str, Any]] = None
    forge: Optional[Dict[str, Any]] = None
    fairy_soul: Optional[Dict[str, Any]] = None
    trophy_fish: Optional[Dict[str, Any]] = None
    objectives: Optional[Dict[str, Any]] = None
    slayer: Optional[Dict[str, Any]] = None
    currencies: Optional[Currencies] = None
    profile: Optional[Dict[str, Any]] = None
    player_id: Optional[str] = None
    pets_data: Optional[PetsData] = None
    class Config:
        extra = "ignore"
        validate_by_name = True

class BankingDetails(BaseModel):
    balance: int
    transactions: List[Dict[str, Any]]
    class Config:
        extra = "ignore"
        validate_by_name = True

class CurrentlyUpgrading(BaseModel):
    upgrade: Optional[str] = None
    new_tier: Optional[int] = None
    start_ms: Optional[int] = None
    who_started: Optional[str] = None

class UpgradeState(BaseModel):
    upgrade: Optional[str] = str
    tier: Optional[int] = None
    started_ms: Optional[int] = None
    started_by: Optional[str] = None
    claimed_ms: Optional[int] = None
    claimed_by: Optional[str] = None

class CommunityUpgrades(BaseModel):
    currently_upgrading: Optional[CurrentlyUpgrading] = None
    upgrade_states: Optional[List[UpgradeState]] = Field(default_factory=list)
    class Config:
        extra = "ignore"

class Profile(BaseModel):
    profile_id: str
    community_upgrades: Optional[CommunityUpgrades] = None
    members: Dict[str, MembersDetails] = Field(default_factory=dict)
    game_mode: Optional[str] = None
    cute_name: Optional[str] = None
    class Config:
        extra = "ignore"
        validate_by_name = True

class ProfileResponse(BaseModel):
    success: bool
    profile: Optional[Profile] = None
    class Config:
        extra = "ignore"

# Profiles Models

class ProfilesResponse(BaseModel):
    success: bool
    profiles: Optional[List[Profile]] = Field(default_factory=list)
    class Config:
        extra = "ignore"
        validate_by_name = True

# Museum Models

class MuseumItemItems(BaseModel):
    type: Optional[int] = None
    data: Optional[str] = None
    class Config:
        extra = "ignore"

class MuseumItem(BaseModel):
    donated_time: Optional[int] = None
    featured_slot: Optional[str] = None
    borrowing: bool = False
    items: Optional[MuseumItemItems] = None
    class Config:
        extra = "ignore"

class MuseumMembers(BaseModel):
    value: Optional[int] = None
    appraisal: bool = False
    items: Optional[Dict[str, MuseumItem]] = None
    special: Optional[List[Dict[str, Any]]] = None

class MuseumResponse(BaseModel):
    success: bool
    members: Optional[Dict[str, MuseumMembers]] = None
    class Config:
        extra = "ignore"
        validate_by_name = True

# Garden Models

class ComposterUpgrades(BaseModel):
    speed: Optional[int] = None
    multi_drop: Optional[int] = None
    fuel_cap: Optional[int] = None
    organic_matter_cap: Optional[int] = None
    cost_reduction: Optional[int] = None

class Composter(BaseModel):
    organic_matter: Optional[int] = None
    fuel_units: Optional[int] = None
    compost_units: Optional[int] = None
    compost_items: Optional[int] = None
    conversion_ticks: Optional[int] = None
    last_save: Optional[int] = None
    upgrades: Optional[Dict[str, ComposterUpgrades]] = None

class GardenCommissionData(BaseModel):
    visits: Optional[Dict[str, Any]] = None
    completed: Optional[Dict[str, Any]] = None
    total_completed: Optional[int] = None
    unique_npcs_served: Optional[int] = None

class GardenDetails(BaseModel):
    uuid: Optional[str] = None
    unlocked_plots_ids: Optional[List[str]] = Field(default_factory=list)
    commission_data: Optional[GardenCommissionData] = None
    resource_collected: Optional[Dict[str, Any]] = None
    composter_data: Optional[Composter] = None
    garden_experience: Optional[float] = None
    selected_barn_skin: Optional[str] = None
    crop_upgrade_levels: Optional[Dict[str, Any]] = None
    unlocked_barn_skins: Optional[List[str]] = Field(default_factory=list)


class GardenResponse(BaseModel):
    success: bool
    garden: Optional[Dict[str, Any]] = None
    class Config:
        extra = "ignore"
        validate_by_name = True

# Bingo data Models

class BingoEvents(BaseModel):
    key: Optional[int] = None
    points: Optional[int] = None
    completed_goals: Optional[List[str]] = Field(default_factory=list)

class BingoDataResponse(BaseModel):
    success: bool
    events: Optional[List[BingoEvents]] = Field(default_factory=list)
    class Config:
        extra = "ignore"
        validate_by_name = True

# Active Fire Sale Models

class FireSaleItem(BaseModel):
    item_id: Optional[str] = None
    start: Annotated[Optional[str], BeforeValidator(timestamp_to_datetime)]
    end: Annotated[Optional[str], BeforeValidator(timestamp_to_datetime)]
    amount: Optional[int] = None
    price: Optional[int] = None

class FireSalesResponse(BaseModel):
    success: bool
    sales: Optional[List[FireSaleItem]] = Field(default_factory=list)
    class Config:
        extra = "ignore"
        validate_by_name = True

# Collections Models

class CollectionsTier(BaseModel):
    tier: Optional[int] = None
    amountRequired: Optional[int] = None
    unlocks: Optional[List[str]] = Field(default_factory=list)

class CollectionsItem(BaseModel):
    name: Optional[str] = None
    maxTier: Optional[int] = None
    tiers: Optional[List[CollectionsTier]] = Field(default_factory=list)

class CollectionsCategory(BaseModel):
    name: Optional[str] = None
    items: Optional[Dict[str, CollectionsItem]] = None

class CollectionsResponse(BaseModel):
    success: bool
    lastUpdated: Annotated[Optional[str], BeforeValidator(timestamp_to_datetime)]
    version: Optional[str] = None
    collections: Optional[Dict[str, CollectionsCategory]] = None
    class Config:
        extra = "ignore"
        validate_by_name = True

# Skills Models

class SkillsLevels(BaseModel):
    level: Optional[int] = None
    totalExpRequired: Optional[float] = None
    unlocks: Optional[List[str]] = Field(default_factory=list)

class SkillsCategory(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    maxLevel: Optional[int] = None
    skills: Optional[List[SkillsLevels]] = None

class SkillsResponse(BaseModel):
    success: bool
    lastUpdated: Annotated[Optional[str], BeforeValidator(timestamp_to_datetime)]
    version: Optional[str] = None
    skills: Optional[Dict[str, Any]] = None
    class Config:
        extra = "ignore"
        validate_by_name = True

# Items Models

class ItemsDetails(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    tier: Optional[str] = None
    material: Optional[str] = None
    class Config:
        extra = "allow"
        validate_by_name = True

class ItemsResponse(BaseModel):
    success: bool
    lastUpdated: Annotated[Optional[str], BeforeValidator(timestamp_to_datetime)]
    items: Optional[List[ItemsDetails]] = None
    class Config:
        extra = "ignore"
        validate_by_name = True

# Elections Models

class MayorPerks(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    class Config:
        extra = "allow"

class CandidatesDetails(BaseModel):
    key: Optional[str] = None
    name: Optional[str] = None
    perks: Optional[List[MayorPerks]] = Field(default_factory=list)
    class Config:
        extra = "allow"

class MinisterDetails(BaseModel):
    key: Optional[str] = None
    name: Optional[str] = None
    perk: Optional[MayorPerks] = None

class ElectionDetails(BaseModel):
    year: Optional[int] = None
    candidates: Optional[List[CandidatesDetails]] = None

class MayorDetails(BaseModel):
    key: Optional[str] = None
    name: Optional[str] = None
    perks: Optional[List[MayorPerks]] = Field(default_factory=list)
    minister: Optional[MinisterDetails] = None
    election: Optional[ElectionDetails] = None

class ElectionsResponse(BaseModel):
    success: bool
    lastUpdated: Annotated[Optional[str], BeforeValidator(timestamp_to_datetime)]
    mayor: Optional[MayorDetails] = None
    current: Optional[ElectionDetails] = None
    class Config:
        extra = "ignore"
        validate_by_name = True

# Bingo Models

class BingoGoals(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    tiers: Optional[List[int]] = Field(default_factory=list)
    progress: Optional[int] = None
    lore: Optional[str] = None
    fullLore: Optional[List[str]] = None
    class Config:
        extra = "allow"

class BingoResponse(BaseModel):
    success: bool
    lastUpdated: Annotated[Optional[str], BeforeValidator(timestamp_to_datetime)]
    id: Optional[int] = None
    name: Optional[str] = None
    start: Annotated[Optional[str], BeforeValidator(timestamp_to_datetime)]
    end: Annotated[Optional[str], BeforeValidator(timestamp_to_datetime)]
    modifier: Optional[str] = None
    goals: Optional[List[BingoGoals]] = None

# News Models

class NewsDetails(BaseModel):
    item: Optional[Dict[str, Any]] = None
    link: Optional[str] = None
    title: Optional[str] = None
    text: Optional[str] = None

class NewsResponse(BaseModel):
    success: bool
    items: Optional[List[NewsDetails]] = None
    class Config:
        extra = "ignore"
        validate_by_name = True

# Request Auctions Models

class RequestAuctionsBids(BaseModel):
    auction_id: Optional[str] = None
    bidder: Optional[str] = None
    profile_id: Optional[str] = None
    amount: Optional[int] = None
    time: Annotated[Optional[str], BeforeValidator(timestamp_to_datetime)] = Field(alias="timestamp")

class AuctionsDetails(BaseModel):
    uuid: Optional[str] = None
    auctioneer: Optional[str] = None
    profile_id: Optional[str] = None
    coop: Optional[List[str]] = Field(default_factory=list)
    start: Annotated[Optional[str], BeforeValidator(timestamp_to_datetime)]
    end: Annotated[Optional[str], BeforeValidator(timestamp_to_datetime)]
    item_name: Optional[str] = None
    item_lore: Optional[str] = None
    extra: Optional[str] = None
    tier: Optional[str] = None
    starting_bid: Optional[int] = None
    claimed: Optional[bool] = None
    claimed_bidders: Optional[List[str]] = Field(default_factory=list)
    highest_bid_amount: Optional[int] = None
    bids: Optional[List[RequestAuctionsBids]] = Field(default_factory=list)

class RequestAuctionsResponse(BaseModel):
    success: bool
    auctions: Optional[List[AuctionsDetails]] = None
    class Config:
        extra = "ignore"
        validate_by_name = True

# Active Auctions Models

class ActiveAuctionsResponse(BaseModel):
    success: bool
    page: Optional[int] = None
    total_pages: Optional[int] = None
    totalAuctions: Optional[int] = None
    lastUpdated: Annotated[Optional[str], BeforeValidator(timestamp_to_datetime)]
    auctions: Optional[List[AuctionsDetails]] = None
    class Config:
        extra = "ignore"
        validate_by_name = True

# Recently Ended Auctions Models

class RecentlyAuctionsDetails(BaseModel):
    auction_id: Optional[str] = None
    seller: Optional[str] = None
    seller_profile: Optional[str] = None
    buyer: Optional[str] = None
    buyer_profile: Optional[str] = None
    time: Annotated[Optional[str], BeforeValidator(timestamp_to_datetime)] = Field(alias="timestamp")
    price: Optional[int] = None
    bin: Optional[bool] = None
    item_bytes: Optional[str] = None

class RecentlyEndedAuctionsResponse(BaseModel):
    success: bool
    lastUpdated: Annotated[Optional[str], BeforeValidator(timestamp_to_datetime)]
    auctions: Optional[List[RecentlyAuctionsDetails]] = None
    class Config:
        extra = "ignore"
        validate_by_name = True