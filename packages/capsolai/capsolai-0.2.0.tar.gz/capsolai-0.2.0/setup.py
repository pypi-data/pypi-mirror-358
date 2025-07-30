from setuptools import setup, find_packages

setup(
    name="capsolai", 
    version="0.2.0",
    author="trailios",
    author_email="admin@bombing.lol",
    description="Python API wrapper for the Captcha Solver AI service",
    url="https://github.com/trailios/csai",
    license="Apache License 2.0",
    packages=find_packages(include=["capsolai", "capsolai.*"]),
    install_requires=[
        "requests>=2.25",
        "typing-extensions>=4.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
)
