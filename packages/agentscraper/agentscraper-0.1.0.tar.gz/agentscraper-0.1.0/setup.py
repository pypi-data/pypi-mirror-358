from setuptools import setup, find_packages

setup(
    name="agentscraper",
    version="0.1.0",
    author="Syed Syab Ahmad, Sania Shakeel",  # Keeping both authors as requested
    author_email="syab.se@hotmail.com, ayashal551@gmail.com",
    description="Agent-based web scraping with LLM integration",  # Updated description
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/SyabAhmad/agentscraper",
    project_urls={
        "Bug Tracker": "https://github.com/SyabAhmad/agentscraper/issues",
        "Documentation": "https://github.com/SyabAhmad/agentscraper",
        "Source Code": "https://github.com/SyabAhmad/agentscraper",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "groq>=0.4.0",
        "lxml>=4.6.0",
        "python-dotenv>=0.15.0",
        "anthropic>=0.4.0",  # For Claude models
        "openai>=0.27.0",    # For OpenAI models
    ],
    extras_require={
        "selenium": ["selenium>=4.0.0", "webdriver-manager>=3.8.0"],
        "advanced": ["crewai>=0.1.0", "google-generativeai>=0.1.0"],
    },
    entry_points={
        "console_scripts": [
            "agentscraper=agentscraper.main:main",
        ],
    },
    include_package_data=True,
)