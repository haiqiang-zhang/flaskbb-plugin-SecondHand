"""
    SecondHand
    ~~~~~~


"""
import ast
import re
import os
from setuptools import setup, find_packages


def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


long_description = read("README.md")
version_line = re.search(
    r"__version__\s+=\s+(.*)", read("SecondHand", "__init__.py")
).group(1)
version = str(ast.literal_eval(version_line))


setup(
    name="flaskbb-plugin-SecondHand",
    version=version,
    author="Haiqiang Zhang",
    license="BSD",
    author_email="a1552094108@gmail.com",
    description="A SecondHand plugin for FlaskBB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="flaskbb plugin SecondHand",
    packages=find_packages("."),
    include_package_data=False,
    # package_data={
    #     "": ["SecondHand/translations/*/*/*.mo", "SecondHand/translations/*/*/*.po"]
    # },
    zip_safe=False,
    platforms="any",
    entry_points={"flaskbb_plugins": ["SecondHand = SecondHand"]},
    install_requires=["FlaskBB>=2.1.0"],
    # setup_requires=["Babel"],
    # classifiers=[
    #     "Development Status :: 5 - Production/Stable",
    #     "Environment :: Web Environment",
    #     "Environment :: Plugins",
    #     "Framework :: Flask",
    #     "Intended Audience :: Developers",
    #     "License :: OSI Approved :: BSD License",
    #     "Operating System :: OS Independent",
    #     "Programming Language :: Python",
    #     "Programming Language :: Python :: 3",
    #     "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    #     "Topic :: Software Development :: Libraries :: Python Modules",
    # ],
)
