# type: ignore
from setuptools import setup, find_packages
from pathlib import Path
# Read README.md for long_description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")
setup(
    name="rn_installer",
    version="0.1",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",    
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
)