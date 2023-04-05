"""Common functions in configurations module."""

import re

def _expand_path(path: str) -> list[str]:
    paths = []
    expansion_stack = [path]
    list_regex = re.compile("\[(.*?)\]")
    while expansion_stack:
        path = expansion_stack.pop(0)

        list_match = re.search(list_regex, path)

        if list_match is None:
            paths.append(path)
            continue

        inner = list_match.group(1)

        if ".." in inner:
            items = range(*map(int, inner.split("..")))
        else:
            items = inner.split(",")

        for item in items:
            expanded_path = re.sub(list_regex, item, path, count=1)
            expansion_stack.append(expanded_path)

    return sorted(paths)
