"""Common functions in configurations module."""

import re

def _expand_path(path: str) -> list[str]:
    paths = []
    expansion_stack = [path]
    range_regex = re.compile(r"\[(?P<start>\d+)-(?P<end>\d+)\]")
    list_regex = re.compile("\[(.*?)\]")
    while expansion_stack:
        path = expansion_stack.pop(0)

        range_match = re.search(range_regex, path)

        if range_match:
            for item in range(
                int(range_match.group("start")),
                int(range_match.group("end")) + 1,
            ):
                expanded_path = re.sub(range_regex, str(item), path, count=1)
                expansion_stack.append(expanded_path)
            continue

        list_match = re.search(list_regex, path)

        if list_match:
            for item in list_match.group(1).split(","):
                expanded_path = re.sub(list_regex, item, path, count=1)
                expansion_stack.append(expanded_path)
            continue

        paths.append(path)

    return sorted(paths)
