from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="hanifx-timelock",
    version="6.1.1",
    description="A secure time-lock and license-check module for Python scripts",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Sajim Hanif",
    author_email="sajim4653@gmail.com",
    url="https://github.com/hanifx-540/hanifx-timelock",
    project_urls={
        "Bug Tracker": "https://github.com/hanifx-540/hanifx-timelock/issues",
        "Source Code": "https://github.com/hanifx-540/hanifx-timelock",
        "Facebook": "https://facebook.com/hanifx540"
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Typing :: Typed",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    keywords="timelock license security script protection",
    license="MIT",
)
