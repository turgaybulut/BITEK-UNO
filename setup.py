from setuptools import setup, find_namespace_packages

setup(
    name="BITEK-UNO",
    version="1.0.0",
    packages=find_namespace_packages(include=["client.*", "server.*", "common.*"]),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "websockets",
        "asyncio",
    ],
)
