from setuptools import setup, find_packages

setup(
    name="calculadora-python-2020ibsi0435-ifes",
    version="0.1.0",
    description="Uma calculadora com API FastAPI",
    author="Matthew A.",
    author_email="ecshestagioclik@gmail.com",
    packages=find_packages(),  # encontra automaticamente o pacote calculadora
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: FastAPI",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)
