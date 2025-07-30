from setuptools import setup, find_packages

setup(
    name="praveen_weather_sdk",
    version="1.0.0",
    author_email="praveen.theguru2020@gmail.com",
    author="Praveen Kumar Bharti",
    description="A simple Python SDK for fetching weather data",
    license="None",
    packages=find_packages(),
    install_requires=[
        "requests>=2.20"
    ],
    python_requires=">=3.6",
)
