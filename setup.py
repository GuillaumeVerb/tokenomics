from setuptools import setup, find_packages

setup(
    name="tokenomics",
    version="0.1.0",
    packages=find_packages(where="backend"),
    package_dir={"": "backend"},
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.115.7",
        "uvicorn>=0.24.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "pytest>=8.0.0",
        "pyjwt>=2.8.0",
        "python-multipart>=0.0.6",
        "httpx>=0.24.1",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
            "pylint>=2.17.0"
        ],
        "test": [
            "pytest>=8.0.0",
            "pytest-cov>=4.1.0",
            "httpx>=0.24.1",
            "pytest-asyncio>=0.21.0"
        ]
    }
) 