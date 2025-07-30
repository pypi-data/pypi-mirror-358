from setuptools import setup, find_packages
from pathlib import Path

setup(
    name='pyrisklib',
    version='0.1.0',
    author="YONG LI",
    author_email="13910058527@139.com",
    description="A Python library for risk management and analysis",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/piper0124/pyrisklib",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "numpy>=1.20",
        "pandas>=1.3",
        "regex>=2023.10.3",
    ],
    license_files=['LICENSE'],  # ✅ 指向 GPLv3 许可证文件
)