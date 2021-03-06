# noble_logging_utils/setup.py

from distutils.core import setup

setup(
    name="noble_logging_utils",
    version="0.1",
    packages=["noble_logging_utils", ],
    #scripts=["bin/emulambda"],
    url="https://www.github.com/noblenetworkcharterschools/noble-logging-utils",
    author="Noble Network of Charter Schools",
    description="Logging utilities",
    install_requires=[
        "structlog==18.2.0",
    ]
)
