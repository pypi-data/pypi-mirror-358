# type: ignore
from setuptools import setup, find_packages
from pathlib import Path

# Read README.md for long_description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="cgsoftech_rn_installer",
    version="0.1",
    author="CG Softech",
    author_email="support@cgsoftech.in",
    description="Official CG Softech React Native dependency installer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://cgsoftech.in/rn-installer",
    packages=find_packages(),
    install_requires=[
        "click",
        "requests",
        "tqdm",
        "plumbum",
        "python-dotenv",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "rn-install = rn_installer.cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
    ],
    python_requires=">=3.7",
    keywords="react-native android sdk cgsoftech",
)