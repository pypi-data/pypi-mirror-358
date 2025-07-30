from setuptools import setup, find_packages

setup(
    name="voice_transcriber_sdk",
    version="0.1.1",
    description="Python SDK for Voice Transcriber Service",
    author="RaedRdhaounia",
    author_email="raedrdhaounia@gmail.com",
    url="https://github.com/RaedRdhaounia/conversation-from-audio",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.24.1",
        "pydantic>=2.0.0",
        "typing-extensions>=4.5.0"
    ],
    
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "mypy>=1.5.0",
            "flake8>=6.1.0",
            "pre-commit>=3.3.3",
            "isort>=5.12.0",
            "httpx>=0.24.1"
        ],
        "docs": [
            "sphinx>=7.2.0",
            "sphinx-rtd-theme>=1.2.0",
            "sphinx-autodoc-typehints>=1.24.0"
        ]
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
