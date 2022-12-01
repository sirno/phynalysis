"""Formatter functions."""

import string


class IncrementalFormatter(string.Formatter):
    """Incremental string formatter."""

    def __init__(self, default="{{{0}}}"):
        self.default = default

    def get_value(self, key, args, kwds):
        if isinstance(key, str):
            return kwds.get(key, self.default.format(key))
        else:
            return string.Formatter.get_value(key, args, kwds)
