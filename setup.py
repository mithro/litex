#!/usr/bin/env python3

import re
import os
import sys
from setuptools import setup
from setuptools import find_packages

import versioneer


def check_submodules(basedir):
    try:
        modules = open(os.path.join(basedir, ".gitmodules")).read()
    except FileNotFoundError as e:
        return []

    submodule_errors = []
    for line in modules.splitlines():
        match = re.search("path = (.+)", line)
        if not match:
            continue

        modulepath = match.groups()[0]

        fullpath = os.path.normpath(os.path.join(basedir, modulepath))
        assert os.path.exists(fullpath)
        assert os.path.isdir(fullpath)
        if not os.path.exists(os.path.join(fullpath, ".git")):
            submodule_errors.append(fullpath)
            continue
        submodule_errors += check_submodules(fullpath)
    return submodule_errors

if sys.version_info[:3] < (3, 3):
    raise SystemExit("You need Python 3.3+")

submodule_errors = check_submodules(os.path.dirname(__file__))
if submodule_errors:
    raise SystemExit("""\
The following git submodules are not initialized:{}

Please run:
git submodule update --recursive --init
git submodule foreach git submodule update --recursive --init
""".format("\n * ".join([""]+submodule_errors)))

setup(
    name="litex",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Python tools to design FPGA cores and SoCs",
    long_description=open("README").read(),
    author="Florent Kermarrec",
    author_email="florent@enjoy-digital.fr",
    url="http://enjoy-digital.fr",
    download_url="https://github.com/enjoy-digital/litex",
    license="BSD",
    platforms=["Any"],
    keywords="HDL ASIC FPGA hardware design",
    classifiers=[
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",  # noqa
        "Environment :: Console",
        "Development Status :: Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    packages=find_packages(),
    setup_requires=['setuptools-pep8'],
    install_requires=["pyserial"],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "litex_term=litex.soc.tools.litex_term:main",
            "mkmscimg=litex.soc.tools.mkmscimg:main",
            "litex_server=litex.soc.tools.remote.litex_server:main"
        ],
    },
)
