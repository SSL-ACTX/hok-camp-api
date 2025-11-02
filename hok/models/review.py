# hok/models/review.py
import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from .common import PublisherInfo, UserInteraction

# --- Data Structures for Hero Reviews and UGC Content ---

@dataclass
class HotComment:
    type: int
    publisherInfo: Union[PublisherInfo, Dict]
    publishTime: datetime.datetime
    collectCount: str
    likeCount: str
    readCount: str
    commentCount: str
    heatCount: str
    shareCount: str
    language: int
    region: int
    userInteraction: Union[UserInteraction, Dict]
    icon: List[Any]
    contentId: str
    replyContentId: str
    replyReplyId: str
    authInfo: List[Any]
    content: str
    media: List[Any]
    score: int
    replyList: List[Any]
    relateId: str
    relateType: int
    customStatus: int
    replyPublisherInfo: Optional[Any] = None
    replyContent: Optional[Any] = None
    relateInfo: Optional[Any] = None

    # This field is in the JSON but missing in your original model
    mentionInfos: List[Any] = field(default_factory=list)


    def __post_init__(self):
        """Convert nested dicts to dataclass objects."""
        if isinstance(self.publisherInfo, dict):
            self.publisherInfo = PublisherInfo(**self.publisherInfo)
        if isinstance(self.userInteraction, dict):
            self.userInteraction = UserInteraction(**self.userInteraction)

@dataclass
class ReviewTagScore:
    score: float
    count: List[int]

@dataclass
class ReviewTagAttribute:
    canComment: bool
    canScore: bool
    canHeat: bool
    showScore: Optional[bool] = False


@dataclass
class ReviewTag:
    id: int
    name: str
    tag: List[Any]
    status: int
    avatar: str
    score: Union[ReviewTagScore, Dict]
    heat: int
    forward: int
    liked: int
    comments: int
    extra: str
    attribute: Union[ReviewTagAttribute, Dict]
    desc: str
    relateReviews: List[Any]
    elements: List[Any]
    handpickList: Dict[str, List[Any]]
    region: str
    createTime: datetime.datetime
    updateTime: datetime.datetime
    hotListDesc: str
    hotListSubDesc: str
    commentHead: str
    commentDefault: str

    def __post_init__(self):
        """Convert nested dicts to dataclass objects."""
        if isinstance(self.score, dict):
            self.score = ReviewTagScore(**self.score)
        if isinstance(self.attribute, dict):
            self.attribute = ReviewTagAttribute(**self.attribute)

@dataclass
class ReviewObjectElement:
    id: str
    type: int
    extra: str

@dataclass
class HandpickList:
    campHomeCommentList: List[Any]
    hokGameCommentList: List[str]

@dataclass
class ReviewObject:
    id: int
    name: str
    tag: Union[List[ReviewTag], List[Dict]]
    status: int
    avatar: str
    score: Union[ReviewTagScore, Dict]
    heat: int
    forward: int
    liked: int
    comments: int
    extra: str
    attribute: Union[ReviewTagAttribute, Dict]
    desc: str
    relateReviews: List[Any]
    elements: Union[List[ReviewObjectElement], List[Dict]]
    handpickList: Union[HandpickList, Dict]
    region: str
    createTime: datetime.datetime
    updateTime: datetime.datetime
    hotListDesc: str
    hotListSubDesc: str
    commentHead: str
    commentDefault: str

    def __post_init__(self):
        """Convert nested dicts to dataclass objects."""
        if self.tag and isinstance(self.tag[0], dict):
            self.tag = [ReviewTag(**t) for t in self.tag]
        if isinstance(self.score, dict):
            self.score = ReviewTagScore(**self.score)
        if isinstance(self.attribute, dict):
            self.attribute = ReviewTagAttribute(**self.attribute)
        if self.elements and isinstance(self.elements[0], dict):
            self.elements = [ReviewObjectElement(**elem) for elem in self.elements]
        if isinstance(self.handpickList, dict):
            self.handpickList = HandpickList(**self.handpickList)

@dataclass
class ReviewListItem:
    reviewObj: Union[ReviewObject, Dict]
    hotComment: Optional[Union[HotComment, Dict]] = None
    commentList: List[Any] = field(default_factory=list)


    def __post_init__(self):
        """Convert nested dicts to dataclass objects."""
        if isinstance(self.reviewObj, dict):
            self.reviewObj = ReviewObject(**self.reviewObj)
        if self.hotComment and isinstance(self.hotComment, dict):
            self.hotComment = HotComment(**self.hotComment)

@dataclass
class HeroReviewsData:
    reviewList: Union[List[ReviewListItem], List[Dict]]

    def __post_init__(self):
        """Convert reviewList of dicts to list of ReviewListItem objects."""
        if self.reviewList and isinstance(self.reviewList[0], dict):
            self.reviewList = [ReviewListItem(**item) for item in self.reviewList]


@dataclass
class GetHeroReviewsResponse:
    code: int
    msg: str
    data: Union[HeroReviewsData, Dict]

    def __post_init__(self):
        """Convert data dict to HeroReviewsData object."""
        if isinstance(self.data, dict):
            self.data = HeroReviewsData(**self.data)

@dataclass
class CommentListItem:
    type: int
    publisherInfo: PublisherInfo
    replyPublisherInfo: Optional[PublisherInfo]
    publishTime: datetime.datetime
    collectCount: str
    likeCount: str
    readCount: str
    commentCount: str
    heatCount: str
    shareCount: str
    language: int
    region: int
    userInteraction: UserInteraction
    icon: List[Any]
    contentId: str
    replyContentId: str
    replyReplyId: str
    authInfo: List[Any]
    content: str
    media: List[Any]
    score: int
    replyList: List[Any]
    relateId: str
    relateType: int
    replyContent: Optional[Any]
    relateInfo: Optional[Any]
    customStatus: int

@dataclass
class CommentList:
    commentList: List[CommentListItem]
    hasMore: bool
    type: int
    commentRemain: int
    reviewObj: Optional[Any]

@dataclass
class ReviewDetail(ReviewObject): # Inherits from ReviewObject
    elements: List[Any] # Override with more specific type if known
