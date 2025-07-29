from setuptools import setup, find_packages


setup(
    name="kynex",
    version=" 0.1.9",
    description="A Python package to get data from different llm's",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Aegletek",
    author_email="coe@aegletek.com",
    url="https://www.aegletek.com/",
    license="MIT",
    packages=find_packages(), # auto-detects kynex
    install_requires=[
        "google-generativeai","langchain","groq"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",

    ],
    python_requires='>=3.7',
)