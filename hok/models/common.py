# hok/models/common.py
import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Any, Union, Dict

# --- Common Data Structures Shared Across Multiple Endpoints ---

@dataclass
class GameUserInfo:
    openid: str
    characName: str
    headUrl: str
    roleJob: str
    roleJobName: str
    roleJobIcon: str

@dataclass
class GameInfoItem:
    gameType: int
    gameUserInfo: Union[GameUserInfo, Dict]

    def __post_init__(self):
        """Convert the nested gameUserInfo dict to a GameUserInfo object."""
        if isinstance(self.gameUserInfo, dict):
            self.gameUserInfo = GameUserInfo(**self.gameUserInfo)


@dataclass
class PublisherInfo:
    publisherId: str
    nickname: str
    avatar: str
    showRegionIcon: str
    gameInfo: Union[List[GameInfoItem], List[Dict]]
    publisherType: int

    def __post_init__(self):
        """Convert gameInfo list of dicts to list of GameInfoItem objects."""
        if self.gameInfo and isinstance(self.gameInfo[0], dict):
            self.gameInfo = [GameInfoItem(**info) for info in self.gameInfo]

@dataclass
class CampAuth:
    authType: str
    authTime: int
    authExpireTime: int
    icon: List[str]
    title: str
    parentType: str
    desc: str

@dataclass
class GameHonor:
    heroId: Optional[int] = None
    titleLocationType: Optional[int] = None
    RankTitle: Optional[int] = None
    rank: Optional[int] = None
    fightScore: Optional[int] = None
    gameTitleLocationType: Optional[int] = None
    heroName: Optional[str] = None
    locationName: Optional[str] = None
    branchRoad: Optional[int] = None
    isBranchRoad: Optional[bool] = None
    displayType: Optional[int] = None
    honorTitleName: Optional[str] = None
    branchRoadName: Optional[str] = None

@dataclass
class AuthInfo:
    authType: int
    gameHonor: Optional[GameHonor]
    campAuth: Optional[CampAuth]

@dataclass
class Tag:
    tagId: str
    tagName: str
    tagFullName: str

@dataclass
class Topic:
    topicId: str
    topicName: str
    type: int
    isHot: int
    hotValue: str

@dataclass
class UserInteraction:
    isLike: bool
    isCollect: bool

@dataclass
class Icon:
    iconName: str
    iconUrl: str
    iconType: int

@dataclass
class ContentTag:
    tagEnum: int
    text: str
    fontColor: str
    bgColor: str
    fontColorH5: str
    bgColorH5: str

@dataclass
class HeroBriefInfo:
    heroId: int
    heroName: str
    icon: str
    mainJob: int
    recommendRoad: int
    minorJob: int
    mainJobName: str
    minorJobName: str
    recommendRoadName: str
    firstTimeUpgradeSkill: int
    cover: str
