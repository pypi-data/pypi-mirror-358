from setuptools import setup, find_packages
from pathlib import Path

# Read the long description from README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="zinmage",
    version="0.1.4",
    description="Minimalist Python library for image conversion",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tin Programmers Team",
    author_email="tinprogrammers@gmail.com",
    url="https://github.com/tinprogrammers/zinmage",  # optional but nice
    packages=find_packages(),
    install_requires=["Pillow"],
    entry_points={
        "console_scripts": [
            "zinmage=zinmage.cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    ],
    python_requires=">=3.6",
)
