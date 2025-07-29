from setuptools import setup, find_packages

setup(
    name="testpysecure",
    version="0.0.1",
    author="Attacker Name",
    author_email="attacker@example.com",
    description="Malicious package for dependency confusion attack",
    packages=find_packages(),
    install_requires=['requests'],
)
