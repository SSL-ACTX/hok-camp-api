# hok/models/hero.py
import datetime
from dataclasses import dataclass, field
from enum import IntEnum
from typing import List, Optional, Dict, Any, Union
from .common import HeroBriefInfo, ContentTag, PublisherInfo, Tag, UserInteraction, Icon, AuthInfo, Topic
from .content import NewsContent
from .review import ReviewDetail, CommentList

# --- Get All Hero Brief Info ---

@dataclass
class GetAllHeroBriefInfoResponse:
    code: int
    msg: str
    data: Dict[str, List[HeroBriefInfo]]

# --- Get Hero Data All (Specific Hero) ---

@dataclass
class HeroDisplayData:
    heroCover: str
    heroCoverHz: str
    heroCoverFigure: str
    heroCoverColor: str
    heroTopCover: str
    activityIcon: str
    heroWorldIcon: str

@dataclass
class HeroBaseInfo:
    heroInfo: HeroBriefInfo
    displayData: HeroDisplayData
    cg: Optional[Any]

@dataclass
class HeroBaseData:
    hot: str
    winRate: str
    matchRate: str
    banRate: str

@dataclass
class HeroAdjustDataContent:
    shortDesc: str
    desc: str
    contentTag: ContentTag

@dataclass
class HeroAdjustData:
    seasonId: str
    seasonName: str
    versionName: str
    versionPublishTime: datetime.datetime
    isCurrent: bool
    adjustContent: HeroAdjustDataContent

@dataclass
class SkillCost:
    skillCostType: int
    skillCost: int

@dataclass
class SkillTag:
    name: str
    backgroundColor: str
    textColor: str

@dataclass
class HeroSkill:
    skillId: int
    skillName: str
    skillIcon: str
    skillDesc: str
    skillCostList: SkillCost
    skillType: int
    skillTag: List[SkillTag]
    skillCd: int
    skillVideo: str
    skillIndex: int
    isUlt: bool
    isPassive: bool
    skillProirity: int
    defaultSkillVideo: str

@dataclass
class SkillSetOrder:
    skillList: List[HeroSkill]
    setOrder: int

@dataclass
class ShortStrategySeason:
    seasonId: str
    seasonName: str

@dataclass
class ShortStrategy:
    title: str
    content: str
    hero: HeroBriefInfo
    season: ShortStrategySeason
    nickname: str
    type: int
    tagText: List[Any]

@dataclass
class RuneEffect:
    effectType: int
    valueType: int
    value: int

@dataclass
class Rune:
    runeId: int
    runeName: str
    runeIcon: str
    runeCommonIcon: int
    runeLevel: int
    runeDesc: str
    runeColor: int
    runeEffect: List[RuneEffect]

@dataclass
class PassiveSkill:
    id: int
    name: str

@dataclass
class EquipSkill:
    id: int
    name: str

@dataclass
class Equip:
    equipId: int
    equipName: str
    equipIcon: str
    preEquipIds: List[int]
    equipDesc: str
    equipPrice: int
    equipType: int
    equipLevel: int
    equipShowId: int
    equipNarrativeDesc: str
    isTopEquip: bool
    equipDescLabel: str
    equipEffects: List[Dict[str, Any]]
    equipSkills: List[EquipSkill]
    passiveSkills: List[PassiveSkill]

@dataclass
class SuitStrategySkill:
    skillId: int
    skillName: str
    skillIcon: str
    skillDesc: str
    skillCd: int
    skillVideo: str

@dataclass
class SuitStrategyTagText:
    id: int
    name: str
    position: List[int]
    equipIds: List[int]
    type: int

@dataclass
class SuitStrategy:
    position: int
    runes: List[Rune]
    runeIds: List[int]
    equips: List[Equip]
    equipIds: List[int]
    skills: SuitStrategySkill
    desc: str
    title: str
    hero: HeroBriefInfo
    season: ShortStrategySeason
    nickname: str
    type: int
    tagText: List[SuitStrategyTagText]

@dataclass
class CombinationHero:
    heroId: int
    heroName: str
    heroIcon: str

@dataclass
class CombinationData:
    dataValue: str
    dataType: int
    dataDesc: str

@dataclass
class Combination:
    heroCombination: List[CombinationHero]
    combinationDesc: str
    combinationData: List[CombinationData]
    combinationType: int

@dataclass
class HeroStrategyData:
    skill: List[SkillSetOrder]
    baseTechVideo: str
    advancedTechVideo: str
    shortStrategy: List[ShortStrategy]
    suitStrategy: List[SuitStrategy]
    combination: List[Combination]
    techVideoCover: str

@dataclass
class WorldVideo:
    videoUrl: str

@dataclass
class WorldInfo:
    height: str
    region: str
    identity: str
    video: WorldVideo
    energy: str

@dataclass
class ImageMaterial:
    id: int
    title1Key: str
    title1: str
    title2Key: str
    title2: str
    title3Key: str
    title3: str
    oriPicUrl: str
    oriPicHeight: int
    oriPicWidth: int
    gameID: str
    category: List[int]
    attachment: List[Any]
    typeTag: str
    heatValue: int
    attributeList: List[str]

@dataclass
class LibraryMaterial:
    materialType: int
    categoryType: int
    image: ImageMaterial

@dataclass
class HeroComic:
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
    userInteraction: Optional[UserInteraction]
    icon: List[Icon]
    contentId: str
    authInfo: List[AuthInfo]
    topics: List[Topic]
    customStatus: int
    news: NewsContent

@dataclass
class UGCData:
    reviewDetail: ReviewDetail
    commentList: CommentList
    events: Optional[Any]

@dataclass
class HeroWorldData:
    world: WorldInfo
    libraryList: List[LibraryMaterial]
    heroComic: List[HeroComic]

@dataclass
class HeroDataAllResponse:
    code: int
    msg: str
    data: Dict[str, Any]

# --- Get Rank List ---

@dataclass
class RankHeroInfo:
    heroId: int
    heroName: str
    heroIcon: str
    heroCareer: str
    heroCover: str

@dataclass
class RankEntry:
    heroId: int
    banRate: float
    showRate: float
    winRate: float
    tRank: int
    heroInfo: Union[RankHeroInfo, Dict]
    position: int
    beginPhase: float
    midPhase: float
    endPhase: float
    killNum: float
    output: float
    money: float
    moneyPerMin: float
    suffer: float
    assist: float
    towerDamage: float
    towerNum: float
    mvp: float
    goldPlay: float
    teamWinRate: float

    def __post_init__(self):
        """Ensure nested heroInfo dict is converted to a RankHeroInfo object."""
        if isinstance(self.heroInfo, dict):
            self.heroInfo = RankHeroInfo(**self.heroInfo)

@dataclass
class RankFilter:
    branchFilter: List[Any]
    tabFilter: List[Any]
    eventList: List[Any]

@dataclass
class GetRankListResponse:
    code: int
    msg: str
    data: Dict[str, Union[RankFilter, str, int, List[RankEntry]]]


class RankType(IntEnum):
    """Enumeration for the different types of hero rankings."""
    TIER = 1
    MATCH_PERIOD = 2
    DAMAGE_DEALT = 6
    GOLD = 7
    DAMAGE_TAKEN = 9
    ASSISTS = 10
    TOWER_DAMAGE = 11

class Position(IntEnum):
    """Enumeration for hero positions/lanes."""
    ALL = 255
    CLASH_LANE = 0
    MID_LANE = 1
    FARM_LANE = 2
    JUNGLE = 3
    ROAMING = 4
