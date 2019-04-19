# setup - setup script for hg-convert-prcs package
# Copyright (C) 2019 Kaz Nishimura
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# SPDX-License-Identifier: MIT

"""setup script for the hg-convert-prcs package
"""

from os import getenv, path
from setuptools import setup, find_packages

def version_suffix():
    """returns the version suffix
    """
    value = "a1"
    build = getenv("BITBUCKET_BUILD_NUMBER")
    if build is not None:
        value = ".dev" + build
    return value

def long_description():
    """return the long description from the 'README.md' file
    """
    cwd = path.abspath(path.dirname(__file__))
    with open(path.join(cwd, "README.md"), encoding="UTF-8") as file:
        # To ignore lines until a level-1 ATX header is found.
        while True:
            line = file.readline()
            if line.startswith("# "):
                break
        return line + file.read()

if __name__ == "__main__":
    setup(
        name="hg-convert-prcs",
        version="1.0" + version_suffix(),
        description="PRCS source for the Mercurial convert extension.",
        url="https://vx68k.bitbucket.io/hg-convert-prcs/",
        author="Kaz Nishimura",
        author_email="kazssym@vx68k.org",
        long_description=long_description(),
        long_description_content_type="text/markdown",
        classifiers=[
            "License :: OSI Approved :: GNU General Public License v3.0 or later",
            "Programming Language :: Python :: 3",
        ],
        requires=["prcslib"],
        python_requires=">= 3",

        packages=find_packages(exclude=["testsuite", "testsuite.*"]),
#        test_suite="testsuite",
    )
