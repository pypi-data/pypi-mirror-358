import json
from typing import Iterable


def json_dumps_for_ai(value, **kwargs) -> str:
    if not isinstance(value, str):
        value = json.dumps(value, ensure_ascii=False, **kwargs)

    return value


def to_markdown_json(string: str) -> str:
    string = f"```json\n{string}\n```"
    return string


def to_json_llm_input(value: dict | list, indent: int | None = 0) -> str:
    string = json_dumps_for_ai(value, indent=indent)
    string = to_markdown_json(string)
    return string


def filter_dict_by_keys(dictionary: dict, keys: Iterable) -> dict:
    dictionary = {key: dictionary[key] for key in keys if key in dictionary}
    return dictionary
