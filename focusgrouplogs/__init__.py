"""Focusgrouplogs flask frontend."""


import os
from collections import namedtuple
from flask import Flask
from flask_cache import Cache
from werkzeug.routing import BaseConverter


__author__ = "Adam Talsma"
__author_email__ = "se-adam.talsma@ccpgames.com"
__version__ = "0.0.2"


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app = Flask(__name__)
app.url_map.converters["regex"] = RegexConverter

if os.environ.get("FOCUSGROUPLOGS_REDIS"):
    cache = Cache(app, config={
        "CACHE_TYPE": "redis",
        "CACHE_REDIS_URL": "redis://{}".format(
            os.environ.get("FOCUSGROUPLOGS_REDIS_URL", "redis:6379/0")
        ),
        "CACHE_DEFAULT_TIMEOUT": 3600,
        "CACHE_KEY_PREFIX": "focusgrouplogs.",
    })
else:
    cache = Cache(app, config={"CACHE_TYPE": "simple"})


FocusGroupLog = namedtuple("FocusGroupLog", ("name", "date", "size"))

FOCUS_GROUPS = os.environ.get(
    "FOCUS_GROUPS",
    "capitals tactical-destroyers"
).split()
