from setuptools import setup, find_packages

setup(
    name="tokenomics",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "gunicorn==21.2.0",
        "pandas==2.1.1",
        "plotly==5.17.0",
        "prophet==1.1.4",
        "pymongo>=4.6.1",
        "pydantic>=2.5.3",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "black>=24.1.1",
            "isort>=5.13.2",
            "flake8>=7.0.0",
        ],
    },
) 