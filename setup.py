from setuptools import setup, find_packages

setup(
    name="aeonrift",
    version="0.1.0",
    description="AEONRIFT — Time-travel infrastructure for AI agents.",
    author="Ansh Rajore",
    author_email="anshrajore@github.com",
    url="https://github.com/anshrajore/AEONRIFT-Time-travel-infrastructure-for-AI-agents.",
    license="Apache-2.0",
    python_requires=">=3.8",
    packages=[
        "aeonrift",
        "aeonrift.core",
        "aeonrift.runtime",
        "aeonrift.cli",
        "adapters",
        "services",
        "services.checkpoint",
        "services.recovery",
        "services.state",
        "services.coordinator",
        "services.gateway",
        "storage",
        "benchmarks",
        "ml"
    ],
    package_dir={
        "aeonrift": "packages/core/aeonrift",
        "aeonrift.core": "packages/core/aeonrift/core",
        "aeonrift.runtime": "packages/runtime/aeonrift/runtime",
        "aeonrift.cli": "packages/cli/aeonrift/cli",
        "adapters": "adapters",
        "services": "services",
        "storage": "storage",
        "benchmarks": "benchmarks",
        "ml": "ml"
    },
    entry_points={
        "console_scripts": [
            "aeonrift = aeonrift.cli.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
