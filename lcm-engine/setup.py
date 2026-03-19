from setuptools import setup, find_packages

setup(
    name="lcm-engine",
    version="0.1.0",
    description="Legacy Code Modernization Engine",
    author="Hackathon Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "z3-solver>=4.12.0",
        "litellm>=1.0.0",
        "chromadb>=0.4.0",
        "sentence-transformers>=2.2.0",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "pydantic>=2.0.0"
    ],
    entry_points={
        "console_scripts": [
            "lcm-engine=lcm_engine.main:app",
        ],
    },
)
