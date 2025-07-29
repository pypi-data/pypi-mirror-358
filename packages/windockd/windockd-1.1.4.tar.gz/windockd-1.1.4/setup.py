from setuptools import setup, find_packages

setup(
    name="windockd",
    version="1.1.4",
    packages=find_packages(),
    package_data={
        "windockd": ["resources/*.zip", "resources/*.py", "resources/*.exe"],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "windockd=windockd.cli:cli"
        ]
    },
    install_requires=[
        "click>=8.0.0",
    ],
    author="Your Name",
    description="Lightweight Windows Container Runtime CLI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/RohanRusta21/windockd",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
)