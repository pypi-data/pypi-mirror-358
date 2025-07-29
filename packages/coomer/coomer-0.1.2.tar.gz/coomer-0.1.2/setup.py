from setuptools import setup, find_packages

setup(
    name="coomer",
    version="0.1.2",
    author="sero01000",
    author_email="author@example.com",
    description="Coomer/Kemono Api client",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sero01000/coomer",
    packages=find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    license="MIT",
    keywords=[
        "coomer",
        "kemono",
        "api",
        "asyncio",
    ],
    install_requires=[
        "requests>=2.0.0,<3.0.0",
        "pydantic>=2.4.1,<2.11",
    ],
    extras_require={
        "aiohttp": ["aiohttp>=3.9.0,<3.12"],
    },
    python_requires=">=3.9",
)
