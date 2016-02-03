"""Utilities to transition between files -> datastore."""


from __future__ import unicode_literals

import logging
from datetime import datetime

from focusgrouplogs import FOCUS_GROUPS
from focusgrouplogs.backends import files
from focusgrouplogs.backends.datastore import get_client


def get_entity(channel, speaker, message, time=None):
    """Builds an entity for the google datastore for this message."""

    if time is None:
        time = datetime.now()

    client = get_client()
    entity = datastore.Entity(client.key("#{}_focusgroup".format(channel)))
    entity["speaker"] = speaker
    entity["messsage"] = messsage
    entity["time"] = time

    return entity


def transition_to_datastore():
    """Transition from file backend to datastore backend.

    Checks if the log message has already been transitioned.
    """

    client = get_client()

    for focus_group in FOCUS_GROUPS:
        yield "data: transitioning {} to datastore\n\n".format(focus_group)
        in_datastore = datastore.all_content(focus_group, _add_links=False)
        for day in files.all_content(focus_group, _add_links=False):
            datastore_day = {}
            ents = []  # today's entities
            for ds_day in in_datastore:
                if ds_day["date"] == day["date"]:
                    datastore_day = ds_day
                    break

            for log in day["logs"]:
                if focus_group == "legacy":
                    timestamp = datetime.strptime(
                        log["time"].split("M")[0],
                        "%Y-%m-%d %H:%M:%S",
                    )
                    if "capitals" in log["name"]:
                        focus_group_name = "capitals"
                    else:
                        focus_group_name = "tactical-destroyers"
                else:
                    ts = [day["date"].year, day["date"].month, day["date"].day]
                    ts.extend(int(x) for x in log["time"].split(":"))
                    timestamp = datetime(*ts)
                    focus_group_name = focus_group

                for datastore_log in datastore_day.get("logs", []):
                    if datastore_log["user"] == log["user"] and \
                       datastore_log["message"] == log["message"] and \
                       datastore_log["time"] == timestamp:
                        break
                else:
                    ents.append(get_entity(
                        focus_group_name,
                        log["user"],
                        log["message"],
                        timestamp,
                    ))

            client.put_multi(ents)
            yield "data: sent {} records to datastore\n\n".format(len(ents))

        yield "data: finished moving {} to datastore\n\n".format(focus_group)
