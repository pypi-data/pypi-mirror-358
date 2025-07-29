from setuptools import setup

import sys

if sys.version_info < (3, 9):
    sys.exit("Error, Python < 3.9 is not supported.")

setup(
    name="fastddm",
    use_scm_version={
        "root": "/Users/runner/work/fastddm/fastddm",
        "fallback_version": "0.3.14",
    },
    setup_requires=["setuptools_scm"],
    packages=["fastddm"],
    package_dir={"fastddm": "/Users/runner/work/fastddm/fastddm/build/temp.macosx-10.9-x86_64-cpython-310/src/python/fastddm"},
    package_data={"fastddm": ["_core.*", "_core_cuda.*"]},
)
