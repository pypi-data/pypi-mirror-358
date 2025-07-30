from setuptools import setup, find_packages


setup(
    name="kid_sdk",
    version="1.0",
    author="Zonesmart",
    author_email="e.beliakov@dev.kokoc.com",
    packages=find_packages(),
    install_requires=[
        "authlib",
        "requests",
        "pendulum",
        "django>=4",
        "psycopg2==2.9.5",
    ],
)
