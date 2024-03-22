import decimal
from datetime import date
from decimal import Decimal
from typing import Optional, List

import pydantic as _pydantic


class CreateSuggestionDto(_pydantic.BaseModel):
    fromDestination: str
    toDestination: str
    fromDate: date
    toDate: date
    latitude: Decimal
    longitude: Decimal
    preferences:  Optional[List[str]]

    class Config:
        from_attributes = True
        from_orm = True
        arbitrary_types_allowed = True


class ReviewDto(_pydantic.BaseModel):
    reviewId: int
    headImage: str
    username: str
    createTime: int
    comment: str
    userRating: Decimal
    predictedSentiment: Optional[Decimal]

    class Config:
        from_attributes = True
        from_orm = True
        arbitrary_types_allowed = True


class DestinationDto(_pydantic.BaseModel):
    id: int
    code: int
    name: str
    price: Decimal
    type: str
    districtName: str
    rating: Decimal
    reviewCount: int
    gglat: Decimal
    gglon: Decimal
    imageUrl: str
    url: Optional[str]
    tags: Optional[List[str]]
    reviews: Optional[List[ReviewDto]]

    class Config:
        from_attributes = True
        from_orm = True
        arbitrary_types_allowed = True


class DestinationResultDto(DestinationDto):
    avgSentiment: Decimal
    predictedSentiment: Decimal
    distance: Decimal

    class Config:
        from_attributes = True
        from_orm = True
        arbitrary_types_allowed = True


class DestinationPageDto(_pydantic.BaseModel):
    data: List[DestinationDto]
    totalRecord: int


class CreateResponseDto(_pydantic.BaseModel):
    optionOne: List[DestinationResultDto]
    optionTwo: List[DestinationResultDto]
    optionThree: List[DestinationResultDto]

    class Config:
        from_attributes = True
        from_orm = True
        arbitrary_types_allowed = True
