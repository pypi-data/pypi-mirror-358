from setuptools import setup, find_packages

setup(
    name="httpqc",
    version="0.0.1",
    description="HTTP/3 client library using QUIC protocol",
    author="Lucas Guerrero",
    author_email="nlucas.guerrero@gmail.com",
    packages=find_packages(),
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
