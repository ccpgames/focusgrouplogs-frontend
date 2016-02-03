"""Functions to deal with reading to/from google datastore."""


from __future__ import unicode_literals

import os
from datetime import datetime
from datetime import timedelta

import googledatastore as datastore
from googledatastore.helper import from_timestamp_usec

from focusgrouplogs import FocusGroupLog
from focusgrouplogs.formatter import add_links


datastore.set_options(
    dataset=os.environ.get("PROJECT_ID", "eve-development-services"),
)


def query_datastore(query):
    """Queries Google's datastore, translates googledatastore to python.

    Args:
        query: a string literal, in GQL syntax

    Returns:
        an iterator of dicts with property name: value for each query match
    """

    req = datastore.RunQueryRequest()
    req.gql_query.allow_literal = True
    req.gql_query.query_string = query

    value_types = ["string", "integer", "boolean", "list", "blob", "blob_key",
                   "double"]
    translations = [(val, lambda x: x) for val in value_types]
    translations.insert(1, ("timestamp_microseconds", from_timestamp_usec))
    for entity in datastore.run_query(req).batch.entity_result:
        result = {}
        for prop in entity.entity.property:
            for value, translation in translations:
                prop_value = getattr(prop.value, "{}_value".format(value))
                if prop_value:
                    if getattr(prop.value, "meaning") == 18:
                        # for reasons~ if you query for only a datetime
                        # property, you will receive integer with meaning 18
                        # instead of timestamp_microseconds...
                        result[prop.name] = from_timestamp_usec(prop_value)
                    else:
                        result[prop.name] = translation(prop_value)
                    break
        yield result


def all_content(focus_group, _add_links=True):
    """Returns all messages for the focus group."""

    return [
        log_content(focus_group, day.date.strftime("%Y-%m-%d"), _add_links)
        for day in log_metadata(focus_group)
    ]


def log_content(focus_group, date, _add_links=True):
    """Returns the content in the focus group for the day."""

    _add_links = add_links if _add_links else lambda x: x
    start_day = datetime(*(int(x) for x in date.split("-")))
    end_day = start_day + timedelta(days=1)
    query = (
        "SELECT * FROM `#{channel}_focusgroup` WHERE `time` > DATETIME("
        "'{start}T00:00:00Z') AND `time` < DATETIME('{end}T00:00:00Z')"
    ).format(
        channel=focus_group,
        start=start_day.strftime("%Y-%m-%d"),
        end=end_day.strftime("%Y-%m-%d"),
    )

    results = {"date": start_day, "name": focus_group, "logs": []}
    already_linked = []
    for res in query_datastore(query):
        this_link = res["time"].strftime("%Y-%m-%dT%H:%M:%S")
        link_extended = 0
        while this_link in already_linked:
            link_extended += 1
            this_link = "{}M{}".format(this_link.split("M")[0], link_extended)

        results["logs"].append({
            "message": _add_links(res["message"]),
            "user": res["speaker"],
            "link": this_link,
            "time": res["time"],
        })

    results["logs"] = list(sorted(results["logs"], key=lambda k: k["time"]))
    return results


def log_metadata(focus_group):
    """Returns the metadata for the focus group's logs."""

    query = "SELECT `time` FROM `#{}_focusgroup`".format(focus_group)
    metadata = {}
    for res in query_datastore(query):
        time = res['time']
        result_day = datetime(year=time.year, month=time.month, day=time.day)
        if result_day in metadata:
            metadata[result_day] += 1
        else:
            metadata[result_day] = 1

    return sorted([
        FocusGroupLog(name=focus_group, date=day, size=count)
        for day, count in metadata.items()
    ], key=lambda k: k.date)
