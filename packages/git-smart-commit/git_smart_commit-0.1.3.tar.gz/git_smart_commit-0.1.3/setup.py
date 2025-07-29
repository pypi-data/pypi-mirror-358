from setuptools import setup

setup(
    name="git-smart-commit",
    version="0.1.3",
    py_modules=["app"],
    entry_points={
        "console_scripts": [
            "git-smart-commit=app:main"
        ]
    },
    description="Generate concise Git commit messages using local LLMs via Ollama",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Saranya K",
    author_email="your@email.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.7",
)
