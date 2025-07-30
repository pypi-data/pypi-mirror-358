from pydantic import BaseModel


class SortingConfig(BaseModel):
    url_query_param_name: str = "sort"
    delimiter: str = ","
