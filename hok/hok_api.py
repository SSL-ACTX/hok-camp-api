# hok_api.py
import httpx
import orjson as json
import asyncio
import datetime
from typing import Any, Dict, List, Optional
from functools import wraps

from hok.models import *
from hok.camp_security import security_manager as default_security_manager
from hok.cache_manager import cache_manager

def retry(exceptions, tries=3, delay=2, backoff=2):
    """
    A decorator for retrying a function or method if it raises one of the specified exceptions.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    print(f"Retrying in {mdelay} seconds... ({e.__class__.__name__})")
                    await asyncio.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class HOKAPI:
    """
    Asynchronous client for the Honor of Kings (HOK) Camp API.
    This class now manages the full lifecycle of its components.
    """
    BASE_URL = "https://api-camp.honorofkings.com"

    def __init__(self, region: int = 608, language: str = "en", security_manager=None):
        self.default_headers = {
            'accept': 'application/json, text/plain, */*',
            'camp-language': language,
            'camp-region': str(region),
            'campsource': 'HOK-CAMP',
            'content-type': 'application/json',
            'deviceid': '08a841e996781e9e77d30a4e4420a8f501a280b00624e6d1224bf54aaff73eba',
            'gameid': '29134',
            'origin': 'https://camp.honorofkings.com',
            'referer': 'https://camp.honorofkings.com/',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        }
        timeout = httpx.Timeout(15.0, connect=30.0)
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=self.default_headers,
            timeout=timeout
        )
        # --- IMPROVEMENT: HOKAPI now owns the security manager ---
        self.security_manager = security_manager or default_security_manager

    @retry(httpx.TimeoutException, tries=3, delay=1)
    async def _request(self, method: str, endpoint: str, data: Optional[Dict] = None, use_cache: bool = True) -> Any:
        cache_key = f"{endpoint}:{json.dumps(data).decode()}" if data else endpoint
        if use_cache:
            cached_response = await cache_manager.get(cache_key)
            if cached_response:
                return cached_response

        # Use the instance's security manager
        security_headers = await self.security_manager.get_headers()

        try:
            response = await self.client.request(method, endpoint, content=json.dumps(data) if data else None, headers=security_headers)
            response.raise_for_status()
            json_response = json.loads(response.content)

            if use_cache:
                await cache_manager.set(cache_key, json_response)

            return json_response
        except httpx.RequestError as e:
            print(f"An HTTPX request error occurred: {e.__class__.__name__} - {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise

    def _parse_datetime_str(self, dt_str: str) -> datetime.datetime:
        """Parses an ISO 8601 datetime string, handling the 'Z' suffix."""
        return datetime.datetime.fromisoformat(dt_str.replace('Z', '+00:00'))

    async def get_all_heroes(self, use_cache: bool = True) -> List[HeroBriefInfo]:
        """Fetches brief information for all heroes."""
        response = await self._request("POST", "/api/herowiki/getallherobriefinfo", use_cache=use_cache)
        return [HeroBriefInfo(**hero) for hero in response.get("data", {}).get("heroList", [])]

    async def get_hero_details(self, hero_id: int, use_cache: bool = True) -> Dict:
        """Fetches comprehensive details for a specific hero."""
        payload = {"heroId": hero_id}
        response = await self._request("POST", "/api/herowiki/getherodataall", data=payload, use_cache=use_cache)
        return response.get("data", {})

    async def get_seasonal_adjustments(self, use_cache: bool = True) -> AdjustForSeasonResponse:
        """Fetches hero adjustments for the current season."""
        payload = {"type": 1}
        response = await self._request("POST", "/api/game/adjust/adjustforseason", data=payload, use_cache=use_cache)
        return AdjustForSeasonResponse(**response)

    async def get_hero_rankings(
        self,
        rank_type: RankType = RankType.TIER,
        position: Position = Position.ALL,
        use_cache: bool = True
    ) -> List[RankEntry]:
        """Fetches hero ranking lists based on specified type and position."""
        payload = {
            "rankId": rank_type,
            "position": position,
            "segment": 255,
            "bottomTab": "",
            "gameId": 29134
        }
        endpoint = "/game/hero/getranklist"
        response = await self._request("POST", endpoint, data=payload, use_cache=use_cache)
        return [RankEntry(**entry) for entry in response.get("data", {}).get("list", [])]

    async def get_homepage_content(self, page: int = 1, use_cache: bool = True) -> Dict:
        """Fetches content from the main homepage feed."""
        payload = {"channelID": "camp_homepage_recommend", "page": page, "lastId": "", "limit": 8, "pageSize": 8}
        response = await self._request("POST", "/api/game/camphome/homepagecontentlist", data=payload, use_cache=use_cache)
        return response

    async def get_information_cards(self, use_cache: bool = True) -> List[InformationCardCategory]:
        """Fetches hero information cards."""
        response = await self._request("POST", "/api/game/hero/getinformationcard", data={}, use_cache=use_cache)
        data = response.get("data", {})
        def parse_datetimes_in_dict(d: Any):
            if isinstance(d, dict):
                for k, v in d.items():
                    if isinstance(v, str) and k in ('updateTime'):
                        try:
                            if v: d[k] = self._parse_datetime_str(v)
                        except (ValueError, TypeError): pass
                    else: parse_datetimes_in_dict(v)
            elif isinstance(d, list):
                for item in d: parse_datetimes_in_dict(item)
        parse_datetimes_in_dict(data)
        return [InformationCardCategory(**cat) for cat in data.get("list", [])]

    async def get_hero_reviews(self, use_cache: bool = True) -> GetHeroReviewsResponse:
        """Fetches a list of reviews for all heroes."""
        payload = {"reviewObjID": 100, "renew": False}
        response = await self._request("POST", "/api/game/review/getreviewslistobjs", data=payload, use_cache=use_cache)
        def parse_datetimes_in_dict(d: Any):
            if isinstance(d, dict):
                for k, v in d.items():
                    if isinstance(v, str) and k in ('createTime', 'updateTime', 'publishTime'):
                        try:
                            if v: d[k] = self._parse_datetime_str(v)
                        except (ValueError, TypeError): pass
                    else: parse_datetimes_in_dict(v)
            elif isinstance(d, list):
                for item in d: parse_datetimes_in_dict(item)
        parse_datetimes_in_dict(response)
        return GetHeroReviewsResponse(**response)

    async def close(self):
        """
        Closes the underlying HTTPX client and the security manager daemon.
        This is now the only cleanup method you need to call.
        """
        await self.client.aclose()
        await self.security_manager.close()
