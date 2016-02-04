"""Utilities to transition between files -> datastore."""


from __future__ import unicode_literals

from datetime import datetime

from gcloud import datastore

from focusgrouplogs import FOCUS_GROUPS
from focusgrouplogs.backends import files
from focusgrouplogs.backends.datastore import get_client
from focusgrouplogs.backends.datastore import all_content


def get_entity(channel, speaker, message, time=None):
    """Builds an entity for the google datastore for this message."""

    if time is None:
        time = datetime.now()

    client = get_client()
    entity = datastore.Entity(client.key("#{}_focusgroup".format(channel)))
    entity["speaker"] = speaker
    entity["message"] = message
    entity["time"] = time

    return entity


def transition_to_datastore():
    """Transition from file backend to datastore backend.

    Checks if the log message has already been transitioned.
    """

    client = get_client()

    for focus_group in FOCUS_GROUPS:
        yield "data: transitioning {} to datastore\n\n".format(focus_group)

        in_datastore = all_content(focus_group, _add_links=False)
        if focus_group == "legacy":
            for group in ("capitals", "tactical-destroyers"):
                in_datastore.extend(all_content(group, _add_links=False))

        for day in files.all_content(focus_group, _add_links=False):
            datastore_logs = []
            for ds_day in in_datastore:
                if focus_group == "legacy":
                    datastore_logs.extend(ds_day["logs"])
                elif ds_day["date"] == day["date"]:
                    datastore_logs = ds_day["logs"]
                    break

            todays_entities = []
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

                for datastore_log in datastore_logs:
                    if datastore_log["user"] == log["user"] and \
                       datastore_log["message"] == log["message"] and \
                       datastore_log["time"] == timestamp:
                        break
                else:
                    todays_entities.append(get_entity(
                        focus_group_name,
                        log["user"],
                        log["message"],
                        timestamp,
                    ))

            client.put_multi(todays_entities)
            yield "data: {} records uploaded\n\n".format(len(todays_entities))

        yield "data: finished moving {} to datastore\n\n".format(focus_group)
