"""Common functions in configurations module."""

import re


def _expand_path(path: str, fmt: str = None) -> list[str]:
    paths = []
    expansion_stack = [path]

    # find the innermost list
    list_regex = re.compile(r"\[([^\[\]]*?)\]")
    while expansion_stack:
        path = expansion_stack.pop(0)

        list_match = re.search(list_regex, path)

        if list_match is None:
            paths.append(path)
            continue

        inner = list_match.group(1)

        if ":" in inner:
            inner, fmt = inner.split(":")
            fmt = f"%{fmt}"

        if ".." in inner:
            items = range(*map(int, inner.split("..")))
        else:
            items = inner.split(",")

        for item in items:
            if fmt is not None:
                item = fmt % item
            if item is not str:
                item = str(item)
            expanded_path = re.sub(list_regex, item, path, count=1)
            expansion_stack.append(expanded_path)

    # remove duplicates that may be created by nested lists
    paths = list(set(paths))

    return sorted(paths)
