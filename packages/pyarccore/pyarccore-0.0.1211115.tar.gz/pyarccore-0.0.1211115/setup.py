from setuptools import setup, find_packages

setup(
    name="pyarccore",
    version="0.0.1211115",
    author="INICODE",
    author_email="contact.inicode@gmail.com",
    description="Paquetage Python pour gérer les configurations, l'internationalisation et les routes dans les applications FastAPI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/inicode_celestin03/pyarccore",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "python-multipart>=0.0.5",
        "uvicorn>=0.15.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)