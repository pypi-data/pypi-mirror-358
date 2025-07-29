from setuptools import setup

import sys

if sys.version_info < (3, 9):
    sys.exit("Error, Python < 3.9 is not supported.")

setup(
    name="fastddm",
    use_scm_version={
        "root": "/project",
        "fallback_version": "0.3.13",
    },
    setup_requires=["setuptools_scm"],
    packages=["fastddm"],
    package_dir={"fastddm": "/project/build/temp.linux-x86_64-cpython-311/src/python/fastddm"},
    package_data={"fastddm": ["_core.*", "_core_cuda.*"]},
)
