from setuptools import setup, find_packages

setup(
    name="hanifx-timelock",  # PyPI তে যে নাম থাকবে
    version="6.0.0",
    author="Hanif Sajim",
    author_email="sajim4653@gmail.com",
    description="A powerful file time-locking utility from the hanifx project.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/hanifx-540/hanifx-timelock",  # GitHub প্রোফাইল/প্রজেক্ট
    project_urls={
        "Facebook": "https://facebook.com/hanifx540",
        "GitHub": "https://github.com/hanifx-540",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries",
    ],
    keywords="hanifx timelock file-lock lock security",
    python_requires='>=3.6',
)
