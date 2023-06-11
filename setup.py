from setuptools import setup, find_packages

from utils.misc import build_req

packages = find_packages(".")

setup(
    name="discordSS",
    version="0.1.0",
    description="discordSS is a discord.py superset",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ZackaryW/discordSS",
    author="ZackaryW",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
    ],
    keywords="discord discord.py",
    packages=packages,
    install_requires=["discord"],
    python_requires=">=3.8",
    extras_require=build_req(),
)


