from setuptools import setup, find_packages

setup(
    name="youtube-collector",
    version="0.0.5",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "pandas>=1.2.0",
        "numpy>=1.19.0",
        "python-dotenv>=0.19.0",
        "pytz>=2021.1",
    ],
    author="Hoang Vu",
    author_email="hoangvu@example.com",
    description="A Python library for collecting YouTube data including channel videos, hashtag videos, keyword search, comments, and channel profiles",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/youtube-collector",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
