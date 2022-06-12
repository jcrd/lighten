from pathlib import Path

from setuptools import setup


def read(name):
    return open(Path(Path(__file__).parent, name)).read()


setup(
    name="lighten",
    version="0.0.0",
    packages=["lighten", "lightend"],
    install_requires=["dbus-python", "pygobject"],
    test_suite="test",
    entry_points={
        "console_scripts": [
            "lighten = lighten.__main__:main",
            "lightend = lightend.__main__:main",
        ],
    },
    description="Intelligent monitor brightness control utility",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/jcrd/lighten",
    license="MIT",
    author="James Reed",
    author_email="james@twiddlingbits.net",
    classifiers=[
        "License :: OSI Approved :: MIT License",
    ],
)
