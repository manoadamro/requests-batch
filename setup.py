from setuptools import setup

setup(
    name="requests_batch",
    version="1.0.0",
    install_requires=[
        "requests==2.31.0",
        "fire==0.2.1"
    ],
    extras_require={
        "dev": [
            "isort==4.3.21",
            "black==19.10b0",
            "autoflake==1.3.1",
            "mock==3.0.5",
            "mypy==0.750"
        ],
        "bs4": [
            "beautifulsoup4==4.8.1"
        ],
        "pillow": [
            "pillow==6.2.1"
        ]
    },
    entry_points={
        {"console-scripts": [
            "batch-request = requests_batch.cli:main"
        ]}
    }
)