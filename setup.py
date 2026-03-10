from setuptools import setup, find_packages
setup(
    name="zrb-toolkit",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "sqlalchemy>=2.0","pydantic>=2.0","click>=8.0","cachetools>=5.0","pyyaml>=6.0","python-dateutil>=2.8","flask>=2.0"
    ],
    entry_points={"console_scripts": ["zrb=zrb.cli.main:cli"]},
)
