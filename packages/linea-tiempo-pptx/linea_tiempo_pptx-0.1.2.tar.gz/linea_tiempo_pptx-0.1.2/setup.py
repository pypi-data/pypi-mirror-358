from setuptools import setup, find_packages

setup(
    name="linea_tiempo_pptx",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "python-pptx",
        "openpyxl"
    ],
    entry_points={
        "console_scripts": [
            "linea-tiempo=linea_tiempo.generador:generar_presentacion"
        ]
    },
    author="Jhony Zavala",
    description="Generador de líneas de tiempo en PowerPoint desde Excel",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jhonyzavala/linea_tiempo",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.7',
)
