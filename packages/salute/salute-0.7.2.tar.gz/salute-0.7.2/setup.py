from setuptools import setup, find_packages

setup(
    name="salute",
    packages=find_packages(),
    install_requires=[
        "asyncpg>=0.30.0",
        "pydantic>=2.11.3",
        "python-decouple>=3.8",
        "sanic>=25.3.0",
    ]
)
