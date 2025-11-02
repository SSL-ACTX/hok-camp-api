# hok/__init__.py
"""
Honor of Kings (HOK) Camp Unofficial API Library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An unofficial, asynchronous API wrapper for the Honor of Kings Camp website.

This library provides a simple and typed interface to fetch data such as
hero details, seasonal adjustments, player reviews, and ranking statistics.
"""

__version__ = "1.0.0"
__author__ = "Seuriin"
__license__ = "MIT"

from .hok_api import HOKAPI
from .client import HOKClient
from .cache_manager import cache_manager
from .camp_security import security_manager
from .models import *

__all__ = [
    # Main Client
    "HOKAPI",
    "HOKClient",

    # Managers
    "cache_manager",
    "security_manager",

    # Enums
    "RankType",
    "Position",

    # Common Models
    "GameUserInfo",
    "PublisherInfo",
    "CampAuth",
    "GameHonor",
    "AuthInfo",
    "Tag",
    "Topic",
    "UserInteraction",
    "Icon",
    "ContentTag",
    "HeroBriefInfo",

    # Content-related Models
    "VideoPlaylistItem",
    "Video",
    "NewsContent",
    "PostItemText",
    "PostItemPic",
    "PostItemPart",
    "PostContent",
    "ContentListItem",
    "HomepageContentListResponse",
    "HeroInfoAdjust",
    "AdjustItem",
    "AdjustForSeasonData",
    "AdjustForSeasonResponse",
    "InformationCardTag",
    "InformationCard",
    "InformationCardCategory",
    "GetInformationCardResponse",

    # Hero-related Models
    "GetAllHeroBriefInfoResponse",
    "HeroDisplayData",
    "HeroBaseInfo",
    "HeroBaseData",
    "HeroAdjustDataContent",
    "HeroAdjustData",
    "SkillCost",
    "SkillTag",
    "HeroSkill",
    "SkillSetOrder",
    "ShortStrategySeason",
    "ShortStrategy",
    "RuneEffect",
    "Rune",
    "PassiveSkill",
    "EquipSkill",
    "Equip",
    "SuitStrategySkill",
    "SuitStrategyTagText",
    "SuitStrategy",
    "CombinationHero",
    "CombinationData",
    "Combination",
    "HeroStrategyData",
    "WorldVideo",
    "WorldInfo",
    "ImageMaterial",
    "LibraryMaterial",
    "HeroComic",
    "UGCData",
    "HeroWorldData",
    "HeroDataAllResponse",
    "RankHeroInfo",
    "RankEntry",
    "RankFilter",
    "GetRankListResponse",

    # Review-related Models
    "HotComment",
    "ReviewTagScore",
    "ReviewTagAttribute",
    "ReviewTag",
    "ReviewObjectElement",
    "HandpickList",
    "ReviewObject",
    "ReviewListItem",
    "HeroReviewsData",
    "GetHeroReviewsResponse",
    "CommentListItem",
    "CommentList",
    "ReviewDetail",
]
