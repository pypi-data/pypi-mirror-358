from setuptools import setup, find_packages

setup(
    name="apaya-py-logger",
    version="1.0.8",
    author="Apaya Development Team",
    author_email="dev@apaya.com",
    description="Advanced Python logging with automatic compression, intelligent rotation, and enterprise-grade log management for Apaya's AI social media automation platform",
    long_description="Enterprise logging library for Apaya's internal use. Provides automatic log rotation, compression, and intelligent cleanup for production AI workloads.",
    long_description_content_type="text/plain",
    project_urls={
        "Apaya Platform": "https://apaya.com/",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    keywords=[
        "logging",
        "logger",
        "log rotation",
        "log compression",
        "log management",
        "enterprise logging",
        "production logging",
        "apaya",
        "social media automation",
        "ai logging",
        "gzip compression",
        "automated logging",
    ],
    python_requires=">=3.7",
    license="Proprietary",
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
            "build",
            "twine",
        ],
    },
    entry_points={
        "console_scripts": [
            # No console scripts for this library
        ],
    },
    include_package_data=True,
    zip_safe=False,
)