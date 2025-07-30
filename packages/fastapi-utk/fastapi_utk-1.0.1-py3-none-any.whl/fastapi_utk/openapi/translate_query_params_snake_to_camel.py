import typing as tp
from copy import deepcopy

from pydantic.alias_generators import to_camel

from .types import OpenapiSchema


def is_query_param(param: dict[str, str]) -> bool:
    return param["in"] == "query" and "name" in param


def is_path_param(param: dict[str, str]) -> bool:
    return param["in"] == "path" and "name" in param


def translate_query_params_snake_to_camel(
    openapi_schema: OpenapiSchema,
) -> OpenapiSchema:
    path: str
    methods: dict[str, dict[str, tp.Any]]

    new_openapi_schema = deepcopy(openapi_schema)
    new_openapi_schema["paths"] = {}

    for path, methods in openapi_schema["paths"].items():
        for method in methods.values():
            for param in method.get("parameters", []):
                if is_query_param(param):
                    param["name"] = to_camel(param["name"])
                elif is_path_param(param):
                    old_param_name = str(param["name"])
                    new_param_name = to_camel(old_param_name)

                    path = path.replace(
                        f"{{{old_param_name}}}", f"{{{new_param_name}}}"
                    )
                    param["name"] = new_param_name

        new_openapi_schema["paths"][path] = methods

    return new_openapi_schema
