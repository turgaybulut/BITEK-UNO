from setuptools import setup, find_packages

setup(
    name="BITEK_UNO",
    version="1.0.0",
    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=["scripts*"]),
    python_requires=">=3.10",
    install_requires=[
        "websockets",
        "asyncio",
    ],
    scripts=[
        "scripts/run_client.py",
        "scripts/run_server.py",
    ],
)
