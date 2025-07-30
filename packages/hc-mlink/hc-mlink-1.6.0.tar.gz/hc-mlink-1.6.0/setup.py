from setuptools import setup, find_packages
import codecs
import os

VERSION = '1.6.0'
DESCRIPTION = 'mLink module for Hobby Components range of mLink I2C devices'
LONG_DESCRIPTION = 'mLink module for Hobby Components range of mLink I2C devices'

# Setting up
setup(
    name="hc-mlink",
    version=VERSION,
    author="HobbyComponents (Andrew Davies)",
    author_email="<support@hobbycomponents.com.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['smbus2'],
    keywords=['mLink', 'I2C', 'sensors', 'relay', 'interface', 'serial', 'infrared', 'motor', 'wireless', 'servo'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Operating System :: Other OS",
    ]
)
