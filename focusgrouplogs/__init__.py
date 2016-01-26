"""Focusgrouplogs flask frontend."""


import os
from collections import namedtuple
from flask import Flask
from flask.ext.cache import Cache
from werkzeug.routing import BaseConverter


__author__ = "Adam Talsma"
__author_email__ = "se-adam.talsma@ccpgames.com"
__version__ = "0.0.1"


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app = Flask(__name__)
cache = Cache(app, config={"CACHE_TYPE": "simple"})
app.url_map.converters["regex"] = RegexConverter

LOGDIR = os.environ.get("FOCUSGROUPLOGS_LOGDIR")
FOCUS_GROUPS = list(sorted([
    d for d in os.listdir(LOGDIR) if os.path.isdir(os.path.join(LOGDIR, d))
]))

# make legacy last..
if "legacy" in FOCUS_GROUPS:
    FOCUS_GROUPS.remove("legacy")
    FOCUS_GROUPS.append("legacy")

FocusGroupLog = namedtuple("FocusGroupLog", ("name", "date", "size"))
