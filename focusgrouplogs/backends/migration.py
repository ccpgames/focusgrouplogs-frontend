"""Utilities to transition between files -> datastore."""


from __future__ import unicode_literals

from time import sleep
from datetime import datetime
from datetime import timedelta

from gcloud import datastore

from focusgrouplogs import FOCUS_GROUPS
from focusgrouplogs.backends import files
from focusgrouplogs.backends.datastore import all_content
from focusgrouplogs.backends.datastore import get_client


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


def _within(a, b, span=60):
    """Returns boolean of `a` being within `span` seconds of `b`."""

    # b/c TypeError: can't subtract offset-naive and offset-aware datetimes
    if a.tzinfo:
        a = (a + a.tzinfo.utcoffset(a)).replace(tzinfo=None)
    if b.tzinfo:
        b = (b + b.tzinfo.utcoffset(b)).replace(tzinfo=None)

    return b - timedelta(seconds=span) < a < b + timedelta(seconds=span)


def upload_to_google(entities):
    """Uploads entities to the google datastore."""

    if not entities:
        raise StopIteration

    client = get_client()

    while True:
        try:
            client.put_multi(entities)
        except Exception as error:
            yield "data: problem uploading: {}\n\n".format(error)
            for _ in range(30):
                sleep(1)
        else:
            break

    yield "data: {} records sent\n\n".format(len(entities))


def transition_to_datastore():
    """Transition from file backend to datastore backend.

    Checks if the log message has already been transitioned.
    """

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
                    if "capitals" in day["name"]:
                        focus_group_name = "capitals"
                    else:
                        focus_group_name = "tactical-destroyers"
                else:
                    ts = [day["date"].year, day["date"].month, day["date"].day]
                    ts.extend(
                        int(x) for x in
                        log["link"].split("T")[1].split("M")[0].split(":")
                    )
                    timestamp = datetime(*ts)
                    focus_group_name = focus_group

                for datastore_log in datastore_logs:
                    if datastore_log["user"] == log["user"] and \
                       datastore_log["message"] == log["message"] and \
                       _within(datastore_log["time"], timestamp):
                        break
                else:
                    todays_entities.append(get_entity(
                        focus_group_name,
                        log["user"],
                        log["message"],
                        timestamp,
                    ))

                if len(todays_entities) > 498:
                    for msg in upload_to_google(todays_entities):
                        yield msg
                    todays_entities = []

            for msg in upload_to_google(todays_entities):
                yield msg

        yield "data: finished moving {} to datastore\n\n".format(focus_group)
