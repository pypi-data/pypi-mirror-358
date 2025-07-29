#!/usr/bin/env python
# -*- coding: utf-8 -*-

from yaml import SafeLoader  # noqa: F401

from torchwrench.extras.yaml import (  # noqa: F401
    IgnoreTagLoader,
    SplitTagLoader,
    dump_yaml,
    load_yaml,
)
