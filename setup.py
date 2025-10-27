from setuptools import setup, find_packages

setup(
    name="emulator_adapter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "vgamepad",
    ],
    python_requires=">=3.7",
    description="Universal adapter for connecting to various game emulators",
    author="Your Name",
)

