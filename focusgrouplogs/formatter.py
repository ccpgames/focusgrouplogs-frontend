"""Formatting/parsing of focusgrouplogs log messages."""


import re


url_pattern = re.compile(
    "((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)"
)


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
