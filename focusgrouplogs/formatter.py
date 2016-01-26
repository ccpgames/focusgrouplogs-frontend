"""Formatting/parsing of focusgrouplogs log messages."""


import os
import io
import re
from flask import abort
from datetime import datetime

from focusgrouplogs import LOGDIR
from focusgrouplogs import FocusGroupLog


timestamp_pattern = re.compile("^[0-9]{4}-[0-9]{2}-[0-9]{2}.")
url_pattern = re.compile(
    "((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)"
)


def log_name_and_date(focus_group, log):
    """Returns a tuple of (name, datetime object) for the log file."""

    match = re.match(timestamp_pattern, log)
    if match and focus_group != 'legacy':
        name = log[match.end():]
        date = datetime(*[int(i) for i in match.group()[:-1].split("-")])
    else:
        name = log
        date = datetime.utcfromtimestamp(
            os.stat(os.path.join(LOGDIR, focus_group, log)).st_mtime
        )

    return name, date


def log_metadata(focus_group):
    """Return metadata for all the log entries in the group."""

    # use file timestamp, fallback to mtime
    all_logs = []
    for log in os.listdir(os.path.join(LOGDIR, focus_group)):
        name, date = log_name_and_date(focus_group, log)
        size = size_string(focus_group, log)
        all_logs.append(FocusGroupLog(name, date, size))

    return list(reversed(sorted(all_logs, key=lambda k: k.date)))


def size_string(focus_group, logfile):
    """Returns the file size as a human readable string."""

    filename = os.path.join(LOGDIR, focus_group, logfile)
    size_int = os.path.getsize(filename)
    size_strings = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]

    def shrink(size):
        if size_int > 1024:
            return True, int(size_int / 1024.)
        else:
            return False, size_int

    size_string = 1
    while size_string < len(size_strings):
        shrunk, size_int = shrink(size_int)
        if shrunk:
            size_string += 1
        else:
            break

    return "{}{}".format(size_int, size_strings[size_string - 1])


def all_content(focus_group):
    """Builds a list for all log contents in a focus_group."""

    all_contents = []
    for log in os.listdir(os.path.join(LOGDIR, focus_group)):
        all_contents.append(log_content(focus_group, log))
    return sorted(all_contents, key=lambda k: k["date"])


def log_content(focus_group, log, adjusted=False):
    """Reads the log file and returns it in a dict with name, date and logs."""

    log_name = os.path.join(LOGDIR, focus_group, log)
    if not os.path.isfile(log_name):
        log = "{}.{}.txt".format(log, focus_group)
        log_name = os.path.join(LOGDIR, focus_group, log)
        if not os.path.isfile(log_name):
            abort(404)

    name, date = log_name_and_date(focus_group, log)
    log_meta = {
        "name": name,
        "date": date,
        "logs": [],
    }
    with io.open(log_name, "r", encoding="utf-8") as openlog:
        log_content = openlog.read().splitlines()

    already_linked = []

    for line in log_content:
        sline = line.split()
        this_link = "{}T{}".format(sline[0][1:], sline[1][:-1])
        link_extended = 0
        while this_link in already_linked:
            link_extended += 1
            this_link = "{}M{}".format(this_link.split("M")[0], link_extended)

        if focus_group == "legacy":
            timestamp = this_link.replace("T", " ")
        else:
            timestamp = sline[1][:-4]

        log_meta["logs"].append({
            "link": this_link,
            "time": timestamp,
            "message": add_links(" ".join(sline[3:])),
            "user": sline[2][1:-1],
        })
        already_linked.append(this_link)

    return log_meta


def add_links(log_message):
    """Adds <a> tags to links."""

    message = []
    last_match = 0
    for match in re.finditer(url_pattern, log_message):
        span = match.span()
        message.append(log_message[last_match:span[0]])
        link = log_message[span[0]:span[1]]
        message.append('<a href="{}">{}</a>'.format(link, link))
        last_match = span[1]

    message.append(log_message[last_match:])
    return "".join(message)
