#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module provides templates to render paralex metadata as markdown files.
"""
from pathlib import Path
import pkg_resources
import shutil
from .paths import templates_path


class CustomTemplates(object):
    def __init__(self, *files):
        self.replace = [(templates_path / f,
                         pkg_resources.resource_filename("frictionless",
                                                         f"assets/templates/{f}"),
                         pkg_resources.resource_filename("frictionless",
                                                         f"assets/templates/{f}.tmp"))
                        for f in files]

    def __enter__(self):
        for custom, prev, tmp in self.replace:
            shutil.copyfile(prev, tmp)
            shutil.copyfile(custom, prev)

    def __exit__(self, type, value, traceback):
        for custom, prev, tmp in self.replace:
            shutil.copyfile(tmp, prev)
            Path(tmp).unlink()


def to_markdown(package, output_filename, title=None):
    yaml_lines = ["warning: This file was automatically generated, do NOT EDIT"]
    if title is not None:
        yaml_lines +=  ["title: "+title]
    yaml_lines= "\n    " + "\n    ".join(yaml_lines)

    with CustomTemplates("field.md", "package.md", "resource.md"):
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("---"+yaml_lines+"\n---\n\n\n")
            f.write(package.to_markdown())
