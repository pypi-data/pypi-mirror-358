# setup.py for reqlytics-python-sdk

from setuptools import setup, find_packages

setup(
    name="reqlytics",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "fastapi",
        "starlette"
    ],
    author="Reqlytics Team",
    author_email="kunletobi4@gmail.com",
    description="Real-Time API Analytics Middleware for Flask and FastAPI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/adepoju-oluwatobi/reqlytics-python-sdk",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Flask",
        "Framework :: FastAPI",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)