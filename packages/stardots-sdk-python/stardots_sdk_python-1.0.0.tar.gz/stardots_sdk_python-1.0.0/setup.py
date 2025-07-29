from setuptools import setup, find_packages

setup(
    name="stardots-sdk-python",
    version="1.0.0",
    description="StarDots SDK for Python 3",
    author="StarDots Team",
    author_email="support@stardots.io",
    url="https://stardots.io",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "pydantic>=1.10.0"
    ],
    python_requires=">=3.7",
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 