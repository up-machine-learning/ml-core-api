import pydantic as _pydantic


# class MediaBaseDto(_pydantic.BaseModel):

class MediaDto(_pydantic.BaseModel):
    id: int
    entityType: str
    entityId: int
    filename: str

    class Config:
        from_attributes = True
        from_orm = True


class MediaShortDto(_pydantic.BaseModel):
    filename: str

    class Config:
        from_attributes = True
        from_orm = True
