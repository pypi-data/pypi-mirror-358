from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="minecraftserverapi",
    version="2.0.2",
    author="Bautista Fabris",
    author_email="tu.email@ejemplo.com",
    description="Librería para crear y gestionar servidores Minecraft Paper, Forge y Fabric con ngrok.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/notV4FAB/minecraftserverapi", 
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "utilfab>=1.1.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        'console_scripts': [
            'minecraftserverapi=minecraftserverapi.cli:main',  
        ],
    },
)
