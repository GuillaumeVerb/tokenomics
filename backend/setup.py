from setuptools import find_packages, setup

setup(
    name="tokenomics",
    version="0.1.0",
    packages=find_packages(include=["app", "app.*", "tests", "tests.*"]),
    include_package_data=True,
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn>=0.27.0",
        "gunicorn>=21.2.0",
        "pandas>=2.1.1",
        "plotly>=5.17.0",
        "pymongo>=4.6.1",
        "pydantic>=2.5.3",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "test": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.25.0",
            "httpx>=0.24.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.10.0",
        ],
        "dev": [
            "black>=24.1.1",
            "isort>=5.13.2",
            "flake8>=7.0.0",
        ],
    },
    python_requires=">=3.9",
) 