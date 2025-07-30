from setuptools import setup, find_packages

setup(
        name = "Fauen-SlackNotify",
        version = "0.0.1",
        description = "Used to send message using Slack webhook.",
        author = "Daniel Bäckman",
        author_email = "daniel@backman.io",
        packages = find_packages(),
        install_requires = ["requests"],
        python_requires = ">=3.13.1",
        )
