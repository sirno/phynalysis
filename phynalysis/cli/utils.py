"""Cli utility functions."""


def write(file, data):
    """Write file to output."""
    if isinstance(file, str):
        with open(file, "w", encoding="utf8") as file_descriptor:
            file_descriptor.write(data)
    else:
        file.write(data)
