"""focusgrouplogs frontend."""


import io
import os
import re
from setuptools import setup
from setuptools import find_packages


def find_version(filename):
    """Uses re to pull out the assigned value to __version__ in filename."""

    with io.open(filename, "r", encoding="utf-8") as version_file:
        version_match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]',
                                  version_file.read(), re.M)
    if version_match:
        return version_match.group(1)
    return "0.0-version-unknown"


if os.path.isfile("README.md"):
    with io.open("README.md", encoding="utf-8") as opendescr:
        long_description = opendescr.read()
else:
    long_description = __doc__


setup(
    name="focusgrouplogs",
    version=find_version("focusgrouplogs/__init__.py"),
    description="A flask frontend to the focus group logs.",
    author="Adam Talsma",
    author_email="se-adam.talsma@ccpgames.com",
    url="https://github.com/ccpgames/focusgrouplogs/",
    download_url="https://github.com/ccpgames/focusgrouplogs/",
    entry_points={"paste.app_factory": ["main = focusgrouplogs.web:paste"]},
    install_requires=["Flask>=0.10.0", "flask-cache", "gcloud != 0.10.0"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
    ],
    extras_require={"deploy": ["paste", "PasteDeploy", "uwsgi"]},
    include_package_data=True,
    zip_safe=False,
    package_data={
        "focusgrouplogs": [
            os.path.join("focusgrouplogs", "templates", f) for f in
            os.listdir(os.path.join("focusgrouplogs", "templates"))
        ],
    },
    packages=find_packages(),
    long_description=long_description,
)
