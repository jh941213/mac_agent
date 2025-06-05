#!/usr/bin/env python3
"""
Mac Agent 설치 스크립트
"""

from setuptools import setup, find_packages
from pathlib import Path

# README 파일 읽기
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# requirements.txt 읽기
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="mac-agent",
    version="1.0.0",
    description="터미널에서 자연어로 캘린더를 관리하는 AI 어시스턴트",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="kdb",
    author_email="kim.db@kt.com",
    url="https://github.com/your-username/mac-agent",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'mac_agent=app.main:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Scheduling",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    keywords="calendar, ai, assistant, macos, cli, natural-language",
) 