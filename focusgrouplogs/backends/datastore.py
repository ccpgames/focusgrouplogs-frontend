"""Functions to deal with reading to/from google datastore."""


from __future__ import unicode_literals

from datetime import datetime
from datetime import timedelta

from gcloud import datastore

from focusgrouplogs import FocusGroupLog
from focusgrouplogs.formatter import add_links


class FocusgroupLogClient(object):
    @staticmethod
    def get_client():
        if not hasattr(FocusgroupLogClient, "_client"):
            FocusgroupLogClient._client = datastore.Client()
        return FocusgroupLogClient._client


def get_client():
    """Returns the same gcloud.datastore.Client every time."""

    return FocusgroupLogClient.get_client()


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

    kind = "#{}_focusgroup".format(focus_group)
    query = [("time", ">=", start_day), ("time", "<", end_day)]

    results = {"date": start_day, "name": focus_group, "logs": []}
    already_linked = []

    client = get_client()

    for res in client.query(kind=kind, filters=query).fetch():
        this_link = res["time"].strftime("%Y-%m-%dT%H:%M:%S")
        link_extended = 0
        while this_link in already_linked:
            link_extended += 1
            this_link = "{}M{}".format(this_link.split("M")[0], link_extended)
        already_linked.append(this_link)

        results["logs"].append({
            "message": _add_links(res["message"]),
            "user": res["speaker"],
            "link": this_link,
            "time": res["time"],
        })

    results["logs"] = list(reversed(sorted(results["logs"],
                                           key=lambda k: k["time"])))
    return results


def log_metadata(focus_group):
    """Returns the metadata for the focus group's logs."""

    kind = "#{}_focusgroup".format(focus_group)
    epoch = datetime.utcfromtimestamp(0)
    metadata = {}
    client = get_client()
    for res in client.query(kind=kind, projection=("time",)).fetch():
        time = epoch + timedelta(microseconds=res['time'])
        result_day = datetime(year=time.year, month=time.month, day=time.day)
        if result_day in metadata:
            metadata[result_day] += 1
        else:
            metadata[result_day] = 1

    return list(reversed(sorted([
        FocusGroupLog(name=focus_group, date=day, size=count)
        for day, count in metadata.items()
    ], key=lambda k: k.date)))
