from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="statecall",
    version="0.2.1",
    author="Kavish Soningra",
    author_email="kavishsoningra009@gmail.com",
    description="A simple library to add memory and semantic search to AI chatbots",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Kavish2040/StateCall.git",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Communications :: Chat",
    ],
    keywords="ai chatbot memory conversation search llm openai groq claude",
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "semantic": [
            "sentence-transformers>=2.2.0",
            "numpy>=1.21.0",
        ],
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
) 