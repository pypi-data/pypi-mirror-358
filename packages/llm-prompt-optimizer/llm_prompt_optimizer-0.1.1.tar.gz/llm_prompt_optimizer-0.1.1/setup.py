from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="llm-prompt-optimizer",
    version="0.1.1",
    author="Sherin Joseph Roy",
    author_email="sherin.joseph2217@gmail.com",
    description="A comprehensive framework for systematic A/B testing, optimization, and performance analytics of LLM prompts across multiple providers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sherin-SEF-AI/prompt-optimizer.git",
    project_urls={
        "Bug Tracker": "https://github.com/Sherin-SEF-AI/prompt-optimizer/issues",
        "Documentation": "https://github.com/Sherin-SEF-AI/prompt-optimizer#readme",
        "Source Code": "https://github.com/Sherin-SEF-AI/prompt-optimizer.git",
        "LinkedIn": "https://www.linkedin.com/in/sherin-roy-deepmost/",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.8",
    keywords="llm prompt optimization a/b testing machine learning ai",
    license="MIT",
) 