# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

"""
Helper module for YAML files.

Reads YAML files into a dictionary with a custom loader.
"""

import os
import yaml


def read_yaml(path: os.PathLike):
    """
    Read a YAML file into a dictionary.

    Loads the YAML file specified by `path`. The YAML loader is configured
    to read datetime objects as strings, for simplifying validation with a JSON schema.

    Args:
        path (path-like): Path of the YAML file.

    Returns:
        dict: A dictionary, populated from the YAML file.
    """
    _remove_implicit_resolver(yaml.SafeLoader)
    with open(path, "r", encoding="utf8") as file:
        return yaml.load(file, Loader=yaml.SafeLoader)


def _remove_implicit_resolver(cls, tag_to_remove='tag:yaml.org,2002:timestamp'):
    """
    Remove implicit resolvers for a particular tag

    Takes care not to modify resolvers in super classes.

    We want to load datetime objects as strings, not dates, because we
    go on to serialise as JSON which doesn't have the advanced types
    of YAML, and leads to incompatibilities down the track.
    """
    if 'yaml_implicit_resolvers' not in cls.__dict__:
        cls.yaml_implicit_resolvers = cls.yaml_implicit_resolvers.copy()

    for first_letter, mappings in cls.yaml_implicit_resolvers.items():
        cls.yaml_implicit_resolvers[first_letter] = [
            (tag, regexp)
            for tag, regexp in mappings
            if tag != tag_to_remove
        ]
