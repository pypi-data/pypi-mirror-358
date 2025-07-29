"""
Setup script for TimeTravelDebugger
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Travel-Debugger",
    version="1.1.0",
    author="tikisan",
    author_email="s2501082@sendai-nct.jp",
    description="実行状態記録を用いた革命的なPythonタイムトラベルデバッグライブラリ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tikipiya/Travel-Debugger",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "ephemeraldb>=1.0.0",
        "rich>=13.0.0",
        "click>=8.0.0",
        "colorama>=0.4.0",
        "tabulate>=0.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ttdbg=time_travel_debugger.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "time_travel_debugger": ["*.py"],
    },
)