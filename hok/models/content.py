# hok/models/content.py
import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any
from .common import PublisherInfo, Tag, UserInteraction, Icon, AuthInfo, Topic, ContentTag, HeroBriefInfo

# --- Video/Post/News Related Structures (used in homepage content) ---

@dataclass
class VideoPlaylistItem:
    url: str
    resolutionRatio: int
    bitrate: str
    extra: str

@dataclass
class Video:
    cover: str
    orientation: int
    width: int
    height: int
    playList: List[VideoPlaylistItem]
    duration: int
    displayType: int
    source: int
    videoId: str

@dataclass
class NewsContent:
    title: str
    cover: str
    coverThumb: str
    newsType: int
    video: List[Video]
    newsId: str

@dataclass
class PostItemText:
    text: str
    ext: str

@dataclass
class PostItemPic:
    thumb: str
    original: str
    width: int
    height: int
    isGif: bool

@dataclass
class PostItemPart:
    itemType: int
    text: Optional[PostItemText] = None
    pic: Optional[PostItemPic] = None
    video: Optional[Any] = None
    linkCard: Optional[Any] = None
    jumpLink: Optional[Any] = None
    emote: Optional[Any] = None
    yuanliuPoster: Optional[Any] = None

@dataclass
class PostContent:
    title: str
    type: int
    htmlStr: str
    htmlJson: str
    itemParts: List[PostItemPart]

# --- Homepage Content List ---

@dataclass
class ContentListItem:
    contentType: int
    publisherInfo: PublisherInfo
    publishTime: datetime.datetime
    tags: List[Tag]
    likeCount: str
    readCount: str
    commentCount: str
    heatCount: str
    shareCount: str
    collectCount: str
    language: int
    region: int
    userInteraction: UserInteraction
    icon: List[Icon]
    contentId: str
    authInfo: List[AuthInfo]
    topics: List[Topic]
    customStatus: int
    news: Optional[NewsContent] = None
    post: Optional[PostContent] = None

@dataclass
class HomepageContentListResponse:
    code: int
    msg: str
    data: Dict[str, Union[List[ContentListItem], bool]]

# --- Adjust for Season ---

@dataclass
class HeroInfoAdjust:
    heroId: int
    heroName: str
    icon: str
    winningProbability: float
    appearanceRate: float
    banRote: float
    skilledLevel: Optional[int] = None
    skilledTitle: Optional[str] = None
    skilledTitleIcon: Optional[str] = None

@dataclass
class AdjustItem:
    type: int
    shortDesc: str
    desc: str
    contentTag: Union[ContentTag, Dict]
    heroInfo: Union[HeroInfoAdjust, Dict]

    def __post_init__(self):
        """Convert nested dicts to dataclass objects."""
        if isinstance(self.contentTag, dict):
            self.contentTag = ContentTag(**self.contentTag)
        if isinstance(self.heroInfo, dict):
            self.heroInfo = HeroInfoAdjust(**self.heroInfo)

@dataclass
class AdjustForSeasonData:
    seasonId: str
    seasonName: str
    adjustList: Union[List[AdjustItem], List[Dict]]

    def __post_init__(self):
        """Convert adjustList of dicts to list of AdjustItem objects."""
        if self.adjustList and isinstance(self.adjustList[0], dict):
            self.adjustList = [AdjustItem(**item) for item in self.adjustList]

@dataclass
class AdjustForSeasonResponse:
    code: int
    msg: str
    data: Union[AdjustForSeasonData, Dict]

    def __post_init__(self):
        """Convert data dict to AdjustForSeasonData object."""
        if isinstance(self.data, dict):
            self.data = AdjustForSeasonData(**self.data)

# --- Get Information Card ---

@dataclass
class InformationCardTag:
    tag: str
    fontColor: str
    bgColor: str

@dataclass
class InformationCard:
    heroInfo: Union[HeroBriefInfo, Dict] # Allow Dict for init
    tags: Union[List[InformationCardTag], List[Dict]] # Allow List[Dict] for init
    content: str
    updateTime: datetime.datetime
    id: str

    def __post_init__(self):
        """Convert nested dicts into dataclass objects."""
        if isinstance(self.heroInfo, dict):
            self.heroInfo = HeroBriefInfo(**self.heroInfo)
        if self.tags and isinstance(self.tags[0], dict):
            self.tags = [InformationCardTag(**tag) for tag in self.tags]


@dataclass
class InformationCardCategory:
    category: str
    categoryIcon: str
    cardList: Union[List[InformationCard], List[Dict]] # Allow List[Dict] for init

    def __post_init__(self):
        """Convert cardList of dicts to list of InformationCard objects."""
        if self.cardList and isinstance(self.cardList[0], dict):
            self.cardList = [InformationCard(**card) for card in self.cardList]

@dataclass
class GetInformationCardResponse:
    code: int
    msg: str
    data: Dict[str, Union[datetime.datetime, List[InformationCardCategory]]]
