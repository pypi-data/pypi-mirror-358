import io
import re
from setuptools import setup


with io.open("southerncross/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read(), re.M).group(1)


setup(
    name="southerncross",
    version=version,
    description="Provides common frameworks using flask, wtforms, gunicorn and sqlalchemy.",
    py_modules=[
        "southerncross.sqlalchemy.types",
        "southerncross.validators",
        "southerncross.i18n.default_dictionary",
        "southerncross.wtforms.validators",
        "southerncross.testing.utils"
    ],
    packages=["southerncross"],
    zip_safe=False,
    platforms="any",
    setup_requires=["wheel"],
    license="Unlicense",
    tests_require=[
        "authlib",
        "email_validator",
        "flask_mail",
        "flask_sqlalchemy",
        "jsonschema",
        "pymysql",
        "pyquery",
        "wtforms"
    ],
    install_requires=[
        "flask>=2.2.0",
        "sqlalchemy",
        "gunicorn",
        "requests"
    ],
    classifiers=[
        "Environment :: Web Environment",
        "License :: OSI Approved :: The Unlicense (Unlicense)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13"
    ]
)
