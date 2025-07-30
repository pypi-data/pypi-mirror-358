from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="apays",
    version="0.1.0",
    description="APays API client for Python",
    author="Bezdarnost",
    url="https://github.com/Bezdarnost01/apays",
    packages=find_packages(where="src"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    install_requires=[
        "httpx>=0.24.0",
        "pydantic>=2.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
