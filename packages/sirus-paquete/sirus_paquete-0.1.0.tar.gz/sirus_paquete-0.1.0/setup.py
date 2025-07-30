from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
	long_description = fh.read()

setup(
	name="sirus_paquete",
	version="0.1.0",
	packages=find_packages(),
	install_requires=[],
	author="SIrus",
	description="Consultar cursos de la academia Hack4u de S4vitar",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://hack4u.io"

)
