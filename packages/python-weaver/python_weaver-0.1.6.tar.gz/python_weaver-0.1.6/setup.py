from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="python-weaver",
    version="0.1.6",
    author="Advait Shinde",
    author_email="advaitss11@gmail.com",
    description="A framework to orchestrate long-running LLM workflows with a persistent task tracker.",
    long_description=long_description,
    long_description_content_type = "text/markdown",
    url="https://github.com/adv-11/python-weaver",
    packages=find_packages(exclude=["tests", "examples"]),
    python_requires='>=3.7',  # Python 3.7+ includes sqlite3 in stdlib
    install_requires=[
        "litellm",
        "pandas",
        "beautifulsoup4",
        "requests",
        "PyPDF2",
        "click",
        "backoff",
        "toml",
        "python-dotenv",
    ],
    extras_require={
        "dev": ["pytest"]
    },
    tests_require=["pytest"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "weaver=weaver.cli:main"
        ]
    }
)
