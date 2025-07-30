from setuptools import setup, find_packages

setup(
    name="nyxploit",
    version="0.0.1",
    description="Namespace reservation for Nyxploit",
    author="Sean Richardson",
    author_email="sean@nyxploit.com",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)