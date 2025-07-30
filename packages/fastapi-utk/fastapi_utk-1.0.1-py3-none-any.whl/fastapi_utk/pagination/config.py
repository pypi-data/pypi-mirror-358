from pydantic import BaseModel


class PaginationConfig(BaseModel):
    default_page: int = 1
    default_page_size: int = 10
    max_page_size: int | None = 20
    url_page_query_param_name: str = "page"
    url_page_size_query_param_name: str = "pageSize"
