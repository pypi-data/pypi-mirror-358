from pydantic import HttpUrl, BaseModel
from pydantic.alias_generators import to_camel

__all__ = [
    "PaginationInfo",
    "Paginated",
]


class PaginationInfo(BaseModel):
    page: int
    page_size: int
    total_pages: int | None = None
    total: int | None = None
    next_page: HttpUrl | None = None
    prev_page: HttpUrl | None = None

    class Config:
        from_attributes = True
        populate_by_name = True
        use_enum_values = True
        alias_generator = to_camel


class Paginated[T: BaseModel](BaseModel):
    data: list[T]
    pagination: PaginationInfo

    class Config:
        from_attributes = True
        populate_by_name = True
        use_enum_values = True
        alias_generator = to_camel
