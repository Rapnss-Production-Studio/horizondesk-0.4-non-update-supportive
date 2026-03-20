from setuptools import setup, find_packages

setup(
    name="horizondesk-sdk",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pywebview",
        "colorama",
        "python-dotenv",
        "psutil"
    ],
    entry_points={
        'console_scripts': [
            'horizondesk-sdk=horizondesk_sdk.cli:main',
        ],
    },
    author="Rapnss Team",
    description="SDK and CLI for building Horizon Desk AI Plugins",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
