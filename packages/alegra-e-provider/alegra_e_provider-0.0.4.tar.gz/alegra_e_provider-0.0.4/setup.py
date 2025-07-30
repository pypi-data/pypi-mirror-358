from setuptools import find_packages, setup

import versioneer

setup(
    name="alegra-e-provider",
    packages=find_packages(include=["alegra", "alegra.*"]),
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Alegra E-Provider, Python Wrapper for Alegra Electronic Provider API",
    author="Luis Martinez",
    install_requires=[
        "pydantic[email]==2.8.2",
        "requests==2.32.3",
        "httpx==0.27.2",
    ],
    test_suite="tests",
    python_requires=">=3.6",
)
