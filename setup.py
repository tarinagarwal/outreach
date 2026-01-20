"""
Setup configuration for Outreach Agent
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements from requirements.txt
requirements = []
requirements_path = this_directory / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="outreach-agent",
    version="1.0.0",
    description="AI-powered automated personalized email outreach system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AI Kaptan",
    author_email="support@aikaptan.com",
    url="https://github.com/aikaptan/outreach-agent",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    install_requires=requirements,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Communications :: Email",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Framework :: Flask",
    ],
    keywords="email automation, outreach, ai, openai, google sheets, google docs, smtp, flask",
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "outreach-agent=app:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/aikaptan/outreach-agent/issues",
        "Source": "https://github.com/aikaptan/outreach-agent",
        "Documentation": "https://github.com/aikaptan/outreach-agent#readme",
    },
)
