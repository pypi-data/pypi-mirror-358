from setuptools import setup, find_packages

setup(
    name="layman_terminal",
    version="0.1.0b6",
    packages=find_packages(),
    install_requires=[
        "python-dotenv",
        "pyyaml",
        "google-genai"
    ],
    entry_points={
        "console_scripts": [
            "lt=layman_terminal.cli:main",
            "lt-init=layman_terminal.initialize_config:create_config"
        ]
    },
    include_package_data=True,
    python_requires=">=3.9",
    author="Prashant Gavit",
    author_email="prashantgavit115@gmail.com",
    description="AI-powered terminal assistant",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/prashantgavit/layman-terminal",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="ai terminal cli assistant",
    project_urls={
        "Bug Tracker": "https://github.com/prashantgavit/layman-terminal/issues",
    },


)