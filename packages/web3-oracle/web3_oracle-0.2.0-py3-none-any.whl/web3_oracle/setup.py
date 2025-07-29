from setuptools import setup, find_packages

setup(
    name="web3_oracle",
    version="0.1.0",
    packages=find_packages(),
    package_data={
        "web3_oracle": ["data/*.csv"],
    },
    install_requires=[
        "pandas",
        "pytz",
    ],
    author='Gmatrixuniverse',
    author_email='gmatrixuniverse@gmail.com',
    description="A package to retrieve token prices by timestamp",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/gmatrixuniverse/web3_oracle",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
) 