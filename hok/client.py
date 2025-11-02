# hok/client.py
# WIP - Use low-level api instead
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from .hok_api import HOKAPI
from .models import *
from .cache_manager import cache_manager

@dataclass
class RichRankEntry:
    """
    An enriched ranking entry that COMBINES the original RankEntry
    with its corresponding HeroBriefInfo.
    """
    rank_data: RankEntry
    hero_info: HeroBriefInfo

@dataclass
class RichAdjustItem:
    """Combines an adjustment item with full hero info."""
    adjust_data: AdjustItem
    hero_info: Optional[HeroBriefInfo]

@dataclass
class RichInformationCard:
    """Combines an information card with full hero info."""
    card_data: InformationCard
    hero_info: Optional[HeroBriefInfo]

class HOKClient:
    """
    A high-level, stateful client for the HOK API.

    This client abstracts away common boilerplate, like fetching and mapping
    hero names to other data, and provides automatic resource management
    via the async context manager protocol. It returns rich, combined data
    structures for ease of use.
    """
    _hero_list_cache: Optional[List[HeroBriefInfo]] = None
    _hero_map_cache: Optional[Dict[int, HeroBriefInfo]] = None

    def __init__(self, region: int = 608, language: str = "en"):
        """Initializes the client with a low-level API instance."""
        self.api = HOKAPI(region=region, language=language)

    async def __aenter__(self):
        """Enter the async context, initializing the cache."""
        await cache_manager.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context, ensuring all resources are closed."""
        await self.api.close()

    async def _get_hero_map(self) -> Dict[int, HeroBriefInfo]:
        """
        Fetches the full hero list and caches it in memory for the
        lifetime of the client instance. This is the core of the abstraction.
        """
        if self._hero_map_cache is None:
            self._hero_list_cache = await self.api.get_all_heroes()
            self._hero_map_cache = {hero.heroId: hero for hero in self._hero_list_cache}
        return self._hero_map_cache

    # --- Hero Endpoints ---

    async def get_all_heroes(self) -> List[HeroBriefInfo]:
        """
        Gets brief information for all heroes, caching the result in memory.
        """
        await self._get_hero_map()
        return self._hero_list_cache

    async def get_hero_details(self, hero_id: int) -> Dict[str, Any]:
        """
        Fetches comprehensive details for a specific hero.
        (This is a direct pass-through as it's already hero-specific).
        """
        return await self.api.get_hero_details(hero_id)

    # --- Ranking Endpoints (with Enrichment) ---

    async def get_rich_hero_rankings(
        self,
        rank_type: RankType = RankType.TIER,
        position: Position = Position.ALL,
    ) -> List[RichRankEntry]:
        """
        Fetches hero rankings and automatically enriches them by combining
        the rank data with full hero information.
        """
        hero_map = await self._get_hero_map()
        raw_rankings = await self.api.get_hero_rankings(rank_type=rank_type, position=position)

        return [
            RichRankEntry(rank_data=rank_entry, hero_info=hero_map.get(rank_entry.heroId))
            for rank_entry in raw_rankings
            if rank_entry.heroId in hero_map
        ]

    # --- Content Endpoints (with Enrichment where applicable) ---

    async def get_rich_seasonal_adjustments(self) -> List[RichAdjustItem]:
        """
        Fetches hero adjustments for the current season and enriches
        each adjustment with full hero information.
        """
        hero_map = await self._get_hero_map()
        response = await self.api.get_seasonal_adjustments()

        if not response or not response.data:
            return []

        return [
            RichAdjustItem(
                adjust_data=item,
                hero_info=hero_map.get(item.heroInfo.heroId)
            )
            for item in response.data.adjustList
        ]

    async def get_rich_information_cards(self) -> List[RichInformationCard]:
        """
        Fetches hero information cards and enriches each card
        with the full hero information object.
        """
        hero_map = await self._get_hero_map()
        card_categories = await self.api.get_information_cards()

        rich_cards = []
        for category in card_categories:
            for card in category.cardList:
                hero_id = card.heroInfo.heroId
                rich_cards.append(
                    RichInformationCard(
                        card_data=card,
                        hero_info=hero_map.get(hero_id)
                    )
                )
        return rich_cards

    async def get_hero_reviews(self) -> GetHeroReviewsResponse:
        """
        Fetches a list of reviews for all heroes.
        (Pass-through, as this endpoint is already comprehensive).
        """
        return await self.api.get_hero_reviews()

    async def get_homepage_content(self, page: int = 1) -> Dict:
        """
        Fetches content from the main homepage feed.
        (Pass-through, as this is generic content).
        """
        return await self.api.get_homepage_content(page=page)
