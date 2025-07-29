from setuptools import setup, find_packages

setup(
    name="zinmage",
    version="0.1.0",
    description="Minimalist Python library for image conversion (PNG to JPG)",
    author="Tin Programmers Team",
    author_email="tinprogrammers@gmail.com",
    packages=find_packages(),
    install_requires=["Pillow"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
