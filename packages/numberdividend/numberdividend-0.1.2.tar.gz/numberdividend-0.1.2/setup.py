from setuptools import setup, find_packages

setup(
    name="numberdividend",
    version="0.1.2",
    packages=find_packages(),
    author="Sabolch",
    author_email="sabolch.dev@gmail.com",
    description="A tool for dividend distribution analysis.",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Natural Language :: English",
    ],
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/SaboIch/NumberDividend",
    python_requires=">=3.6",
    keywords="dividend distribution analysis",
    install_requires=[
        "pandas>=1.0.0",
        "matplotlib>=3.0.0",
        "numpy>=1.0.0",
        "argparse>=1.4.0",
        "typing>=3.6.0",
    ],
    entry_points={
        "console_scripts": [
            "numberdividend=numberdividend.__main__:main",
        ],
    },
)
