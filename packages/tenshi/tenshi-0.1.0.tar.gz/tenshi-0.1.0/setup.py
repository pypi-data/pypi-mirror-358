from setuptools import setup, find_packages

setup(
    name="tenshi",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["requests"],
    author="Your Name",
    description="A Gemini AI wrapper with API key rotation and system prompt support.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/tenshi/",  # update with GitHub later if needed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
