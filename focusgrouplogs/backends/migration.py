"""Utilities to transition between files -> datastore."""


from __future__ import unicode_literals

import logging
from datetime import datetime
import googledatastore
from googledatastore.helper import add_key_path
from googledatastore.helper import add_properties

from focusgrouplogs import FOCUS_GROUPS
from focusgrouplogs.backends import files
from focusgrouplogs.backends import datastore


def add_message(channel, speaker, message, time=None):
    """Adds a message to the google datastore for the channel."""

    if time is None:
        time = datetime.now()

    payload = {"speaker": speaker, "message": message, "time": time}

    key = googledatastore.Key()
    add_key_path(key, "#{}_focusgroup".format(channel))

    try:
        req = googledatastore.CommitRequest()
        req.transaction = googledatastore.begin_transaction(req).transaction

        this_key = req.mutation.insert_auto_id.add()

        this_key.key.CopyFrom(key)
        add_properties(this_key, payload)

        googledatastore.commit(req)
        logging.info("uploaded message to google datastore")
    except googledatastore.RPCError as e:
        logging.error(req)
        logging.error("Error while doing datastore operation")
        logging.error("RPCError: %s %s", e.method, e.reason)
        logging.error(
            "HTTPError: %s %s",
            e.response.status,
            e.response.reason,
        )


def transition_to_datastore():
    """Transition from file backend to datastore backend.

    Checks if the log message has already been transitioned.
    """

    for focus_group in FOCUS_GROUPS:
        yield "data: transitioning {} to datastore\n\n".format(focus_group)
        migrated = 0
        not_migrated = 0
        in_datastore = datastore.all_content(focus_group, _add_links=False)
        for day in files.all_content(focus_group, _add_links=False):
            datastore_day = {}
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
                        not_migrated += 1
                        break
                else:
                    add_message(
                        focus_group_name,
                        log["user"],
                        log["message"],
                        timestamp,
                    )
                    migrated += 1

        yield "data: migrated {} out of {} {} records to datastore\n\n".format(
            migrated,
            migrated + not_migrated,
            focus_group,
        )
